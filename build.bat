@echo off
echo ========================================
echo  ImageViewer ビルド
echo ========================================
echo.

uv run --with pyinstaller pyinstaller ^
    --onefile ^
    --windowed ^
    --icon=app_icon.ico ^
    --name=ImageViewer ^
    --paths=src ^
    --add-data "app_icon.ico;." ^
    --add-data "app_icon_256.png;." ^
    src\main.py

echo.
if exist dist\ImageViewer.exe (
    echo [完了] dist\ImageViewer.exe が作成されました
) else (
    echo [エラー] ビルドに失敗しました
)
echo.
pause
