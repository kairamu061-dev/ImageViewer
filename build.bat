@echo off
echo ========================================
echo  ImageViewer Build (single exe)
echo ========================================
echo.
taskkill /f /im ImageViewer.exe 2>nul
uv run --with pyqt6 --with pyinstaller pyinstaller --onefile --windowed --icon=app_icon.ico --name=ImageViewer --paths=src --add-data "app_icon.ico;." --add-data "app_icon_256.png;." src\main.py
echo.
if exist dist\ImageViewer.exe (
    echo [OK] dist\ImageViewer.exe
) else (
    echo [ERROR] Build failed
)
echo.
pause
