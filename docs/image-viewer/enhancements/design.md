# enhancements 設計

## 技術選定

| 技術 | 用途 | 選定理由 |
|------|------|----------|
| JumpSlider (QSlider 継承) | クリックジャンプ | mousePressEvent をオーバーライドするだけで実現 |
| QStyle.sliderValueFromPosition | スライダー値算出 | Qt 標準 API でグルーブ内座標から値を正確に計算 |
| subprocess.Popen(["explorer"]) | エクスプローラー起動 | Windows 標準コマンド |
| QPropertyAnimation | スワップボタンフェード不要 | ボタンは常時表示のためアニメーション不要 |

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
  └── navigate_to_folder シグナル → TabContent._on_navigate

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
