# grid-view 設計

## 技術選定

| 技術 | 用途 | 選定理由 |
|------|------|----------|
| QListWidget (IconMode) | サムネイルグリッド | 標準ウィジェットでグリッド配置・縦スクロール・選択・クリックが揃っており、独自描画が不要 |
| QImageReader.setScaledSize | 縮小デコード | 原寸をメモリに載せずデコード段階で縮小でき、高速かつ省メモリ |
| QThreadPool + QRunnable | 非同期読み込み | 既存 ImageCache と同じパターン。世代カウンタでフォルダ切替時の古い結果を破棄 |
| QStackedLayout | 表示モード切替 | canvas / grid の排他表示を最小変更で実現 |

## アーキテクチャ

```
ImageViewerPanel
├── _mode_btn (QPushButton, 左上オーバーレイ)   … 「一覧」⇔「1枚」
├── _swap_btn (既存, 右上オーバーレイ)          … 一覧表示中は hide()
├── QStackedLayout
│   ├── ImageCanvas (既存・1枚表示)
│   └── ThumbnailGridView (新規・一覧表示)
└── HoverSlider (既存・1枚表示のみ有効)

ThumbnailGridView (QListWidget)
└── _ThumbLoader … QThreadPool で縮小デコード → シグナルで QIcon 反映
```

- 新規ファイル `src/grid_view.py` に ThumbnailGridView とローダーを実装
- ImageViewerPanel の `load_folder()` でグリッドにも画像リストを渡す
- モード状態は ImageViewerPanel 内で完結（TabContent / AppTabs は変更不要）

## データ構造

```
ThumbnailGridView
    _images: list[Path]        # 表示対象（ImageViewerPanel と同一リスト）
    _generation: int           # フォルダ切替で increment、古い読込結果を破棄
    COLUMNS = 5                # 固定列数
    THUMB_SIZE = 256           # デコード時の最大辺 px

QListWidgetItem
    Qt.ItemDataRole.UserRole → int (画像 index)
    toolTip → ファイル名
```

## インターフェース

```python
class ThumbnailGridView(QListWidget):
    image_activated = pyqtSignal(int)          # クリックされた画像 index

    def set_images(self, images: list[Path]): ...  # 全件をプレースホルダで登録し非同期読込開始
    def select_index(self, index: int): ...        # 現在画像を選択しスクロール

class ImageViewerPanel:                        # 追加分
    def _on_mode_toggled(self, checked): ...   # スタック切替・ボタン表示制御
    def _on_thumb_activated(self, index): ...  # 1枚表示に戻して show_image(index)
```

## 依存関係

| ライブラリ / サービス | 用途 |
|-----------------------|------|
| PyQt6 (既存) | UI・非同期読み込みすべて。追加依存なし |
