from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QSplitter, QFileDialog, QToolBar, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction, QIcon
from folder_tree import FolderTreePanel
from image_viewer_panel import ImageViewerPanel


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("画像ビューアー")
        self.resize(1200, 800)

        self._folder_panel = FolderTreePanel(self)
        self._viewer_panel = ImageViewerPanel(self)

        splitter = QSplitter(Qt.Orientation.Horizontal, self)
        splitter.addWidget(self._folder_panel)
        splitter.addWidget(self._viewer_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([220, 980])
        splitter.setHandleWidth(1)
        splitter.setStyleSheet("QSplitter::handle { background: #3c3c3c; }")

        self.setCentralWidget(splitter)
        self._folder_panel.folder_selected.connect(self._on_folder_selected)

        self._build_toolbar()
        self._apply_style()

    def _build_toolbar(self):
        toolbar = QToolBar("メイン", self)
        toolbar.setMovable(False)
        toolbar.setStyleSheet("""
            QToolBar {
                background: #2d2d30;
                border-bottom: 1px solid #3c3c3c;
                spacing: 4px;
                padding: 2px 6px;
            }
            QToolButton {
                color: #CCCCCC;
                background: transparent;
                border: none;
                padding: 4px 10px;
                font-size: 13px;
            }
            QToolButton:hover {
                background: #3e3e42;
                border-radius: 3px;
            }
        """)
        open_action = QAction("フォルダを開く", self)
        open_action.triggered.connect(self.open_folder_dialog)
        toolbar.addAction(open_action)
        self.addToolBar(toolbar)

    def _apply_style(self):
        self.setStyleSheet("""
            QMainWindow {
                background: #1E1E1E;
            }
        """)

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(
            self, "フォルダを選択", str(Path.home()),
            QFileDialog.Option.ShowDirsOnly,
        )
        if folder:
            self._load_root(Path(folder))

    def _load_root(self, folder: Path):
        self._folder_panel.set_root(folder)
        self._viewer_panel.load_folder(folder)

    def _on_folder_selected(self, folder: Path):
        self._viewer_panel.load_folder(folder)
