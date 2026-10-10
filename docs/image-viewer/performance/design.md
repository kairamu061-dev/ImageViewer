# performance 設計

## 技術選定

| 技術 | 用途 | 選定理由 |
|------|------|----------|
| collections.OrderedDict | ImageCache のLRU実装 | 標準ライブラリのみで `move_to_end` / `popitem(last=False)` によるLRUが簡単に実装できるため |
| 専用 QThreadPool（複数インスタンス） | サブシステムごとのスレッドプール分離 | `QThreadPool.globalInstance()` を全サブシステムで共有していたことが競合の原因だったため、フォルダツリー・一覧表示それぞれに専用プールを持たせて分離 |
| QListView.indexAt() による可視範囲算出 | 一覧表示の可視範囲優先読み込み | グリッドの実際のレイアウト（列数・スクロール位置）をQt自身に問い合わせることで、独自の行/列計算を持たずに正確な可視範囲を得られるため |
| logging（標準ライブラリ）+ ファイル出力 | 「画像がありません」不具合の原因調査 | `console=False`（ウィンドウアプリ）でコンソール出力が見えないため、`%TEMP%\ImageViewer.log` にファイル出力。LRU化で不具合が解決しなかったため、憶測での再修正ではなく実機でのログ採取に切り替えた |
| QTimer.singleShot によるバックオフ付き遅延リトライ | 「画像がありません」不具合の対策 | 実機ログで同一ファイルが約1秒近く連続してデコード失敗することを確認。即時リトライでは短すぎるため、時間を空けて最大3回まで自動再試行する方式に変更 |

## アーキテクチャ

```
ImageCache
  ├── _cache: OrderedDict[int, QPixmap]  (CACHE_LIMIT=60 でLRU)
  ├── _store(index, pixmap): 挿入 + move_to_end + 上限超過分を popitem
  ├── get() / get_sync(): ヒット時に move_to_end
  └── get_sync(): デコード失敗時に1回だけ即時リトライ

FolderOnlyModel
  └── _pool: QThreadPool(maxThreadCount=2)  ← globalInstance() から変更

ThumbnailGridView
  ├── _pool: QThreadPool()  ← globalInstance() から変更
  ├── _dispatched: set[int]  (ディスパッチ済みインデックス、generation ごとにリセット)
  ├── _visible_range(): indexAt() で現在の可視行範囲を算出
  └── _ensure_visible_loaded(): 可視範囲 ± (COLUMNS×PRELOAD_ROWS) 件を未ディスパッチなら読み込み
      呼び出し元: set_images / showEvent / resizeEvent / scrollContentsBy

main.py
  └── _setup_logging(): logging.basicConfig でファイル出力を設定（%TEMP%\ImageViewer.log）

image_cache.py / grid_view.py
  └── _load_qimage() / _load_thumb(): try/except で例外も捕捉し、失敗時は
      reader.errorString() も含めてログ出力（従来は無言で None を返すのみだった）

image_viewer_panel.py
  ├── show_image(): get_sync() が None を返した場合、対象のパスをログ出力し _schedule_retry を起動
  ├── _schedule_retry(index, folder, attempt): _RETRY_DELAYS_MS に従い QTimer.singleShot で遅延実行をスケジュール
  └── _retry_show_image(index, folder, attempt): folder/index が現在の表示と一致する場合のみ
      get_sync() を再試行。成功ならキャンバス更新、失敗なら次の attempt を再スケジュール
```

## データ構造

```python
# image_cache.py
CACHE_LIMIT = 60
_cache: OrderedDict[int, QPixmap]

# grid_view.py
PRELOAD_ROWS = 2   # 可視範囲の前後に追加で読み込む行数
_dispatched: set[int]

# image_viewer_panel.py
_RETRY_DELAYS_MS = (300, 1000, 3000)   # 遅延リトライのバックオフ間隔
```

## 依存関係

| ライブラリ / サービス | 用途 |
|-----------------------|------|
| collections.OrderedDict (標準ライブラリ) | ImageCache のLRU |
| PyQt6.QtCore.QThreadPool | サブシステムごとの専用プール |
| PyQt6.QtWidgets.QAbstractItemView.indexAt | 一覧表示の可視範囲算出 |
