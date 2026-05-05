from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import Qt
from image_canvas import ImageCanvas
from hover_slider import HoverSlider
from image_cache import ImageCache, SUPPORTED_EXTS


class ImageViewerPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._cache = ImageCache()
        self._images: list[Path] = []
        self._index = 0

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

    def load_folder(self, folder: Path):
        try:
            files = sorted(
                [p for p in folder.iterdir() if p.suffix.lower() in SUPPORTED_EXTS],
                key=lambda p: p.name.lower(),
            )
        except PermissionError:
            files = []

        self._images = files
        self._index = 0
        self._cache.set_folder(folder, files)
        self._slider.set_count(len(files))

        if files:
            px = self._cache.get_sync(0)
            self._canvas.set_pixmap(px)
            self._cache.preload(0)
        else:
            self._canvas.clear()

        self._reposition_slider()

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

    def next_image(self):
        if not self._images:
            return
        self.show_image((self._index + 1) % len(self._images))

    def prev_image(self):
        if not self._images:
            return
        self.show_image((self._index - 1) % len(self._images))

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
