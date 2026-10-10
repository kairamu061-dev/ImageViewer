from __future__ import annotations
import logging
import threading
from collections import OrderedDict
from pathlib import Path
from PyQt6.QtGui import QPixmap, QImage, QImageReader
from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject

logger = logging.getLogger(__name__)

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".tif"}
PRELOAD_RADIUS = 3
# Full-resolution QPixmaps are uncompressed in memory; without a cap, browsing
# a large folder end to end accumulates them without limit. Capping this is a
# reasonable improvement regardless, but it did NOT fix the "no image" bug
# reported in large folders -- see _load_qimage's logging for the real cause.
CACHE_LIMIT = 60


def _load_qimage(path: Path) -> QImage | None:
    """Load image into QImage on any thread (QImageReader is thread-safe per instance)."""
    try:
        reader = QImageReader(str(path))
        reader.setAutoTransform(True)   # Honour EXIF orientation
        img = reader.read()
        if not img.isNull():
            return img
        logger.warning("decode failed: %s (%s)", path, reader.errorString())

        # Fallback: a plain full-resolution read() can deterministically fail
        # for a file that the thumbnail grid's scaled decode (setScaledSize)
        # always succeeds on. Requesting the native size via setScaledSize
        # routes through that same, more tolerant decode path while keeping
        # full resolution (no actual downscaling happens).
        reader = QImageReader(str(path))
        reader.setAutoTransform(True)
        native_size = reader.size()
        if native_size.isValid():
            reader.setScaledSize(native_size)
        img = reader.read()
        if img.isNull():
            logger.warning("scaled-fallback decode also failed: %s (%s)",
                            path, reader.errorString())
            return None
        logger.info("scaled-fallback decode succeeded: %s", path)
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
        # Dedicated, fully-serialized pool: the logged failures showed several
        # preload workers hammering the same drive (confirmed internal HDD)
        # with concurrent random-access reads for a second or more at a time.
        # A spinning disk has none of an SSD's tolerance for concurrent seeks,
        # so preload reads are serialized to one at a time to avoid that.
        self._pool = QThreadPool()
        self._pool.setMaxThreadCount(1)
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
