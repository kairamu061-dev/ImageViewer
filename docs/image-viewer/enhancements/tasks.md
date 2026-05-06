# enhancements タスク

## 実装タスク一覧

- [x] JumpSlider 実装
- [x] ImageCanvas ドラッグパン + クランプ
- [x] ImageCanvas スワップモード対応
- [x] ImageViewerPanel スワップボタン追加
- [x] ImageViewerPanel 兄弟フォルダ移動
- [x] FolderTreePanel コンテキストメニュー
- [x] TabContent フォルダパネル折りたたみボタン
- [x] FavoritesTab フォルダパネル折りたたみボタン
- [x] スワップモードのデフォルト変更（ホイール=移動）
- [x] スワップモードの状態保存/復元

## 依存関係

- JumpSlider → HoverSlider（差し替え）
- ImageCanvas スワップモード → ImageViewerPanel スワップボタン
- FolderTreePanel コンテキストメニュー → TabContent シグナル中継 → AppTabWidget
