# favorites タスク

## 実装タスク一覧

- [x] FavoritesModel 実装（QStandardItemModel + JSON シリアライズ）
- [x] FavoritesPanel 実装（D&D ツリー + コンテキストメニュー）
- [x] FavoritesTab 実装（FavoritesPanel + ImageViewer + 折りたたみボタン）
- [x] 通常タブのコンテキストメニューに「お気に入りに追加」追加
- [x] AppTabWidget への FavoritesModel 登録・シグナル接続
- [x] お気に入りパネルの展開/折りたたみ矢印アイコン

## 依存関係

- FavoritesModel → FavoritesPanel → FavoritesTab
- FavoritesTab → AppTabWidget（`☆/★` ボタン制御）
- FolderTreePanel の `add_to_favorites` シグナル → AppTabWidget → FavoritesModel
