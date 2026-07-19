# grid-view タスク

## 実装タスク一覧

<!-- ステータス: [ ] 未着手 / [~] 進行中 / [x] 完了 -->

- [x] `src/grid_view.py`: ThumbnailGridView（5列グリッド・縦スクロール・非同期サムネイル）
- [x] ImageViewerPanel: QStackedWidget 化とモード切替ボタン（左上）
- [x] ImageViewerPanel: load_folder / show_image とグリッドの連携（現在位置同期）
- [x] サムネイルクリック → 1枚表示遷移
- [x] 一覧表示中のスワップボタン非表示・スライダー無効化
- [x] 動作確認（Windows 実機、2026-07-19 問題なしを確認）

## 実機フィードバック対応（2026-07-19）

- [x] サムネイルが米粒サイズになる不具合を修正（アイテムに sizeHint を明示設定）
- [x] 新規タブの一覧表示が4列になる不具合を修正（セル幅をスクロールバー幅込みで決定的に計算）
- [x] サムネイルのデコードサイズを 256px → 384px に拡大（フルHDのセル幅をカバー）
- [x] 縦スクロール幅の調整: 既定のほぼ1ページ → 1行 → 1/5行 → 最終的に 2/5行 で確定

## 依存関係

- ThumbnailGridView → ImageViewerPanel 組み込み（グリッド単体が先）
- ImageViewerPanel 組み込み → 連携・遷移・動作確認
