from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QSplitter, QToolButton, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from favorites_panel import FavoritesPanel
from favorites_model import FavoritesModel
from image_viewer_panel import ImageViewerPanel

_TOGGLE_STYLE = """
    QToolButton {
        background: #2a2a2a;
        color: #666;
        border: none;
        border-right: 1px solid #3c3c3c;
        font-size: 9px;
    }
    QToolButton:hover {
        background: #3a3a3a;
        color: #ccc;
    }
"""


class FavoritesTab(QWidget):
    title_changed = pyqtSignal(str)

    def __init__(self, model: FavoritesModel, parent=None):
        super().__init__(parent)
        self._model = model
        self._stored_panel_width = 220

        self._fav_panel = FavoritesPanel(model, self)
        self._viewer = ImageViewerPanel(self)

        self._splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self._splitter.addWidget(self._fav_panel)
        self._splitter.addWidget(self._viewer)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([220, 980])
        self._splitter.setHandleWidth(1)
        self._splitter.setCollapsible(0, True)
        self._splitter.setStyleSheet("QSplitter::handle { background: #3c3c3c; }")
        self._splitter.splitterMoved.connect(self._on_splitter_moved)

        self._toggle_btn = QToolButton(self)
        self._toggle_btn.setFixedWidth(16)
        self._toggle_btn.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        self._toggle_btn.setText("<")
        self._toggle_btn.setToolTip("お気に入りパネルを閉じる")
        self._toggle_btn.setStyleSheet(_TOGGLE_STYLE)
        self._toggle_btn.clicked.connect(self._toggle_panel)

        outer = QHBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(4)
        outer.addWidget(self._toggle_btn)
        outer.addWidget(self._splitter)

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

    def _toggle_panel(self):
        sizes = self._splitter.sizes()
        if sizes[0] > 0:
            self._stored_panel_width = sizes[0]
            self._splitter.setSizes([0, sum(sizes)])
            self._update_toggle_btn(0)
        else:
            total = sum(sizes)
            self._splitter.setSizes([self._stored_panel_width, total - self._stored_panel_width])
            self._update_toggle_btn(self._stored_panel_width)

    def _on_splitter_moved(self, pos: int, index: int):
        self._update_toggle_btn(self._splitter.sizes()[0])

    def _update_toggle_btn(self, panel_width: int):
        if panel_width == 0:
            self._toggle_btn.setText(">")
            self._toggle_btn.setToolTip("お気に入りパネルを開く")
        else:
            self._toggle_btn.setText("<")
            self._toggle_btn.setToolTip("お気に入りパネルを閉じる")

    def get_splitter_sizes(self) -> list[int]:
        return self._splitter.sizes()

    def restore_splitter_sizes(self, sizes: list[int]):
        if sizes and len(sizes) == 2:
            self._splitter.setSizes(sizes)
            self._update_toggle_btn(sizes[0])
