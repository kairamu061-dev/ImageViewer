from __future__ import annotations
from pathlib import Path
from PyQt6.QtGui import QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt

ITEM_DATA_ROLE = Qt.ItemDataRole.UserRole + 1
KIND_FOLDER = "folder"
KIND_GROUP = "group"

_BASE_FLAGS = (
    Qt.ItemFlag.ItemIsEnabled
    | Qt.ItemFlag.ItemIsSelectable
    | Qt.ItemFlag.ItemIsDragEnabled
    | Qt.ItemFlag.ItemIsDropEnabled
)


def _make_folder_item(path: Path) -> QStandardItem:
    item = QStandardItem(path.name)
    item.setData({"kind": KIND_FOLDER, "path": str(path)}, ITEM_DATA_ROLE)
    item.setFlags(_BASE_FLAGS)
    return item


def _make_group_item(name: str = "階層") -> QStandardItem:
    item = QStandardItem(name)
    item.setData({"kind": KIND_GROUP, "name": name}, ITEM_DATA_ROLE)
    item.setFlags(_BASE_FLAGS)
    return item


class FavoritesModel(QStandardItemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setItemPrototype(QStandardItem())

    def add_folder(self, path: Path):
        # Avoid duplicates at top level
        for row in range(self.rowCount()):
            item = self.item(row)
            data = item.data(ITEM_DATA_ROLE) or {}
            if data.get("kind") == KIND_FOLDER and data.get("path") == str(path):
                return
        self.appendRow(_make_folder_item(path))

    def add_group(self, name: str = "階層", parent_item: QStandardItem | None = None):
        item = _make_group_item(name)
        if parent_item is not None:
            parent_item.appendRow(item)
        else:
            self.appendRow(item)

    def rename_item(self, item: QStandardItem, new_name: str):
        item.setText(new_name)
        data = item.data(ITEM_DATA_ROLE) or {}
        data["name"] = new_name
        item.setData(data, ITEM_DATA_ROLE)

    def remove_item(self, item: QStandardItem):
        parent = item.parent()
        if parent is None:
            self.removeRow(item.row())
        else:
            parent.removeRow(item.row())

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------

    def to_json(self) -> list:
        return _serialize(self.invisibleRootItem())

    def from_json(self, data: list):
        self.clear()
        _deserialize(data, self.invisibleRootItem())


def _serialize(parent: QStandardItem) -> list:
    result = []
    for row in range(parent.rowCount()):
        item = parent.child(row)
        d = item.data(ITEM_DATA_ROLE) or {}
        if d.get("kind") == KIND_FOLDER:
            result.append({"kind": KIND_FOLDER, "path": d.get("path", ""), "name": item.text()})
        else:
            result.append({
                "kind": KIND_GROUP,
                "name": item.text(),
                "children": _serialize(item),
            })
    return result


def _deserialize(data: list, parent: QStandardItem):
    for entry in data:
        if entry.get("kind") == KIND_FOLDER:
            path_str = entry.get("path", "")
            name = entry.get("name") or Path(path_str).name
            item = QStandardItem(name)
            item.setData({"kind": KIND_FOLDER, "path": path_str}, ITEM_DATA_ROLE)
            item.setFlags(_BASE_FLAGS)
            parent.appendRow(item)
        else:
            name = entry.get("name", "階層")
            item = _make_group_item(name)
            parent.appendRow(item)
            _deserialize(entry.get("children", []), item)
