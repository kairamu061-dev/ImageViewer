# tabs 設計

## 技術選定

| 技術 | 用途 | 選定理由 |
|------|------|----------|
| QTabWidget | タブ管理 | Qt 標準ウィジェット。スタック管理が内蔵 |
| QTabBar.setTabButton | カスタム × ボタン | setTabsClosable のデフォルトアイコンが暗い背景で見えないため手動実装 |
| QHBoxLayout (コーナーウィジェット) | `+` / `☆` ボタン | setCornerWidget で TabBar 右端に配置 |

## アーキテクチャ

```
AppTabWidget (QTabWidget)
  ├── _fav_model: FavoritesModel  (共有データ)
  ├── _fav_tab: FavoritesTab | None
  ├── _default_swap_mode: bool
  ├── add_new_tab(root?) → TabContent
  ├── _toggle_favorites() → FavoritesTab
  └── コーナー: [+] [☆/★]

TabContent (QWidget) — 通常タブの中身
  ├── FolderTreePanel (左)
  ├── ImageViewerPanel (右)
  ├── QSplitter
  ├── _toggle_btn: < / > ボタン
  └── シグナル: title_changed, add_to_favorites, open_in_new_tab
```

## インターフェース

```python
class AppTabWidget(QTabWidget):
    def add_new_tab(self, root: Path | None = None) -> TabContent
    def get_state(self) -> dict
    def restore_state(self, state: dict)

class TabContent(QWidget):
    title_changed = pyqtSignal(str)
    add_to_favorites = pyqtSignal(Path)
    open_in_new_tab = pyqtSignal(Path)
    def set_root(self, folder: Path)
    def get_state(self) -> dict
    def restore_state(self, state: dict)
```

## 依存関係

| ライブラリ / サービス | 用途 |
|-----------------------|------|
| PyQt6.QtWidgets.QTabWidget | タブ UI |
| PyQt6.QtWidgets.QTabBar | カスタムボタン配置 |
