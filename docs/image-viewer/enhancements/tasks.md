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

## 実機フィードバック対応（2026-10-09）

- [x] ファイル一覧・兄弟フォルダ一覧を自然順ソートに変更（`_natural_sort_key`）
- [x] 兄弟フォルダ移動から隠しフォルダを除外（`QFileInfo.isHidden()`）
- [x] `_natural_sort_key` の実装を正規表現ベースから `QCollator` に変更（日本語名の読み順がフォルダツリーと食い違う不具合の修正）
- [x] ソート方式を再変更: 数字部分は Python int 比較、文字部分のみ `QCollator.compare()` のハイブリッドに（`(C99)`/`(C100)` の順序が `QCollator` 数値モード単体では逆転する不具合の修正）

## 依存関係

- JumpSlider → HoverSlider（差し替え）
- ImageCanvas スワップモード → ImageViewerPanel スワップボタン
- FolderTreePanel コンテキストメニュー → TabContent シグナル中継 → AppTabWidget
