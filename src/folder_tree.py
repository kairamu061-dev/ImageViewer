from __future__ import annotations
import os
import subprocess
import tempfile
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QTreeView, QAbstractItemView, QMenu,
)
from PyQt6.QtCore import pyqtSignal, QDir, Qt, QModelIndex
from PyQt6.QtGui import QFileSystemModel, QPixmap, QPainter, QPainterPath, QColor

_ARROW_PATHS: dict[str, str] = {}


def _ensure_arrow_paths() -> dict[str, str]:
    """Generate branch arrow PNG files once and cache their paths."""
    global _ARROW_PATHS
    if _ARROW_PATHS:
        return _ARROW_PATHS
    tmpdir = tempfile.gettempdir()
    shapes = {
        "closed": [(2.5, 1.5), (8.5, 5.0), (2.5, 8.5)],   # ▶ right-pointing
        "open":   [(1.5, 2.5), (8.5, 2.5), (5.0, 8.5)],   # ▼ down-pointing
    }
    for name, pts in shapes.items():
        px = QPixmap(10, 10)
        px.fill(Qt.GlobalColor.transparent)
        p = QPainter(px)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        path = QPainterPath()
        path.moveTo(*pts[0])
        for pt in pts[1:]:
            path.lineTo(*pt)
        path.closeSubpath()
        p.fillPath(path, QColor("#999999"))
        p.end()
        out = os.path.join(tmpdir, f"iv_branch_{name}.png")
        px.save(out)
        _ARROW_PATHS[name] = out.replace("\\", "/")
    return _ARROW_PATHS


class FolderOnlyModel(QFileSystemModel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFilter(QDir.Filter.Dirs | QDir.Filter.NoDotAndDotDot)
        self._subdir_cache: dict[str, bool] = {}
        self.directoryLoaded.connect(lambda p: self._subdir_cache.pop(p, None))

    def columnCount(self, parent=QModelIndex()) -> int:
        return 1

    def hasChildren(self, parent=QModelIndex()) -> bool:
        if not parent.isValid():
            return self.rowCount() > 0
        path = self.filePath(parent)
        if path not in self._subdir_cache:
            try:
                self._subdir_cache[path] = any(
                    e.is_dir() for e in Path(path).iterdir()
                )
            except OSError:
                self._subdir_cache[path] = False
        return self._subdir_cache[path]


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
        self._tree.setIndentation(18)
        self._tree.clicked.connect(self._on_clicked)
        self._tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self._tree)

        self._apply_style()

    def _apply_style(self):
        arrows = _ensure_arrow_paths()
        closed = arrows.get("closed", "")
        opened = arrows.get("open", "")
        self.setStyleSheet(f"""
            QTreeView {{
                background: #252526;
                color: #CCCCCC;
                border: none;
                font-size: 13px;
            }}
            QTreeView::item {{
                padding: 2px 0;
            }}
            QTreeView::item:selected {{
                background: #2196F3;
                color: white;
            }}
            QTreeView::item:hover:!selected {{
                background: #2d2d30;
            }}
            QTreeView::branch {{
                background: #252526;
            }}
            QTreeView::branch:has-children:closed {{
                image: url({closed});
            }}
            QTreeView::branch:open:has-children {{
                image: url({opened});
            }}
            QMenu {{
                background: #2d2d30;
                color: #CCCCCC;
                border: 1px solid #3c3c3c;
            }}
            QMenu::item:selected {{
                background: #2196F3;
            }}
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
        menu.addAction("別のタブとして開く").triggered.connect(
            lambda: self.open_in_new_tab.emit(path)
        )
        menu.addSeparator()
        menu.addAction("エクスプローラーで開く").triggered.connect(
            lambda: self._open_in_explorer(path)
        )
        menu.addAction("お気に入りに追加").triggered.connect(
            lambda: self.add_to_favorites.emit(path)
        )
        menu.exec(self._tree.viewport().mapToGlobal(pos))

    @staticmethod
    def _open_in_explorer(path: Path):
        subprocess.Popen(["explorer", str(path)])
