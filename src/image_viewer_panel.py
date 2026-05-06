from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal
from image_canvas import ImageCanvas
from hover_slider import HoverSlider
from image_cache import ImageCache, SUPPORTED_EXTS


class ImageViewerPanel(QWidget):
    image_changed = pyqtSignal()
    navigate_to_folder = pyqtSignal(Path, int)  # path, image_index (-1 = last)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._cache = ImageCache()
        self._images: list[Path] = []
        self._index = 0
        self._folder: Path | None = None

        self._canvas = ImageCanvas(self)
        self._slider = HoverSlider(self)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._canvas)

        self._canvas.next_requested.connect(self.next_image)
        self._canvas.prev_requested.connect(self.prev_image)
        self._canvas.hover_bottom.connect(self._on_hover_bottom)
        self._slider.index_changed.connect(self._on_slider_changed)

        self.setStyleSheet("background: #1E1E1E;")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition_slider()

    def _reposition_slider(self):
        h = 48
        self._slider.setGeometry(0, self.height() - h, self.width(), h)

    def load_folder(self, folder: Path, initial_index: int = 0):
        try:
            files = sorted(
                [p for p in folder.iterdir() if p.suffix.lower() in SUPPORTED_EXTS],
                key=lambda p: p.name.lower(),
            )
        except PermissionError:
            files = []

        self._folder = folder
        self._images = files
        self._cache.set_folder(folder, files)
        self._slider.set_count(len(files))

        if files:
            if initial_index == -1:
                idx = len(files) - 1
            else:
                idx = max(0, min(initial_index, len(files) - 1))
            self._index = idx
            px = self._cache.get_sync(idx)
            self._canvas.set_pixmap(px)
            self._slider.set_index(idx)
            self._cache.preload(idx)
        else:
            self._index = 0
            self._canvas.clear()

        self._reposition_slider()
        self.image_changed.emit()

    def show_image(self, index: int):
        if not self._images:
            return
        self._index = index
        px = self._cache.get(index)
        if px is None:
            px = self._cache.get_sync(index)
        self._canvas.set_pixmap(px)
        self._slider.set_index(index)
        self._cache.preload(index)
        self.image_changed.emit()

    def next_image(self):
        if not self._images:
            return
        next_idx = self._index + 1
        if next_idx >= len(self._images):
            sibling = self._get_sibling_folder(+1)
            if sibling is not None:
                self.navigate_to_folder.emit(sibling, 0)
                return
            next_idx = 0
        self.show_image(next_idx)

    def prev_image(self):
        if not self._images:
            return
        prev_idx = self._index - 1
        if prev_idx < 0:
            sibling = self._get_sibling_folder(-1)
            if sibling is not None:
                self.navigate_to_folder.emit(sibling, -1)
                return
            prev_idx = len(self._images) - 1
        self.show_image(prev_idx)

    def _get_sibling_folder(self, direction: int) -> Path | None:
        if self._folder is None:
            return None
        parent = self._folder.parent
        try:
            siblings = sorted(
                [p for p in parent.iterdir() if p.is_dir()],
                key=lambda p: p.name.lower(),
            )
        except PermissionError:
            return None
        try:
            idx = siblings.index(self._folder)
        except ValueError:
            return None
        target = idx + direction
        if 0 <= target < len(siblings):
            return siblings[target]
        return None

    def _on_hover_bottom(self, entered: bool):
        if len(self._images) < 2:
            return
        if entered:
            self._slider.show_slider()
        else:
            self._slider.start_hide()

    def _on_slider_changed(self, value: int):
        if value != self._index:
            self.show_image(value)
