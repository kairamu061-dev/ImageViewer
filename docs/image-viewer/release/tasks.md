# release タスク

## 実装タスク一覧

- [x] 起動時引数の取得（`main.py._initial_path` / `MainWindow(initial_path)`）
- [x] 引数がファイルならその画像を初期表示（`load_folder` に `initial_image` を追加し全経路へ伝播）
- [x] 引数起動時は前回セッションを保存しない（`_persist_on_close`）
- [x] Inno Setup スクリプト `installer.iss`（ユーザー単位・日本語・スタート/デスクトップ・任意の関連付け）
- [x] 一括ビルドバッチ `build-installer.bat`（onedir → ISCC）
- [ ] 実機（Windows）でビルド確認: `build-installer.bat` → `dist\ImageViewer-Setup-1.0.0.exe` 生成
- [ ] 実機確認: インストール→起動→アンインストール
- [ ] 実機確認: 関連付け有効時、画像を「プログラムから開く」で開けるか

## 依存関係

- 起動時引数対応（アプリ側）→ 関連付け機能（インストーラー側）が意味を持つ前提
- PyInstaller onedir ビルド → ISCC コンパイル（build-installer.bat 内で逐次実行）
