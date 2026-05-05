# image-viewer 設計

## 技術選定

| 技術 | 用途 | 選定理由 |
|------|------|----------|
| Python 3.10+ | アプリ本体 | Pillow・PyQt6 との相性・開発速度 |
| PyQt6 | GUI フレームワーク | Windows ネイティブ描画・マウス XButton 対応・QThreadPool |
| Pillow (PIL) | 画像読み込み・リサイズ | 幅広いフォーマット対応、QPixmap への変換が容易 |
| QThreadPool | プリロード | メインスレッドをブロックせず隣接画像を先読み |

## アーキテクチャ

```
main.py
└── MainWindow (QMainWindow)
    ├── MenuBar / ToolBar
    │   └── 「フォルダを開く」アクション
    ├── QSplitter（水平分割）
    │   ├── FolderTreePanel
    │   │   ├── QTreeView
    │   │   └── FolderOnlyModel (QFileSystemModel サブクラス)
    │   │       └── filterAcceptsRow: ディレクトリのみ通す
    │   └── ImageViewerPanel
    │       ├── ImageCanvas (QWidget)
    │       │   └── paintEvent: QPixmap を描画
    │       └── HoverSlider (QSlider)
    │           └── ビューアー下部ホバーで表示/非表示
    └── ImageCache
        ├── current: QPixmap（表示中画像）
        ├── cache: dict[int, QPixmap]（インデックス→QPixmap）
        └── _preload_worker: QRunnable（バックグラウンド先読み）
```

## データ構造

```python
# 現在フォルダの状態
@dataclass
class FolderState:
    folder_path: Path
    image_files: list[Path]   # ソート済み対応画像ファイルリスト
    current_index: int        # 0-based

# キャッシュ
class ImageCache:
    _cache: dict[int, QPixmap]   # index -> pixmap
    _loading: set[int]           # バックグラウンドロード中のインデックス
    PRELOAD_RADIUS = 3           # 前後 3 枚をプリロード
```

## インターフェース

```python
class FolderTreePanel(QWidget):
    folder_selected = Signal(Path)   # フォルダクリック時に emit

class ImageViewerPanel(QWidget):
    def load_folder(self, folder_path: Path) -> None: ...
    def show_image(self, index: int) -> None: ...   # キャッシュから即時描画
    def next_image(self) -> None: ...
    def prev_image(self) -> None: ...

class ImageCanvas(QWidget):
    def set_pixmap(self, pixmap: QPixmap) -> None: ...
    def wheelEvent(self, event): ...          # ズーム
    def mousePressEvent(self, event): ...     # XButton1/2

class HoverSlider(QWidget):
    # ビューアー下部に絶対位置で重ねる
    # QPropertyAnimation でフェードイン/アウト
    index_changed = Signal(int)
    def set_count(self, count: int) -> None: ...
    def set_index(self, index: int) -> None: ...

class ImageCache:
    def get(self, index: int) -> QPixmap | None: ...   # キャッシュヒット時即返却
    def preload(self, center: int, total: int, folder: Path) -> None: ...
    def clear(self) -> None: ...
```

## 高速切り替えの実現方針

1. **フォルダ選択時**: バックグラウンドスレッドで全画像のパスリストを取得し、先頭画像 + 前後 PRELOAD_RADIUS 枚を QRunnable で読み込む
2. **切り替え時**: `cache.get(index)` がヒットすれば paintEvent を即時呼び出し（< 1ms）。ミスの場合はその場で同期読み込み（最悪ケース）
3. **スライダードラッグ時**: valueChanged シグナルをそのまま show_image に接続（デバウンスなし）。キャッシュヒット率で十分な速度が出る

## 依存関係

| ライブラリ / サービス | 用途 |
|-----------------------|------|
| PyQt6 | GUI 全般 |
| Pillow | 画像読み込み・フォーマット変換 |
| Python 標準 pathlib | パス操作 |
| Python 標準 threading | キャッシュのスレッドセーフ操作 |
