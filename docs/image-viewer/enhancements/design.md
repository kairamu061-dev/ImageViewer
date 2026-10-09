# enhancements 設計

## 技術選定

| 技術 | 用途 | 選定理由 |
|------|------|----------|
| JumpSlider (QSlider 継承) | クリックジャンプ | mousePressEvent をオーバーライドするだけで実現 |
| QStyle.sliderValueFromPosition | スライダー値算出 | Qt 標準 API でグルーブ内座標から値を正確に計算 |
| subprocess.Popen(["explorer"]) | エクスプローラー起動 | Windows 標準コマンド |
| QPropertyAnimation | スワップボタンフェード不要 | ボタンは常時表示のためアニメーション不要 |
| 正規表現分割 + Python int 比較（数字部分）/ QCollator.compare（文字部分）のハイブリッド | 自然順ソート | `QCollator.setNumericMode(True)` 単体に数字比較を任せたところ `(C99)`/`(C100)` で逆順になる事例が実機で確認されたため不採用。数字比較は常に正しい `int` 比較に固定し、日本語の読み順比較だけ `QCollator`（`QFileSystemModel` と同じ設定）に委ねることで両方を確実に満たす |

## アーキテクチャ

```
FolderTreePanel
  ├── signals: folder_selected, open_in_new_tab, add_to_favorites
  └── _on_context_menu: メニュー項目ごとに対応シグナルを emit

ImageCanvas
  ├── swap_mode: bool  (ホイール/サイドボタン動作の切り替えフラグ)
  ├── _drag_start / _drag_offset_at_start: ドラッグパン管理
  ├── _clamp_offset(): 画像端クランプ
  └── _apply_zoom(): ズームステップ（ZoomCache 無効化含む）

ImageViewerPanel
  ├── _swap_btn: QPushButton (オーバーレイ)
  ├── get_swap_mode() / set_swap_mode()
  ├── navigate_to_folder シグナル → TabContent._on_navigate
  └── _natural_sort_cmp(a, b): ファイル一覧・兄弟フォルダ一覧の共通比較関数（cmp_to_key で利用）

TabContent
  ├── _toggle_btn: QToolButton (16px 幅、常時表示)
  ├── _stored_folder_width: 折りたたみ前の幅を保存
  └── _update_toggle_btn(): ボタンテキスト `<`/`>` を更新
```

## データ構造

```python
# ドラッグパン
_drag_start: QPoint | None
_drag_offset_at_start: QPoint  # ドラッグ開始時の _offset のコピー

# ズームキャッシュ
_zoom_pixmap: QPixmap | None
_zoom_scale: float  # キャッシュが有効なスケール値

# フォルダパネル折りたたみ
_stored_folder_width: int  # 折りたたみ前の幅（デフォルト 220）
```

## 依存関係

| ライブラリ / サービス | 用途 |
|-----------------------|------|
| PyQt6.QtWidgets.QStyle | sliderValueFromPosition |
| subprocess | エクスプローラー起動 |
| PyQt6.QtCore.QCollator | 自然順ソートの文字部分比較（`QFileSystemModel` と同じ照合エンジン） |
| re / functools.cmp_to_key (標準ライブラリ) | 自然順ソートの数字/文字分割・比較関数のキー化 |
