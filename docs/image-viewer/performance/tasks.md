# performance タスク

## 実装タスク一覧

- [x] ImageCache: `_cache` を OrderedDict 化し CACHE_LIMIT=60 でLRU破棄
- [x] ImageCache: `get_sync()` に1回リトライを追加
- [x] FolderOnlyModel: 専用 QThreadPool（maxThreadCount=2）に変更
- [x] ThumbnailGridView: 専用 QThreadPool に変更
- [x] ThumbnailGridView: `_ensure_visible_loaded()` による可視範囲優先読み込みに変更（`_start_loading` の全件一括読み込みを廃止）
- [ ] 実機確認: フォルダツリー・一覧スクロールの重さ（未確認）
- [!] 実機確認: 大きいフォルダでの「画像がありません」再発有無 → LRU化後も再発を確認。原因未解決だった
- [x] `_load_qimage` / `_load_thumb` / `show_image` に診断用ログを追加（`%TEMP%\ImageViewer.log`）
- [x] ログから原因特定（同一ファイルへの読み込みが約1秒近く連続失敗 = 外部要因による一時ブロックと判断）
- [x] `ImageViewerPanel` にバックオフ付き遅延リトライ（300ms/1000ms/3000ms）を追加
- [!] 実機確認: 遅延リトライで「画像がありません」が解消されるか → 2回目のユーザ確認でも解消せず
- [x] 2回目のログから追加原因を推定（プリロードの並列読み込みによる同一ドライブへのスラッシング）
- [x] ImageCache 専用プール（並列度2）に変更、遅延リトライ間隔を 500/1500/4000/9000ms（計4回）に延長
- [ ] 実機確認: 上記2点の追加対応で「画像がありません」が解消されるか（未確認）

## 依存関係

- ImageCache の変更と ThumbnailGridView / FolderOnlyModel の変更は互いに独立（並行実装済み）
- ログ追加 → 原因特定 → 遅延リトライ実装 → 再発確認 → 並列度制限・リトライ間隔延長（この順で進めた）
