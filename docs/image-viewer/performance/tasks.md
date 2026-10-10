# performance タスク

## 実装タスク一覧

- [x] ImageCache: `_cache` を OrderedDict 化し CACHE_LIMIT=60 でLRU破棄
- [x] ImageCache: `get_sync()` に1回リトライを追加
- [x] FolderOnlyModel: 専用 QThreadPool（maxThreadCount=2）に変更
- [x] ThumbnailGridView: 専用 QThreadPool に変更
- [x] ThumbnailGridView: `_ensure_visible_loaded()` による可視範囲優先読み込みに変更（`_start_loading` の全件一括読み込みを廃止）
- [ ] 実機（Windows）での動作確認（大きいフォルダでの「画像がありません」再発有無、フォルダツリー・一覧スクロールの重さ）

## 依存関係

- ImageCache の変更と ThumbnailGridView / FolderOnlyModel の変更は互いに独立（並行実装済み）
