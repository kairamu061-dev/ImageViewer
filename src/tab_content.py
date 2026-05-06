from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter
from PyQt6.QtCore import Qt, pyqtSignal
from folder_tree import FolderTreePanel
from image_viewer_panel import ImageViewerPanel


class TabContent(QWidget):
    title_changed = pyqtSignal(str)
    add_to_favorites = pyqtSignal(Path)
    open_in_new_tab = pyqtSignal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._root_folder: Path | None = None

        self._folder_panel = FolderTreePanel(self)
        self._viewer = ImageViewerPanel(self)

        self._splitter = QSplitter(Qt.Orientation.Horizontal, self)
        self._splitter.addWidget(self._folder_panel)
        self._splitter.addWidget(self._viewer)
        self._splitter.setStretchFactor(0, 0)
        self._splitter.setStretchFactor(1, 1)
        self._splitter.setSizes([220, 980])
        self._splitter.setHandleWidth(1)
        self._splitter.setStyleSheet("QSplitter::handle { background: #3c3c3c; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._splitter)

        self._folder_panel.folder_selected.connect(self._on_folder_selected)
        self._folder_panel.add_to_favorites.connect(self.add_to_favorites)
        self._folder_panel.open_in_new_tab.connect(self.open_in_new_tab)
        self._viewer.navigate_to_folder.connect(self._on_navigate)
        self._viewer.image_changed.connect(self._emit_title)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def set_root(self, folder: Path):
        self._root_folder = folder
        self._folder_panel.set_root(folder)
        self._viewer.load_folder(folder)

    def get_state(self) -> dict:
        return {
            "root_folder": str(self._root_folder) if self._root_folder else None,
            "selected_folder": str(self._viewer._folder) if self._viewer._folder else None,
            "image_index": self._viewer._index,
            "splitter_sizes": self._splitter.sizes(),
        }

    def restore_state(self, state: dict):
        root = state.get("root_folder")
        selected = state.get("selected_folder")
        index = state.get("image_index", 0)
        sizes = state.get("splitter_sizes")

        if root:
            root_path = Path(root)
            if root_path.exists():
                self._root_folder = root_path
                self._folder_panel.set_root(root_path)

                target = Path(selected) if selected else root_path
                if target.exists():
                    self._folder_panel.select_folder(target)
                    self._viewer.load_folder(target, index)
                else:
                    self._viewer.load_folder(root_path, 0)

        if sizes and len(sizes) == 2:
            self._splitter.setSizes(sizes)

    # ------------------------------------------------------------------
    # Slots
    # ------------------------------------------------------------------

    def _on_folder_selected(self, folder: Path):
        self._viewer.load_folder(folder)

    def _on_navigate(self, folder: Path, image_index: int):
        self._folder_panel.select_folder(folder)
        self._viewer.load_folder(folder, image_index)

    def _emit_title(self):
        folder = self._viewer._folder
        if folder is None:
            self.title_changed.emit("新しいタブ")
            return
        images = self._viewer._images
        idx = self._viewer._index
        if images and 0 <= idx < len(images):
            self.title_changed.emit(f"{folder.name} | {images[idx].name}")
        else:
            self.title_changed.emit(folder.name)
