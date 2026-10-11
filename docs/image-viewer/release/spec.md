# release 仕様

## 機能一覧

| # | 機能名 | 説明 |
|---|--------|------|
| 1 | インストーラー生成 | `installer.iss`（Inno Setup 6）でユーザー単位インストーラーを生成 |
| 2 | 一括ビルドバッチ | `build-installer.bat` が onedir ビルド → ISCC コンパイルまで実行 |
| 3 | スタートメニュー/デスクトップ | スタートメニューにショートカット。デスクトップは任意（既定オフ） |
| 4 | アンインストーラ | 「プログラムの追加と削除」に登録。関連付けレジストリも削除 |
| 5 | 画像ファイル関連付け（任意） | 対応拡張子の「プログラムから開く」に画像ビューアーを追加（既定を奪わない） |
| 6 | 起動時引数でファイルを開く | 引数に画像/フォルダが渡されたら、その親フォルダを開きその画像を初期表示 |

## インストーラー挙動

- **形式**: ユーザー単位（`PrivilegesRequired=lowest`）。管理者権限・UACプロンプト不要
- **インストール先**: `{autopf}\ImageViewer`（権限lowestのため実体は `%LocalAppData%\Programs\ImageViewer`）
- **同梱物**: PyInstaller `--onedir` の出力一式（`ImageViewer.exe` と `_internal\`）
- **言語**: 日本語（`compiler:Languages\Japanese.isl`）
- **AppId**: 固定GUID（アップグレード時に重複せず上書きされるよう固定）
- **出力**: `dist\ImageViewer-Setup-<version>.exe`

## 画像ファイル関連付け（タスク「associate」有効時のみ）

- ProgID `ImageViewer.Image` を登録（`shell\open\command = "...ImageViewer.exe" "%1"`）
- 対応拡張子（`.jpg .jpeg .png .bmp .gif .webp .tiff .tif`）の `OpenWithProgids` に ProgID を追加
- 既定ハンドラの強制変更はしない（Windows仕様で不可。「プログラムから開く」候補・既定のアプリ画面に出るのみ）
- アンインストール時にこれらのレジストリを削除

## 起動時引数の扱い（アプリ側）

- `main.py._initial_path()` が最初の「存在する非オプション引数」を取得
- `MainWindow(initial_path)`:
  - ファイルなら `add_new_tab(path.parent, initial_image=path)` でその画像を表示
  - フォルダなら `add_new_tab(path)`
  - いずれでもない場合は通常どおり前回セッションを復元
- **引数起動時は前回セッションを保存しない**（`_persist_on_close=False`）。単発の「この画像を開く」起動で、保存済みのタブ構成を上書きしないため

## エラーケース

| 条件 | 挙動 |
|------|------|
| Inno Setup 未インストールでビルド | `build-installer.bat` がエラー表示し中断（ダウンロードURLを案内） |
| 関連付け拡張子だが実体が無い/読めないファイルを渡して起動 | 存在しなければ通常起動（セッション復元）にフォールバック |
| 未署名exeのため SmartScreen 警告 | 「詳細情報」→「実行」で起動可（コード署名は本スコープ外） |

## 未対応ケース

- 既定アプリへの強制設定、自動アップデート、コード署名、Win以外のパッケージング
