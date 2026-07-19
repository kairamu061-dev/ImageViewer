# grid-view タスク

## 実装タスク一覧

<!-- ステータス: [ ] 未着手 / [~] 進行中 / [x] 完了 -->

- [x] `src/grid_view.py`: ThumbnailGridView（5列グリッド・縦スクロール・非同期サムネイル）
- [x] ImageViewerPanel: QStackedWidget 化とモード切替ボタン（左上）
- [x] ImageViewerPanel: load_folder / show_image とグリッドの連携（現在位置同期）
- [x] サムネイルクリック → 1枚表示遷移
- [x] 一覧表示中のスワップボタン非表示・スライダー無効化
- [ ] 動作確認（リサイズ時5列維持・空フォルダ・大量画像）※本環境に Python が無いため Windows 側で要確認

## 依存関係

- ThumbnailGridView → ImageViewerPanel 組み込み（グリッド単体が先）
- ImageViewerPanel 組み込み → 連携・遷移・動作確認
