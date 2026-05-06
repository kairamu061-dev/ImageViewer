@echo off
echo ========================================
echo  ImageViewer ビルド (フォルダ形式)
echo ========================================
echo.

uv run --with pyinstaller pyinstaller ^
    --onedir ^
    --windowed ^
    --icon=app_icon.ico ^
    --name=ImageViewer ^
    --paths=src ^
    --add-data "app_icon.ico;." ^
    --add-data "app_icon_256.png;." ^
    src\main.py

echo.
if exist dist\ImageViewer\ImageViewer.exe (
    echo [完了] dist\ImageViewer\ImageViewer.exe が作成されました
    echo        起動が速いのでこちらを推奨します
    echo        フォルダごとどこかに置いてexeをショートカット登録してください
) else (
    echo [エラー] ビルドに失敗しました
)
echo.
pause
