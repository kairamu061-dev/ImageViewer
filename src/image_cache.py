from __future__ import annotations
import threading
from pathlib import Path
from PyQt6.QtGui import QPixmap, QImage
from PyQt6.QtCore import QRunnable, QThreadPool, pyqtSignal, QObject
from PIL import Image, UnidentifiedImageError

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".gif", ".webp", ".tiff", ".tif"}
PRELOAD_RADIUS = 3


def _load_pixmap(path: Path) -> QPixmap | None:
    try:
        img = Image.open(path)
        img.load()
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if img.mode == "P" and "transparency" in img.info else "RGB")
        channels = 4 if img.mode == "RGBA" else 3
        data = img.tobytes("raw", img.mode)
        fmt = QImage.Format.Format_RGBA8888 if img.mode == "RGBA" else QImage.Format.Format_RGB888
        qimg = QImage(data, img.width, img.height, img.width * channels, fmt)
        return QPixmap.fromImage(qimg)
    except (UnidentifiedImageError, Exception):
        return None


class _LoadSignals(QObject):
    done = pyqtSignal(int, int, object)  # generation, index, QPixmap or None


class _LoadWorker(QRunnable):
    def __init__(self, generation: int, index: int, path: Path, signals: _LoadSignals):
        super().__init__()
        self.generation = generation
        self.index = index
        self.path = path
        self.signals = signals
        self.setAutoDelete(True)

    def run(self):
        px = _load_pixmap(self.path)
        self.signals.done.emit(self.generation, self.index, px)


class ImageCache:
    def __init__(self):
        self._cache: dict[int, QPixmap] = {}
        self._loading: set[int] = set()
        self._lock = threading.Lock()
        self._images: list[Path] = []
        self._folder: Path | None = None
        self._generation = 0
        self._pool = QThreadPool.globalInstance()
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
            return self._cache.get(index)

    def get_sync(self, index: int) -> QPixmap | None:
        with self._lock:
            if index in self._cache:
                return self._cache[index]
            if not self._images or index < 0 or index >= len(self._images):
                return None
            path = self._images[index]
        px = _load_pixmap(path)
        with self._lock:
            if px is not None:
                self._cache[index] = px
        return px

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
            to_load = [i for i in dict.fromkeys(indices) if i not in self._cache and i not in self._loading]
            self._loading.update(to_load)
            paths = [(i, self._images[i]) for i in to_load]

        for idx, path in paths:
            worker = _LoadWorker(gen, idx, path, self._signals)
            self._pool.start(worker)

    def _on_loaded(self, generation: int, index: int, pixmap):
        with self._lock:
            if generation != self._generation:
                return
            self._loading.discard(index)
            if pixmap is not None:
                self._cache[index] = pixmap

    def clear(self):
        with self._lock:
            self._cache.clear()
            self._loading.clear()
            self._images = []
