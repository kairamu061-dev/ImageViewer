from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt, pyqtSignal
from favorites_panel import FavoritesPanel
from favorites_model import FavoritesModel
from image_viewer_panel import ImageViewerPanel


class FavoritesTab(QWidget):
    title_changed = pyqtSignal(str)

    def __init__(self, model: FavoritesModel, parent=None):
        super().__init__(parent)
        self._model = model

        self._fav_panel = FavoritesPanel(model, self)
        self._viewer = ImageViewerPanel(self)

        self._splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self._splitter.addWidget(self._fav_panel)
        self._splitter.addWidget(self._viewer)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([220, 980])
        self._splitter.setHandleWidth(1)
        self._splitter.setStyleSheet("QSplitter::handle { background: #3c3c3c; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._splitter)

        self._fav_panel.folder_selected.connect(self._on_folder_selected)
        self._viewer.image_changed.connect(self._emit_title)

    def _on_folder_selected(self, folder: Path):
        self._viewer.load_folder(folder)

    def _emit_title(self):
        folder = self._viewer._folder
        images = self._viewer._images
        idx = self._viewer._index
        if folder and images and 0 <= idx < len(images):
            self.title_changed.emit(f"★ {folder.name} | {images[idx].name}")
        elif folder:
            self.title_changed.emit(f"★ {folder.name}")
        else:
            self.title_changed.emit("お気に入り")

    def get_splitter_sizes(self) -> list[int]:
        return self._splitter.sizes()

    def restore_splitter_sizes(self, sizes: list[int]):
        if sizes and len(sizes) == 2:
            self._splitter.setSizes(sizes)
