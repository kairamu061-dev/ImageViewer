# favorites 設計

## 技術選定

| 技術 | 用途 | 選定理由 |
|------|------|----------|
| QStandardItemModel | お気に入りデータモデル | D&D・ツリー構造・シリアライズに対応。カスタムモデルより実装コストが低い |
| QAbstractItemView.InternalMove | D&D モード | 内部移動のみ許可。外部ドラッグは不要のためシンプルに設定 |
| JSON | データ永続化 | state_manager の共通フォーマットに統一 |

## アーキテクチャ

```
FavoritesModel (QStandardItemModel)
  ├── add_folder(path)
  ├── add_group(name, parent?)
  ├── rename_item(item, name)
  ├── remove_item(item)
  ├── to_json() → list
  └── from_json(list)

FavoritesPanel (QWidget)
  ├── QTreeView (InternalMove D&D)
  ├── folder_selected シグナル
  └── _on_context_menu: 空白/フォルダ/グループで内容が変わる

FavoritesTab (QWidget)
  ├── FavoritesPanel (左)
  ├── ImageViewerPanel (右)
  ├── QSplitter
  └── _toggle_btn: < / > ボタン
```

## データ構造

```python
# FavoritesModel の各アイテムのカスタムデータ（UserRole+1）
{
    "kind": "folder" | "group",
    "path": str,        # folder のみ
    "name": str,        # group のみ（表示名）
}

# JSON シリアライズ形式
[
    {"kind": "folder", "path": "C:/photos", "name": "photos"},
    {"kind": "group", "name": "旅行", "children": [
        {"kind": "folder", "path": "C:/travel/2024", "name": "2024"}
    ]}
]
```

## 依存関係

| ライブラリ / サービス | 用途 |
|-----------------------|------|
| PyQt6.QtGui.QStandardItemModel | ツリーデータ管理 |
| PyQt6.QtWidgets.QInputDialog | グループ名変更ダイアログ |
