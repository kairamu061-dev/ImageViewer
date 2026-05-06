# favorites 開発メモ

## 実装上の判断

| 判断内容 | 理由 |
|----------|------|
| QStandardItemModel を採用 | カスタム QAbstractItemModel より D&D・ツリー管理の実装コストが大幅に低い |
| FavoritesModel を AppTabWidget が保持 | お気に入いタブが閉じられてもデータを保持し続ける必要があるため |
| トップレベルの重複登録をスキップ | 同一フォルダを誤って二重登録するのを防ぐUX上の配慮 |

## 発生した問題と対処

| 問題 | 対処 |
|------|------|
| ツリーの展開/折りたたみ矢印がダーク背景で不可視 | `_ensure_arrow_paths()` で PNG を動的生成し CSS の `image: url(...)` で適用 |
| 矢印生成関数を folder_tree.py と favorites_panel.py で共有 | `_ensure_arrow_paths` を `folder_tree.py` に定義し `favorites_panel.py` からインポート |

## 今後の課題

- D&D でグループを深くネストした場合の QStandardItemModel の挙動未検証
- 登録フォルダが存在しなくなった場合のビジュアルフィードバックなし
