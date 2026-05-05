# image-viewer タスク

## 実装タスク一覧

<!-- ステータス: [ ] 未着手 / [~] 進行中 / [x] 完了 -->

- [x] プロジェクト構成・依存パッケージ定義 (requirements.txt)
- [x] FolderOnlyModel (QFileSystemModel サブクラス)
- [x] FolderTreePanel (QTreeView + folder_selected シグナル)
- [x] ImageCache (プリロード付きキャッシュ)
- [x] ImageCanvas (QWidget + paintEvent + ズーム + マウスサイドボタン)
- [x] HoverSlider (下部ホバー表示 QSlider)
- [x] ImageViewerPanel (ImageCanvas + HoverSlider 統合)
- [x] MainWindow (QSplitter + FolderTreePanel + ImageViewerPanel 統合)
- [x] フォルダ選択ダイアログ・起動フロー
- [x] 動作確認・バグ修正

## 依存関係

- FolderOnlyModel → FolderTreePanel
- ImageCache → ImageCanvas → ImageViewerPanel
- HoverSlider → ImageViewerPanel
- FolderTreePanel + ImageViewerPanel → MainWindow
