from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import QMainWindow, QFileDialog, QToolBar
from PyQt6.QtGui import QAction
from app_tabs import AppTabWidget
import state_manager


class MainWindow(QMainWindow):
    def __init__(self, initial_path: Path | None = None):
        super().__init__()
        self.setWindowTitle("画像ビューアー")
        self.resize(1200, 800)

        self._tabs = AppTabWidget(self)
        self.setCentralWidget(self._tabs)

        self._build_toolbar()
        self._apply_style()

        # Launched with a file/folder (e.g. a file association): open just
        # that, and don't persist it on close so the user's normal saved
        # session isn't clobbered by an ad-hoc "open this image" launch.
        self._persist_on_close = initial_path is None
        if initial_path is not None:
            self._open_initial_path(initial_path)
        else:
            self._restore_state()

    def _open_initial_path(self, path: Path):
        if path.is_file():
            self._tabs.add_new_tab(path.parent, initial_image=path)
        elif path.is_dir():
            self._tabs.add_new_tab(path)
        else:
            self._restore_state()

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
        open_act = QAction("フォルダを開く", self)
        open_act.triggered.connect(self.open_folder_dialog)
        toolbar.addAction(open_act)
        self.addToolBar(toolbar)

    def _apply_style(self):
        self.setStyleSheet("QMainWindow { background: #1E1E1E; }")

    def open_folder_dialog(self):
        folder = QFileDialog.getExistingDirectory(
            self, "フォルダを選択", str(Path.home()),
            QFileDialog.Option.ShowDirsOnly,
        )
        if folder:
            self._tabs.add_new_tab(Path(folder))

    def _restore_state(self):
        state = state_manager.load()
        if state.get("tabs"):
            self._tabs.restore_state(state)
            geo = state.get("window")
            if geo:
                self.setGeometry(geo["x"], geo["y"], geo["width"], geo["height"])
        else:
            self._tabs.add_new_tab()

    def closeEvent(self, event):
        if self._persist_on_close:
            geo = self.geometry()
            state = self._tabs.get_state()
            state["window"] = {
                "x": geo.x(), "y": geo.y(),
                "width": geo.width(), "height": geo.height(),
            }
            state_manager.save(state)
        super().closeEvent(event)
