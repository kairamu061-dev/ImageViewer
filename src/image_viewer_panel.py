from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QStackedWidget
from PyQt6.QtCore import pyqtSignal
from image_canvas import ImageCanvas
from grid_view import ThumbnailGridView
from hover_slider import HoverSlider
from image_cache import ImageCache, SUPPORTED_EXTS

_SWAP_BTN_STYLE = """
    QPushButton {
        background: rgba(40, 40, 40, 210);
        color: #aaa;
        border: 1px solid #555;
        border-radius: 3px;
        font-size: 11px;
        padding: 0 4px;
    }
    QPushButton:checked {
        background: rgba(33, 150, 243, 180);
        color: #fff;
        border-color: #2196F3;
    }
    QPushButton:hover {
        color: #fff;
    }
"""


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
        self._grid = ThumbnailGridView(self)
        self._slider = HoverSlider(self)

        self._stack = QStackedWidget(self)
        self._stack.addWidget(self._canvas)
        self._stack.addWidget(self._grid)

        # View-mode toggle button (overlay, top-left)
        self._mode_btn = QPushButton("一覧", self)
        self._mode_btn.setCheckable(True)
        self._mode_btn.setFixedSize(52, 22)
        self._mode_btn.setToolTip("一覧表示に切り替え")
        self._mode_btn.setStyleSheet(_SWAP_BTN_STYLE)
        self._mode_btn.toggled.connect(self._on_mode_toggled)
        self._mode_btn.raise_()

        # Swap toggle button (overlay, top-right)
        self._swap_btn = QPushButton("W:移動", self)
        self._swap_btn.setCheckable(True)
        self._swap_btn.setFixedSize(72, 22)
        self._swap_btn.setToolTip(
            "ホイール=移動 / サイドボタン=拡縮\nクリックで切り替え"
        )
        self._swap_btn.setStyleSheet(_SWAP_BTN_STYLE)
        self._swap_btn.toggled.connect(self._on_swap_toggled)
        self._swap_btn.setChecked(True)   # default: wheel=navigate
        self._swap_btn.raise_()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.addWidget(self._stack)

        self._canvas.next_requested.connect(self.next_image)
        self._canvas.prev_requested.connect(self.prev_image)
        self._canvas.hover_bottom.connect(self._on_hover_bottom)
        self._grid.image_activated.connect(self._on_thumb_activated)
        self._slider.index_changed.connect(self._on_slider_changed)

        self.setStyleSheet("background: #1E1E1E;")

    def get_swap_mode(self) -> bool:
        return self._swap_btn.isChecked()

    def set_swap_mode(self, mode: bool):
        if self._swap_btn.isChecked() != mode:
            self._swap_btn.setChecked(mode)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._reposition_slider()
        b = self._swap_btn
        b.move(self.width() - b.width() - 6, 6)
        b.raise_()
        self._mode_btn.move(6, 6)
        self._mode_btn.raise_()

    def _reposition_slider(self):
        h = 48
        self._slider.setGeometry(0, self.height() - h, self.width(), h)
        self._slider.raise_()

    def _on_swap_toggled(self, checked: bool):
        self._canvas.swap_mode = checked
        if checked:
            self._swap_btn.setText("W:移動")
            self._swap_btn.setToolTip(
                "ホイール=移動 / サイドボタン=拡縮\nクリックで切り替え"
            )
        else:
            self._swap_btn.setText("W:拡縮")
            self._swap_btn.setToolTip(
                "ホイール=拡縮 / サイドボタン=移動\nクリックで切り替え"
            )

    def _on_mode_toggled(self, checked: bool):
        if checked:
            self._stack.setCurrentWidget(self._grid)
            self._mode_btn.setText("1枚")
            self._mode_btn.setToolTip("1枚表示に切り替え")
            self._swap_btn.hide()
            self._slider.hide()
            self._grid.select_index(self._index)
        else:
            self._stack.setCurrentWidget(self._canvas)
            self._mode_btn.setText("一覧")
            self._mode_btn.setToolTip("一覧表示に切り替え")
            self._swap_btn.show()

    def _on_thumb_activated(self, index: int):
        self._mode_btn.setChecked(False)   # back to single view
        self.show_image(index)

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
        self._grid.set_images(files)

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
            if self._mode_btn.isChecked():
                self._grid.select_index(idx)
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
        if len(self._images) < 2 or self._mode_btn.isChecked():
            return
        if entered:
            self._slider.show_slider()
        else:
            self._slider.start_hide()

    def _on_slider_changed(self, value: int):
        if value != self._index:
            self.show_image(value)
