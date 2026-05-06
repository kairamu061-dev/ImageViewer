# persistence 仕様

## 機能一覧

| # | 機能名 | 説明 |
|---|--------|------|
| 1 | 状態保存 | アプリ終了時（closeEvent）に JSON へ書き込み |
| 2 | 状態復元 | 起動時に JSON を読み込み各コンポーネントに適用 |
| 3 | エラー耐性 | 保存/読み込み失敗時は例外を出さずスキップ |

## 保存する状態

```json
{
  "window": { "x": 100, "y": 100, "width": 1200, "height": 800 },
  "active_tab": 0,
  "swap_mode": true,
  "tabs": [
    {
      "root_folder": "C:/photos",
      "selected_folder": "C:/photos/2024",
      "image_index": 3,
      "splitter_sizes": [220, 980],
      "folder_panel_width": 220
    }
  ],
  "favorites_tab_open": false,
  "favorites_splitter": [220, 980],
  "favorites_data": [
    { "kind": "folder", "path": "C:/photos", "name": "photos" }
  ]
}
```

## 復元フロー

1. `state_manager.load()` で JSON 読み込み
2. `AppTabWidget.restore_state(state)` を呼び出し
   - `swap_mode` を `_default_swap_mode` に設定
   - お気に入いデータを `FavoritesModel` に適用
   - 各タブを `add_new_tab()` で生成 → `TabContent.restore_state()` で状態適用
   - お気に入りタブが開いていた場合は再生成
3. `MainWindow` でウィンドウ位置/サイズを復元

## エラーケース

| 条件 | 挙動 |
|------|------|
| 状態ファイルが存在しない | 空のタブ1枚で起動 |
| JSON が壊れている | 空のタブ1枚で起動 |
| 保存先フォルダへの書き込み権限なし | サイレントに失敗（例外は出さない）|
| 復元対象のフォルダが存在しない | そのタブは空の状態で開く |

## 未対応ケース

- ウィンドウ位置が複数モニター環境でモニター外になるケース
- タブの並び順の保存（movable=True でも並び順は保存しない）
