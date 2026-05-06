from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import QTabWidget, QWidget, QHBoxLayout, QPushButton
from PyQt6.QtCore import Qt
from tab_content import TabContent
from favorites_tab import FavoritesTab
from favorites_model import FavoritesModel


_TAB_STYLE = """
    QTabWidget::pane {
        border: none;
        background: #1E1E1E;
    }
    QTabBar {
        background: #252526;
    }
    QTabBar::tab {
        background: #2d2d30;
        color: #888;
        padding: 7px 6px 7px 14px;
        min-width: 80px;
        max-width: 200px;
        border: none;
        border-right: 1px solid #1a1a1a;
        border-top: 2px solid transparent;
        font-size: 12px;
    }
    QTabBar::tab:selected {
        background: #1E1E1E;
        color: #fff;
        border-top: 2px solid #2196F3;
    }
    QTabBar::tab:hover:!selected {
        background: #3e3e42;
        color: #ccc;
    }
    QTabBar::close-button {
        subcontrol-position: right;
        margin: 2px 4px;
        border-radius: 3px;
        padding: 1px;
    }
    QTabBar::close-button:hover {
        background: #c42b1c;
    }
"""

_BTN_STYLE = """
    QPushButton {
        background: #2d2d30;
        color: #CCCCCC;
        border: none;
        padding: 4px 10px;
        font-size: 14px;
    }
    QPushButton:hover {
        background: #3e3e42;
    }
"""


class AppTabWidget(QTabWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setTabsClosable(True)
        self.setMovable(True)
        self.setStyleSheet(_TAB_STYLE)
        self.tabCloseRequested.connect(self._on_close_tab)

        self._fav_model = FavoritesModel(self)
        self._fav_tab: FavoritesTab | None = None

        corner = QWidget()
        row = QHBoxLayout(corner)
        row.setContentsMargins(0, 0, 4, 0)
        row.setSpacing(0)
        self._btn_new = QPushButton("+", corner)
        self._btn_new.setStyleSheet(_BTN_STYLE)
        self._btn_new.setFixedWidth(32)
        self._btn_new.clicked.connect(lambda: self.add_new_tab())
        self._btn_fav = QPushButton("☆", corner)
        self._btn_fav.setStyleSheet(_BTN_STYLE)
        self._btn_fav.setFixedWidth(32)
        self._btn_fav.clicked.connect(self._toggle_favorites)
        row.addWidget(self._btn_new)
        row.addWidget(self._btn_fav)
        self.setCornerWidget(corner, Qt.Corner.TopRightCorner)

    # ------------------------------------------------------------------
    # Tab management
    # ------------------------------------------------------------------

    def add_new_tab(self, root: Path | None = None) -> TabContent:
        content = TabContent(self)
        content.add_to_favorites.connect(self._fav_model.add_folder)
        content.open_in_new_tab.connect(self.add_new_tab)
        idx = self.addTab(content, "新しいタブ")
        content.title_changed.connect(lambda t, c=content: self._update_title(c, t))
        self.setCurrentIndex(idx)
        if root:
            content.set_root(root)
        return content

    def _toggle_favorites(self):
        if self._fav_tab is None:
            self._fav_tab = FavoritesTab(self._fav_model, self)
            idx = self.addTab(self._fav_tab, "お気に入り")
            self._fav_tab.title_changed.connect(
                lambda t, f=self._fav_tab: self._update_title(f, t)
            )
            self.setCurrentIndex(idx)
            self._btn_fav.setText("★")
        else:
            self.setCurrentWidget(self._fav_tab)

    def _on_close_tab(self, index: int):
        widget = self.widget(index)
        if widget is self._fav_tab:
            self._fav_tab = None
            self._btn_fav.setText("☆")
        # Keep at least one regular tab open
        regular_count = sum(
            1 for i in range(self.count())
            if not isinstance(self.widget(i), FavoritesTab)
        )
        if not isinstance(widget, FavoritesTab) and regular_count <= 1:
            return
        self.removeTab(index)
        widget.deleteLater()

    def _update_title(self, widget: QWidget, title: str):
        idx = self.indexOf(widget)
        if idx >= 0:
            self.setTabText(idx, title)
            self.setTabToolTip(idx, title)

    # ------------------------------------------------------------------
    # State
    # ------------------------------------------------------------------

    def get_state(self) -> dict:
        tabs = []
        fav_tab_open = self._fav_tab is not None
        fav_splitter = self._fav_tab.get_splitter_sizes() if self._fav_tab else [220, 980]

        for i in range(self.count()):
            w = self.widget(i)
            if isinstance(w, TabContent):
                tabs.append(w.get_state())

        return {
            "tabs": tabs,
            "active_tab": self.currentIndex(),
            "favorites_data": self._fav_model.to_json(),
            "favorites_tab_open": fav_tab_open,
            "favorites_splitter": fav_splitter,
        }

    def restore_state(self, state: dict):
        fav_data = state.get("favorites_data", [])
        if fav_data:
            self._fav_model.from_json(fav_data)

        for tab_state in state.get("tabs", []):
            content = self.add_new_tab()
            content.restore_state(tab_state)

        if state.get("favorites_tab_open"):
            self._toggle_favorites()
            if self._fav_tab:
                self._fav_tab.restore_splitter_sizes(
                    state.get("favorites_splitter", [220, 980])
                )

        active = state.get("active_tab", 0)
        if 0 <= active < self.count():
            self.setCurrentIndex(active)
