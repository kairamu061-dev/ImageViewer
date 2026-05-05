from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTreeView, QAbstractItemView
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
        """)

    def set_root(self, folder: Path):
        root_index = self._model.setRootPath(str(folder))
        self._tree.setRootIndex(root_index)

    def _on_clicked(self, index):
        path = Path(self._model.filePath(index))
        self.folder_selected.emit(path)
