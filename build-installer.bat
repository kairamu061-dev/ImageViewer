@echo off
echo ========================================
echo  ImageViewer Installer Build
echo ========================================
echo.

echo [1/2] Building app (onedir) with PyInstaller...
taskkill /f /im ImageViewer.exe 2>nul
if exist tools\upx.exe (
    uv run --with pyqt6 --with pyinstaller pyinstaller --onedir --windowed --icon=app_icon.ico --name=ImageViewer --paths=src --add-data "app_icon.ico;." --add-data "app_icon_256.png;." --upx-dir tools src\main.py
) else (
    uv run --with pyqt6 --with pyinstaller pyinstaller --onedir --windowed --icon=app_icon.ico --name=ImageViewer --paths=src --add-data "app_icon.ico;." --add-data "app_icon_256.png;." src\main.py
)
if not exist dist\ImageViewer\ImageViewer.exe (
    echo [ERROR] PyInstaller build failed
    pause
    exit /b 1
)

echo.
echo [2/2] Compiling installer with Inno Setup...
set "ISCC=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=ISCC"
"%ISCC%" installer.iss
if errorlevel 1 (
    echo [ERROR] Installer compile failed. Is Inno Setup 6 installed?
    echo         Download: https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)

echo.
if exist dist\ImageViewer-Setup-*.exe (
    echo [OK] Installer created in dist\
    dir /b dist\ImageViewer-Setup-*.exe
) else (
    echo [ERROR] Installer not found in dist\
)
echo.
pause
