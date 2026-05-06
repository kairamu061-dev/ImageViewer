import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon
from main_window import MainWindow

def _resource(filename: str) -> Path:
    """PyInstaller バンドル時は sys._MEIPASS、開発時はリポジトリルートを参照する。"""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / filename
    return Path(__file__).parent.parent / filename

_ICON_PATH = _resource("app_icon.ico")


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    if _ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(_ICON_PATH)))
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
