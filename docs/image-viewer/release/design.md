# release 設計

## 技術選定

| 技術 | 用途 | 選定理由 |
|------|------|----------|
| Inno Setup 6 | インストーラー生成 | 無償・日本語対応・スクリプトが読みやすく、ユーザー単位インストールや関連付けを宣言的に書ける。PyInstaller onedir 出力をそのまま同梱できる |
| PyInstaller `--onedir` | 実行ファイル生成 | `--onefile` より起動が速く AV 誤検知も少ない。インストーラーで配るので複数ファイルでも問題ない |
| ユーザー単位インストール（lowest） | 配布形態 | 管理者権限/UAC を避け、導入ハードルを下げる。関連付けも HKCU で完結 |
| `OpenWithProgids` 方式 | ファイル関連付け | 既定ハンドラを奪わず「プログラムから開く」候補に加えるのみ。Windows 10/11 では既定変更をインストーラーから強制できないため、妥当な範囲 |

## 成果物（リポジトリに追加するファイル）

```
installer.iss          # Inno Setup スクリプト（バージョンは #define MyAppVersion）
build-installer.bat    # onedir ビルド → ISCC コンパイルを一括実行
```

## ビルドフロー

```
build-installer.bat
  ├─ [1/2] uv run ... pyinstaller --onedir ...  → dist\ImageViewer\ImageViewer.exe
  │        （失敗なら中断）
  └─ [2/2] ISCC installer.iss                   → dist\ImageViewer-Setup-<ver>.exe
           ISCC は "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" を既定で探し、
           無ければ PATH 上の ISCC にフォールバック
```

## アプリ側（起動時引数）コンポーネント

```
main.py
  ├─ _initial_path(): sys.argv[1:] の最初の「存在する非オプション引数」を Path で返す
  └─ main(): MainWindow(_initial_path())

main_window.py MainWindow(initial_path: Path | None)
  ├─ _persist_on_close = (initial_path is None)
  ├─ initial_path あり → _open_initial_path()、なし → _restore_state()
  ├─ _open_initial_path(): file→add_new_tab(parent, initial_image=path) /
  │                        dir→add_new_tab(path) / それ以外→_restore_state()
  └─ closeEvent(): _persist_on_close のときのみ state を保存

app_tabs.py   add_new_tab(root=None, initial_image=None) → content.set_root(root, initial_image)
tab_content.py set_root(folder, initial_image=None) → viewer.load_folder(folder, initial_image=...)
image_viewer_panel.py load_folder(folder, initial_index=0, initial_image=None):
  ソート済み files から initial_image.name 一致の位置を initial_index に採用
```

## データ構造 / 定数

```python
# main.py
_IMAGE_ALLOC_LIMIT_MB = 1024   # （別機能: 画像確保上限。release とは独立）

# installer.iss
#define MyAppVersion "1.0.0"   # リリースごとに更新する唯一のバージョン定義
#define MyAppProgId "ImageViewer.Image"
AppId = {B2F1C3A4-5D6E-47F8-9A0B-1C2D3E4F5A6B}   # 固定。変更しないこと
```

## 依存関係

| ライブラリ / サービス | 用途 |
|-----------------------|------|
| Inno Setup 6（ビルドマシン） | インストーラーのコンパイル |
| PyInstaller（ビルドマシン） | exe 生成 |
| uv（ビルドマシン） | PyInstaller/PyQt6 の実行環境 |
