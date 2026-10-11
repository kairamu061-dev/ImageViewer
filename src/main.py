import logging
import sys
import tempfile
from pathlib import Path
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QImageReader
from main_window import MainWindow

# Qt caps a single decoded image at 256 MB by default (a decompression-bomb
# guard). A legit 9600x7200 manga page needs ~264 MB in ARGB32 and was being
# rejected with "Unable to read image data", so full-resolution single-view
# decode failed while the scaled thumbnail decode (under the cap) succeeded.
# Raise the ceiling generously -- this is a local viewer of the user's own
# files -- while still bounding truly absurd allocations. Anything past this
# falls back to image_cache's progressive downscaling.
_IMAGE_ALLOC_LIMIT_MB = 1024

def _resource(filename: str) -> Path:
    """PyInstaller バンドル時は sys._MEIPASS、開発時はリポジトリルートを参照する。"""
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / filename
    return Path(__file__).parent.parent / filename

_ICON_PATH = _resource("app_icon.ico")
LOG_PATH = Path(tempfile.gettempdir()) / "ImageViewer.log"


def _setup_logging():
    logging.basicConfig(
        filename=str(LOG_PATH),
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )


def _initial_path() -> Path | None:
    """First existing non-option CLI arg: the image/folder a file association passed."""
    for arg in sys.argv[1:]:
        if arg.startswith("-"):
            continue
        p = Path(arg)
        if p.exists():
            return p
    return None


def main():
    _setup_logging()
    QImageReader.setAllocationLimit(_IMAGE_ALLOC_LIMIT_MB)
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    if _ICON_PATH.exists():
        app.setWindowIcon(QIcon(str(_ICON_PATH)))
    window = MainWindow(_initial_path())
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
