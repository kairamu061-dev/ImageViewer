from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import QTabWidget, QTabBar, QWidget, QHBoxLayout, QPushButton, QToolButton
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
        background: #1a1a1a;
    }
    QTabBar::tab {
        background: #252526;
        color: #777;
        padding: 7px 6px 7px 14px;
        min-width: 80px;
        max-width: 200px;
        border: none;
        border-right: 1px solid #1a1a1a;
        border-top: 3px solid transparent;
        font-size: 12px;
    }
    QTabBar::tab:selected {
        background: #3c3c3c;
        color: #ffffff;
        border-top: 3px solid #2196F3;
    }
    QTabBar::tab:hover:!selected {
        background: #2d2d30;
        color: #bbbbbb;
    }
"""

_CLOSE_BTN_STYLE = """
    QToolButton {
        color: #888;
        background: transparent;
        border: none;
        font-size: 13px;
        font-weight: bold;
        padding: 0;
        margin: 0;
    }
    QToolButton:hover {
        color: #ffffff;
        background: #c42b1c;
        border-radius: 3px;
    }
"""

_CORNER_BTN_STYLE = """
    QPushButton {
        background: #252526;
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
        self.setTabsClosable(False)   # managed manually
        self.setMovable(True)
        self.setStyleSheet(_TAB_STYLE)

        self._fav_model = FavoritesModel(self)
        self._fav_tab: FavoritesTab | None = None
        self._default_swap_mode = True   # global preference; persisted in state

        corner = QWidget()
        row = QHBoxLayout(corner)
        row.setContentsMargins(0, 0, 4, 0)
        row.setSpacing(0)
        self._btn_new = QPushButton("+", corner)
        self._btn_new.setStyleSheet(_CORNER_BTN_STYLE)
        self._btn_new.setFixedWidth(32)
        self._btn_new.clicked.connect(lambda: self.add_new_tab())
        self._btn_fav = QPushButton("☆", corner)
        self._btn_fav.setStyleSheet(_CORNER_BTN_STYLE)
        self._btn_fav.setFixedWidth(32)
        self._btn_fav.clicked.connect(self._toggle_favorites)
        row.addWidget(self._btn_new)
        row.addWidget(self._btn_fav)
        self.setCornerWidget(corner, Qt.Corner.TopRightCorner)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _make_close_btn(self, widget: QWidget) -> QToolButton:
        btn = QToolButton()
        btn.setText("×")
        btn.setFixedSize(18, 18)
        btn.setStyleSheet(_CLOSE_BTN_STYLE)
        btn.clicked.connect(lambda: self._close_by_widget(widget))
        return btn

    def _attach_close_btn(self, idx: int, widget: QWidget):
        btn = self._make_close_btn(widget)
        self.tabBar().setTabButton(idx, QTabBar.ButtonPosition.RightSide, btn)

    def _close_by_widget(self, widget: QWidget):
        idx = self.indexOf(widget)
        if idx >= 0:
            self._on_close_tab(idx)

    # ------------------------------------------------------------------
    # Tab management
    # ------------------------------------------------------------------

    def add_new_tab(self, root: Path | None = None) -> TabContent:
        content = TabContent(self)
        content.add_to_favorites.connect(self._fav_model.add_folder)
        content.open_in_new_tab.connect(self.add_new_tab)
        idx = self.addTab(content, "新しいタブ")
        self._attach_close_btn(idx, content)
        content.title_changed.connect(lambda t, c=content: self._update_title(c, t))
        content._viewer.set_swap_mode(self._default_swap_mode)
        self.setCurrentIndex(idx)
        if root:
            content.set_root(root)
        return content

    def _toggle_favorites(self):
        if self._fav_tab is None:
            self._fav_tab = FavoritesTab(self._fav_model, self)
            self._fav_tab._viewer.set_swap_mode(self._default_swap_mode)
            idx = self.addTab(self._fav_tab, "お気に入り")
            self._attach_close_btn(idx, self._fav_tab)
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

    def _get_swap_mode(self) -> bool:
        for i in range(self.count()):
            w = self.widget(i)
            if hasattr(w, "_viewer"):
                return w._viewer.get_swap_mode()
        return self._default_swap_mode

    def get_state(self) -> dict:
        fav_tab_open = self._fav_tab is not None
        fav_splitter = self._fav_tab.get_splitter_sizes() if self._fav_tab else [220, 980]
        tabs = [
            self.widget(i).get_state()
            for i in range(self.count())
            if isinstance(self.widget(i), TabContent)
        ]
        return {
            "tabs": tabs,
            "active_tab": self.currentIndex(),
            "favorites_data": self._fav_model.to_json(),
            "favorites_tab_open": fav_tab_open,
            "favorites_splitter": fav_splitter,
            "swap_mode": self._get_swap_mode(),
        }

    def restore_state(self, state: dict):
        # Restore global preference before creating tabs
        self._default_swap_mode = state.get("swap_mode", True)

        fav_data = state.get("favorites_data", [])
        if fav_data:
            self._fav_model.from_json(fav_data)

        for tab_state in state.get("tabs", []):
            content = self.add_new_tab()   # applies _default_swap_mode
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
