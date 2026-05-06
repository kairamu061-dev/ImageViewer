from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QAbstractItemView, QMenu, QInputDialog,
)
from PyQt6.QtCore import pyqtSignal, Qt
from favorites_model import FavoritesModel, ITEM_DATA_ROLE, KIND_FOLDER, KIND_GROUP
from PyQt6.QtGui import QStandardItem


class FavoritesPanel(QWidget):
    folder_selected = pyqtSignal(Path)

    def __init__(self, model: FavoritesModel, parent=None):
        super().__init__(parent)
        self._model = model

        self._tree = QTreeView(self)
        self._tree.setModel(self._model)
        self._tree.setHeaderHidden(True)
        self._tree.setAnimated(True)
        self._tree.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self._tree.setIndentation(16)
        self._tree.setDragDropMode(QAbstractItemView.DragDropMode.InternalMove)
        self._tree.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._tree.setDropIndicatorShown(True)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
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
            QMenu {
                background: #2d2d30;
                color: #CCCCCC;
                border: 1px solid #3c3c3c;
            }
            QMenu::item:selected {
                background: #2196F3;
            }
        """)

    def _on_clicked(self, index):
        item = self._model.itemFromIndex(index)
        if item is None:
            return
        d = item.data(ITEM_DATA_ROLE) or {}
        if d.get("kind") == KIND_FOLDER:
            path = Path(d["path"])
            if path.exists():
                self.folder_selected.emit(path)

    def _on_context_menu(self, pos):
        index = self._tree.indexAt(pos)
        menu = QMenu(self)

        if index.isValid():
            item = self._model.itemFromIndex(index)
            d = item.data(ITEM_DATA_ROLE) or {}
            kind = d.get("kind")
            if kind == KIND_GROUP:
                rename_act = menu.addAction("名前を変更")
                rename_act.triggered.connect(lambda: self._rename_group(item))
                menu.addSeparator()
            del_act = menu.addAction("削除")
            del_act.triggered.connect(lambda: self._model.remove_item(item))
        else:
            add_act = menu.addAction("階層を追加")
            add_act.triggered.connect(lambda: self._model.add_group())

        menu.exec(self._tree.viewport().mapToGlobal(pos))

    def _rename_group(self, item: QStandardItem):
        old = item.text()
        new, ok = QInputDialog.getText(self, "名前を変更", "新しい名前:", text=old)
        if ok and new.strip():
            self._model.rename_item(item, new.strip())
