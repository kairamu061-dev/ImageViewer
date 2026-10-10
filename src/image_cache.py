from __future__ import annotations
import logging
import os
import threading
from collections import OrderedDict
from pathlib import Path
from PyQt6.QtGui import QPixmap, QImage, QImageReader
from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject, QSize, Qt

logger = logging.getLogger(__name__)

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".tif"}
PRELOAD_RADIUS = 3
# Full-resolution QPixmaps are uncompressed in memory; without a cap, browsing
# a large folder end to end accumulates them without limit. Capping this is a
# reasonable improvement regardless, but it did NOT fix the "no image" bug
# reported in large folders -- see _load_qimage's logging for the real cause.
CACHE_LIMIT = 60
# Requesting setScaledSize() at the *native* size turned out to be a no-op
# (no real libjpeg DCT scaling happens, so it fails identically to a plain
# read()). These fractions force genuine scaling, least lossy first.
_FALLBACK_SCALES = (7 / 8, 1 / 2, 1 / 4)
# Guaranteed last resort: the exact size grid_view's thumbnail decode uses,
# which has never failed on any file so far (at the cost of resolution).
_LAST_RESORT_MAX_SIDE = 384


def _load_qimage(path: Path) -> QImage | None:
    """Load image into QImage on any thread (QImageReader is thread-safe per instance)."""
    try:
        reader = QImageReader(str(path))
        reader.setAutoTransform(True)   # Honour EXIF orientation
        native_size = reader.size()   # read header before pixel data
        img = reader.read()
        if not img.isNull():
            return img

        # Log dimensions + byte size on failure: lets us tell an actually
        # corrupt file apart from a merely huge one (full-res alloc failure
        # also surfaces as "Unable to read image data") or a plugin quirk.
        try:
            file_bytes = os.path.getsize(path)
        except OSError:
            file_bytes = -1
        logger.warning("decode failed: %s (%s) native=%dx%d bytes=%d",
                        path, reader.errorString(),
                        native_size.width(), native_size.height(), file_bytes)

        for fraction in _FALLBACK_SCALES:
            reader = QImageReader(str(path))
            reader.setAutoTransform(True)
            if native_size.isValid():
                reader.setScaledSize(QSize(
                    max(1, int(native_size.width() * fraction)),
                    max(1, int(native_size.height() * fraction)),
                ))
            img = reader.read()
            if not img.isNull():
                logger.info("scaled-fallback decode succeeded at %.0f%%: %s",
                            fraction * 100, path)
                return img
            logger.warning("scaled-fallback (%.0f%%) decode also failed: %s (%s)",
                            fraction * 100, path, reader.errorString())

        reader = QImageReader(str(path))
        reader.setAutoTransform(True)
        if native_size.isValid() and (native_size.width() > _LAST_RESORT_MAX_SIDE
                                       or native_size.height() > _LAST_RESORT_MAX_SIDE):
            reader.setScaledSize(
                native_size.scaled(_LAST_RESORT_MAX_SIDE, _LAST_RESORT_MAX_SIDE,
                                    Qt.AspectRatioMode.KeepAspectRatio)
            )
        img = reader.read()
        if img.isNull():
            logger.warning("last-resort decode also failed: %s (%s)",
                            path, reader.errorString())
            return None
        logger.info("last-resort decode succeeded (reduced quality): %s", path)
        return img
    except Exception:
        logger.exception("exception while decoding: %s", path)
        return None


class _LoadSignals(QObject):
    # Carries QImage (not QPixmap) so conversion to QPixmap happens on the main thread
    done = pyqtSignal(int, int, object)   # generation, index, QImage | None


class _LoadWorker(QRunnable):
    def __init__(self, generation: int, index: int, path: Path, signals: _LoadSignals):
        super().__init__()
        self.generation = generation
        self.index = index
        self.path = path
        self.signals = signals
        self.setAutoDelete(True)

    def run(self):
        qimage = _load_qimage(self.path)
        self.signals.done.emit(self.generation, self.index, qimage)


class ImageCache:
    def __init__(self):
        self._cache: OrderedDict[int, QPixmap] = OrderedDict()
        self._loading: set[int] = set()
        self._lock = threading.Lock()
        self._images: list[Path] = []
        self._folder: Path | None = None
        self._generation = 0
        # Dedicated pool (not globalInstance()) so a folder's preloads don't
        # contend with the grid/folder-tree pools. Capped low to keep random
        # reads off a spinning disk modest; full serialization was tried while
        # chasing the "no image" bug but that turned out to be a decode issue
        # (see _load_qimage), not drive contention, so 2 is enough.
        self._pool = QThreadPool()
        self._pool.setMaxThreadCount(2)
        self._signals = _LoadSignals()
        self._signals.done.connect(self._on_loaded)

    def set_folder(self, folder: Path, images: list[Path]):
        with self._lock:
            self._generation += 1
            self._cache.clear()
            self._loading.clear()
            self._images = images
            self._folder = folder

    def get(self, index: int) -> QPixmap | None:
        with self._lock:
            if index not in self._cache:
                return None
            self._cache.move_to_end(index)
            return self._cache[index]

    def get_sync(self, index: int) -> QPixmap | None:
        """Load synchronously on the calling (main) thread."""
        with self._lock:
            if index in self._cache:
                self._cache.move_to_end(index)
                return self._cache[index]
            if not self._images or index < 0 or index >= len(self._images):
                return None
            path = self._images[index]

        # _load_qimage already tries a plain read and a scaled-decode
        # fallback internally; a blind outer retry here proved useless since
        # the observed failures are deterministic (same file, same result
        # every time), not a one-off glitch.
        qimage = _load_qimage(path)
        px = QPixmap.fromImage(qimage) if qimage is not None else None

        with self._lock:
            if px is not None:
                self._store(index, px)
        return px

    def _store(self, index: int, pixmap: QPixmap):
        """Insert/refresh a cache entry and evict the least-recently-used ones over the cap."""
        self._cache[index] = pixmap
        self._cache.move_to_end(index)
        while len(self._cache) > CACHE_LIMIT:
            self._cache.popitem(last=False)

    def preload(self, center: int):
        total = len(self._images)
        if total == 0:
            return
        indices = []
        for offset in range(PRELOAD_RADIUS + 1):
            for i in [center + offset, center - offset]:
                if 0 <= i < total:
                    indices.append(i)
        with self._lock:
            gen = self._generation
            to_load = [i for i in dict.fromkeys(indices)
                       if i not in self._cache and i not in self._loading]
            self._loading.update(to_load)
            paths = [(i, self._images[i]) for i in to_load]

        for idx, path in paths:
            worker = _LoadWorker(gen, idx, path, self._signals)
            self._pool.start(worker)

    def _on_loaded(self, generation: int, index: int, qimage):
        """Called on the main thread via queued signal — safe to create QPixmap here."""
        with self._lock:
            if generation != self._generation:
                return
            self._loading.discard(index)
            if qimage is not None:
                self._store(index, QPixmap.fromImage(qimage))

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._loading.clear()
            self._images = []
