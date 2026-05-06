# tabs タスク

## 実装タスク一覧

- [x] AppTabWidget 実装（QTabWidget 継承）
- [x] TabContent 実装（FolderTree + ImageViewer + トグルボタン）
- [x] タブタイトルの動的更新（image_changed シグナル連携）
- [x] カスタム × クローズボタン（setTabButton）
- [x] 最後の通常タブを閉じない制御
- [x] `+` ボタンで新規タブ追加
- [x] `☆/★` ボタンでお気に入りタブ開閉
- [x] 「別のタブとして開く」シグナル中継

## 依存関係

- TabContent → AppTabWidget
- FavoritesTab → AppTabWidget（`☆` 制御）
