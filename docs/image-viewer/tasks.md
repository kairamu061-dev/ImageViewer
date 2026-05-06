# image-viewer タスク

## 実装タスク一覧

<!-- ステータス: [ ] 未着手 / [~] 進行中 / [x] 完了 -->

### 初期実装
- [x] プロジェクト構成・依存パッケージ定義 (requirements.txt)
- [x] FolderOnlyModel (QFileSystemModel サブクラス)
- [x] FolderTreePanel (QTreeView + folder_selected シグナル)
- [x] ImageCache (QImageReader + QThreadPool プリロード)
- [x] ImageCanvas (QWidget + paintEvent + ズームキャッシュ)
- [x] HoverSlider (下部ホバー表示 JumpSlider)
- [x] ImageViewerPanel (ImageCanvas + HoverSlider 統合)
- [x] MainWindow → AppTabWidget への移行
- [x] フォルダ選択ダイアログ・起動フロー

### enhancements
- [x] ドラッグパン・端クランプ
- [x] スライダーダイレクトジャンプ（JumpSlider）
- [x] 兄弟フォルダ移動
- [x] コンテキストメニュー
- [x] フォルダパネル折りたたみ
- [x] スワップボタン

### tabs
- [x] マルチタブ（AppTabWidget）
- [x] タブタイトル動的更新
- [x] カスタム × ボタン
- [x] お気に入りタブ

### favorites
- [x] FavoritesModel (QStandardItemModel + JSON)
- [x] FavoritesPanel (D&D ツリー)
- [x] FavoritesTab

### persistence
- [x] state_manager.py
- [x] 全状態の保存/復元

### ビルド
- [x] PyInstaller ビルドスクリプト（build.bat / build_dir.bat）
- [x] アイコン設定（app_icon.ico）

## 依存関係

- FolderOnlyModel → FolderTreePanel → TabContent
- ImageCache → ImageCanvas → ImageViewerPanel → TabContent
- HoverSlider → ImageViewerPanel
- JumpSlider → HoverSlider
- FavoritesModel → FavoritesPanel → FavoritesTab
- TabContent + FavoritesTab → AppTabWidget → MainWindow
- AppTabWidget → state_manager → MainWindow
