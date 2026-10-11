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

rem Resolve these first -- %ProgramFiles(x86)% contains "(x86)" whose ")"
rem would break a parenthesised for-block if used there directly.
set "PF86=%ProgramFiles(x86)%"
set "PF=%ProgramFiles%"
set "LAP=%LocalAppData%"

set "ISCC="
for %%P in (
    "%PF86%\Inno Setup 6\ISCC.exe"
    "%PF%\Inno Setup 6\ISCC.exe"
    "%LAP%\Programs\Inno Setup 6\ISCC.exe"
    "%PF86%\Inno Setup 5\ISCC.exe"
    "%PF%\Inno Setup 5\ISCC.exe"
) do if not defined ISCC if exist "%%~P" set "ISCC=%%~P"

rem Fall back to ISCC on PATH if none of the usual locations matched.
if not defined ISCC for /f "delims=" %%I in ('where ISCC 2^>nul') do if not defined ISCC set "ISCC=%%I"

if not defined ISCC (
    echo [ERROR] Inno Setup compiler (ISCC.exe) not found.
    echo         Looked in Program Files ^(x86^)\Inno Setup 6, Program Files\Inno Setup 6,
    echo         %%LocalAppData%%\Programs\Inno Setup 6, the v5 equivalents, and PATH.
    echo.
    echo         - If Inno Setup is not installed: https://jrsoftware.org/isdl.php
    echo         - If it is installed elsewhere, set the full path to ISCC.exe here:
    echo               set "ISCC=D:\path\to\ISCC.exe"
    pause
    exit /b 1
)

echo Using: "%ISCC%"
"%ISCC%" installer.iss
if errorlevel 1 (
    echo [ERROR] Installer compile failed (ISCC returned an error).
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
