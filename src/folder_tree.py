from __future__ import annotations
import os
import subprocess
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QAbstractItemView, QMenu,
)
from PyQt6.QtCore import pyqtSignal, QDir, Qt, QModelIndex
from PyQt6.QtGui import QFileSystemModel


class FolderOnlyModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)

    def columnCount(self, parent=QModelIndex()) -> int:
        return 1


class FolderTreePanel(QWidget):
    folder_selected = pyqtSignal(Path)
    open_in_new_tab = pyqtSignal(Path)
    add_to_favorites = pyqtSignal(Path)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._model = FolderOnlyModel(self)
        self._tree = QTreeView(self)
        self._tree.setModel(self._model)
        self._tree.setHeaderHidden(True)
        self._tree.setAnimated(True)
        self._tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._tree.setIndentation(16)
        self._tree.clicked.connect(self._on_clicked)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._tree)

        self._apply_style()

    def _apply_style(self):
        self.setStyleSheet("""
            QTreeView {
                background: #252526;
                color: #CCCCCC;
                border: none;
                font-size: 13px;
            }
            QTreeView::item:selected {
                background: #2196F3;
                color: white;
            }
            QTreeView::item:hover:!selected {
                background: #2d2d30;
            }
            QTreeView::branch {
                background: #252526;
            }
            QMenu {
                background: #2d2d30;
                color: #CCCCCC;
                border: 1px solid #3c3c3c;
            }
            QMenu::item:selected {
                background: #2196F3;
            }
        """)

    def set_root(self, folder: Path):
        root_index = self._model.setRootPath(str(folder))
        self._tree.setRootIndex(root_index)

    def select_folder(self, path: Path):
        index = self._model.index(str(path))
        if index.isValid():
            self._tree.setCurrentIndex(index)
            self._tree.scrollTo(index, QAbstractItemView.ScrollHint.EnsureVisible)

    def _on_clicked(self, index):
        path = Path(self._model.filePath(index))
        self.folder_selected.emit(path)

    def _on_context_menu(self, pos):
        index = self._tree.indexAt(pos)
        if not index.isValid():
            return
        path = Path(self._model.filePath(index))
        menu = QMenu(self)
        new_tab_act = menu.addAction("別のタブとして開く")
        new_tab_act.triggered.connect(lambda: self.open_in_new_tab.emit(path))
        menu.addSeparator()
        open_act = menu.addAction("エクスプローラーで開く")
        open_act.triggered.connect(lambda: self._open_in_explorer(path))
        fav_act = menu.addAction("お気に入りに追加")
        fav_act.triggered.connect(lambda: self.add_to_favorites.emit(path))
        menu.exec(self._tree.viewport().mapToGlobal(pos))

    @staticmethod
    def _open_in_explorer(path: Path):
        subprocess.Popen(["explorer", str(path)])
