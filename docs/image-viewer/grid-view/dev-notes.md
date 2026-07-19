# grid-view 開発メモ

## 実装上の判断

| 判断内容 | 理由 |
|----------|------|
| QListWidget (IconMode) を採用し独自描画しない | グリッド配置・縦スクロール・選択・クリックが標準機能で揃うため |
| 縦スクロールバーを常時表示 (ScrollBarAlwaysOn) | スクロールバー出現でビューポート幅が変わると5列レイアウトが崩れるため |
| サムネイルのデコードはグリッド初表示まで遅延 | 1枚表示のみ使うユーザのフォルダ切替で全画像デコードが走るのを防ぐため |
| QImageReader.setScaledSize で縮小デコード | 原寸 QImage をメモリに載せない・デコード自体が速くなるため |
| モードは永続化しない（起動時は1枚表示） | 要望になく、既存 state スキーマ変更を避けた。必要なら swap_mode と同様に追加可能 |
| ファイル名はツールチップ表示のみ | セルを画像に最大限使うため |

## 発生した問題と対処

| 問題 | 対処 |
|------|------|
| `add-feature.sh` が CRLF 改行のため Linux 環境で実行エラー | LF に変換した一時コピーで実行した。リポジトリのファイル自体は未修正（要 LF 化 or `.gitattributes`） |
| HoverSlider が QStackedWidget より背面になる | `_reposition_slider()` で `raise_()` するよう変更 |
| サムネイルが米粒サイズで表示される（実機確認で発覚） | アイコン未設定時に QListWidget がアイテムの sizeHint を極小で確定し、uniformItemSizes でそれが全アイテムに固定されるため。各アイテムに `setSizeHint(セルサイズ)` を明示設定して修正。リサイズ時の全件更新はセルサイズ変化時のみ実行 |

## 設計からの変更点

| 変更内容 | 理由 |
|----------|------|
| QStackedLayout → QStackedWidget | 既存の QVBoxLayout にそのまま addWidget でき、変更が最小になるため |

## 今後の課題

- サムネイル読み込みは全件一括キュー。数千枚規模なら可視範囲優先のレイジーロードにしたい
- 表示モードの永続化（state.json への保存）
- グリッド表示中のキーボード操作は QListWidget 標準のみ（Enter で開くのは対応済み）

## ユーザへの要望

- この開発環境（Linux コンテナ）には Python / PyQt6 が無く実行確認ができない。Windows 側で `python src/main.py` を起動し、test-cases.md の I-01〜E-05 の確認をお願いしたい
