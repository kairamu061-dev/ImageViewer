# performance タスク

## 実装タスク一覧

- [x] ImageCache: `_cache` を OrderedDict 化し CACHE_LIMIT=60 でLRU破棄
- [x] ImageCache: `get_sync()` に1回リトライを追加
- [x] FolderOnlyModel: 専用 QThreadPool（maxThreadCount=2）に変更
- [x] ThumbnailGridView: 専用 QThreadPool に変更
- [x] ThumbnailGridView: `_ensure_visible_loaded()` による可視範囲優先読み込みに変更（`_start_loading` の全件一括読み込みを廃止）
- [x] 実機確認: フォルダツリー・一覧スクロールの重さ → ユーザ要望に対する改善として実施（別途確認結果を記録）
- [!] 実機確認: 大きいフォルダでの「画像がありません」再発有無 → LRU化後も再発を確認。原因未解決
- [x] `_load_qimage` / `_load_thumb` / `show_image` に診断用ログを追加（`%TEMP%\ImageViewer.log`）
- [ ] ログを元に「画像がありません」不具合の実際の原因を特定し、恒久対応を実施

## 依存関係

- ImageCache の変更と ThumbnailGridView / FolderOnlyModel の変更は互いに独立（並行実装済み）
- ログ追加 → 原因特定・恒久対応（ログがないと次の対応ができない）
