# performance 設計

## 技術選定

| 技術 | 用途 | 選定理由 |
|------|------|----------|
| collections.OrderedDict | ImageCache のLRU実装 | 標準ライブラリのみで `move_to_end` / `popitem(last=False)` によるLRUが簡単に実装できるため |
| 専用 QThreadPool（複数インスタンス） | サブシステムごとのスレッドプール分離 | `QThreadPool.globalInstance()` を全サブシステムで共有していたことが競合の原因だったため、フォルダツリー・一覧表示それぞれに専用プールを持たせて分離 |
| QListView.indexAt() による可視範囲算出 | 一覧表示の可視範囲優先読み込み | グリッドの実際のレイアウト（列数・スクロール位置）をQt自身に問い合わせることで、独自の行/列計算を持たずに正確な可視範囲を得られるため |
| logging（標準ライブラリ）+ ファイル出力 | 「画像がありません」不具合の原因調査 | `console=False`（ウィンドウアプリ）でコンソール出力が見えないため、`%TEMP%\ImageViewer.log` にファイル出力。LRU化で不具合が解決しなかったため、憶測での再修正ではなく実機でのログ採取に切り替えた |
| QTimer.singleShot によるバックオフ付き遅延リトライ | 「画像がありません」不具合の対策 | 実機ログで同一ファイルが連続してデコード失敗することを確認。即時リトライでは短すぎるため、時間を空けて最大4回まで自動再試行する方式に変更 |
| ImageCache 専用プールを完全直列（maxThreadCount=1）に制限 | 「画像がありません」不具合の対策（遅延リトライのみでは2回目の確認でも解消しなかったため追加） | プリロードが前後3枚（最大7件）を既定の並列度（CPUコア数程度）で同時に読みに行っており、低速ドライブでの同時ランダムアクセスがスラッシングを招いていた可能性が高いと判断。ユーザに確認したところ D: は内蔵HDDと判明し、SSDと異なりランダムな同時シークに弱いため、2並列ではなく完全直列を選択 |
| `_load_qimage` に `reader.size()` の先行呼び出しを追加 | 「画像がありません」不具合の対策（直列化・リトライ完走後も解消しなかったため追加） | ユーザから「一覧表示では同じファイルが表示できている」との情報提供を受け、成功する `_load_thumb` と失敗する `_load_qimage` を比較。`read()` の前に `size()` を呼んでいるかどうかが唯一の差分だったため、同様に追加 → 効果なし |
| 問題の性質を「一過性」から「決定的」に認識を修正し、`_load_qimage` にフル解像度のまま`setScaledSize`経路を使うフォールバックを追加 | `size()` 追加後も実機確認で解消せず、ログで毎回同じ結果（100%再現）であることを確認。縮小デコード（`setScaledSize`使用）だけが常に成功することから、縮小デコード経路自体に何らかの耐性があると推定し、画質を落とさず同じ経路を通すフォールバックを追加。合わせて、効果のなかった `get_sync` の即時リトライは削除 → このフォールバックも実機確認で失敗（元サイズ指定=1:1では実際のDCTスケーリングが発生しないため無意味だった） |
| `_load_qimage` のフォールバックを「段階的に本当に縮小するカスケード」に変更 | 1:1指定が無効だったため、実際に縮小が発生する `_FALLBACK_SCALES = (7/8, 1/2, 1/4)` を順に試し、最後に一覧表示と同じ384px（`_LAST_RESORT_MAX_SIDE`、一度も失敗していない設定）まで下げる最終手段を用意。画質劣化は最小限に抑えつつ、理論上必ずどこかの段階で成功することを目指す |

## アーキテクチャ

```
ImageCache
  ├── _pool: QThreadPool(maxThreadCount=1)  ← globalInstance() から変更
  │   （D: が内蔵HDDと判明。プリロードの並列読み込みが同一ドライブへの
  │    ランダムシーク競合を招いていたため、完全直列化して緩和）
  ├── _cache: OrderedDict[int, QPixmap]  (CACHE_LIMIT=60 でLRU)
  ├── _store(index, pixmap): 挿入 + move_to_end + 上限超過分を popitem
  ├── get() / get_sync(): ヒット時に move_to_end
  └── _load_qimage(): 素の read() が失敗したら、_FALLBACK_SCALES
      (7/8→1/2→1/4) の順に本当に縮小した setScaledSize で再試行し、
      それでも失敗したら _LAST_RESORT_MAX_SIDE=384（grid_view と同じ値）
      まで縮小する最終手段を試す

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
  ├── _schedule_retry(index, folder, attempt): _RETRY_DELAYS_MS（500/1500/4000/9000ms、計4回）に従い QTimer.singleShot で遅延実行をスケジュール
  └── _retry_show_image(index, folder, attempt): folder が現在の表示フォルダと一致する限り
      （ページ送りで index が変わっても中断しない）get_sync() を再試行。成功時、表示中の
      index と一致する場合のみキャンバス更新。失敗なら次の attempt を再スケジュール
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
_RETRY_DELAYS_MS = (500, 1500, 4000, 9000)   # 遅延リトライのバックオフ間隔

# image_cache.py
_FALLBACK_SCALES = (7/8, 1/2, 1/4)   # 段階的な縮小フォールバック
_LAST_RESORT_MAX_SIDE = 384          # grid_view.THUMB_SIZE と同じ、最終手段
```

## 依存関係

| ライブラリ / サービス | 用途 |
|-----------------------|------|
| collections.OrderedDict (標準ライブラリ) | ImageCache のLRU |
| PyQt6.QtCore.QThreadPool | サブシステムごとの専用プール |
| PyQt6.QtWidgets.QAbstractItemView.indexAt | 一覧表示の可視範囲算出 |
