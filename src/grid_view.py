from __future__ import annotations
from pathlib import Path
from PyQt6.QtWidgets import (
    QListWidget, QListWidgetItem, QListView, QAbstractItemView, QStyle,
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QRunnable, QThreadPool, QObject
from PyQt6.QtGui import QPixmap, QIcon, QImageReader

COLUMNS = 5
THUMB_SIZE = 384   # max decode size (px, long side)

_GRID_STYLE = """
    QListWidget {
        background: #1E1E1E;
        border: none;
    }
    QListWidget::item {
        background: #2a2a2a;
        border: 1px solid #3c3c3c;
    }
    QListWidget::item:hover {
        border-color: #888;
    }
    QListWidget::item:selected {
        background: #2a2a2a;
        border: 2px solid #2196F3;
    }
"""


def _load_thumb(path: Path, max_side: int):
    """Decode a downscaled QImage on a worker thread; never holds the full-size image."""
    reader = QImageReader(str(path))
    reader.setAutoTransform(True)
    size = reader.size()
    if size.isValid() and (size.width() > max_side or size.height() > max_side):
        reader.setScaledSize(
            size.scaled(max_side, max_side, Qt.AspectRatioMode.KeepAspectRatio)
        )
    img = reader.read()
    return None if img.isNull() else img


class _ThumbSignals(QObject):
    # Carries QImage; conversion to QPixmap/QIcon happens on the main thread
    done = pyqtSignal(int, int, object)   # generation, index, QImage | None


class _ThumbWorker(QRunnable):
    def __init__(self, generation: int, index: int, path: Path, signals: _ThumbSignals):
        super().__init__()
        self.generation = generation
        self.index = index
        self.path = path
        self.signals = signals
        self.setAutoDelete(True)

    def run(self):
        img = _load_thumb(self.path, THUMB_SIZE)
        self.signals.done.emit(self.generation, self.index, img)


class ThumbnailGridView(QListWidget):
    """Fixed 5-column thumbnail grid with vertical scrolling."""

    image_activated = pyqtSignal(int)   # image index clicked

    def __init__(self, parent=None):
        super().__init__(parent)
        self._generation = 0
        self._images: list[Path] = []
        self._load_pending = False
        self._last_cell = 0
        self._pool = QThreadPool.globalInstance()
        self._signals = _ThumbSignals()
        self._signals.done.connect(self._on_thumb_loaded)

        self.setViewMode(QListView.ViewMode.IconMode)
        self.setResizeMode(QListView.ResizeMode.Adjust)
        self.setMovement(QListView.Movement.Static)
        self.setUniformItemSizes(True)
        self.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        # Always-on so the viewport width (and thus the 5-column layout) never
        # jumps when the scrollbar appears
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOn)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        self.setStyleSheet(_GRID_STYLE)

        self.itemClicked.connect(self._on_item_activated)
        self.itemActivated.connect(self._on_item_activated)   # Enter key

    def set_images(self, images: list[Path]):
        self._generation += 1
        self._images = images
        self.clear()
        cell = self._cell_size()
        for i, path in enumerate(images):
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, i)
            item.setToolTip(path.name)
            item.setSizeHint(QSize(cell, cell))
            self.addItem(item)
        self._update_grid_size()
        # Defer decoding until the grid is actually shown
        self._load_pending = True
        if self.isVisible():
            self._start_loading()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_grid_size()
        if self._load_pending:
            self._start_loading()

    def _start_loading(self):
        self._load_pending = False
        gen = self._generation
        for i, path in enumerate(self._images):
            self._pool.start(_ThumbWorker(gen, i, path, self._signals))

    def select_index(self, index: int):
        if 0 <= index < self.count():
            self.setCurrentRow(index)
            self.scrollToItem(
                self.item(index), QAbstractItemView.ScrollHint.PositionAtCenter
            )

    def _on_thumb_loaded(self, generation: int, index: int, qimage):
        if generation != self._generation:
            return
        item = self.item(index)
        if item is not None and qimage is not None:
            item.setIcon(QIcon(QPixmap.fromImage(qimage)))

    def _on_item_activated(self, item: QListWidgetItem):
        index = item.data(Qt.ItemDataRole.UserRole)
        if index is not None:
            self.image_activated.emit(index)

    def _cell_size(self) -> int:
        # Computed from the widget width instead of the viewport: while the
        # widget is hidden (new tab, stacked page) the viewport does not yet
        # account for the always-on scrollbar, which made 5 columns wrap to 4
        sb = self.style().pixelMetric(QStyle.PixelMetric.PM_ScrollBarExtent, None, self)
        avail = self.width() - 2 * self.frameWidth() - sb - 2
        return max(1, avail // COLUMNS)

    def _update_grid_size(self):
        cell = self._cell_size()
        if cell == self._last_cell:
            return
        self._last_cell = cell
        self.setGridSize(QSize(cell, cell))
        self.setIconSize(QSize(cell - 8, cell - 8))
        # Explicit size hints: without them the item rect is derived from the
        # (initially empty) icon and stays tiny even after thumbnails load
        hint = QSize(cell, cell)
        for i in range(self.count()):
            self.item(i).setSizeHint(hint)

    def _scroll_step(self) -> int:
        # One fifth of a row height per wheel notch / scrollbar arrow click
        cell = self._last_cell or self._cell_size()
        return max(1, cell // 5)

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if delta == 0:
            super().wheelEvent(event)
            return
        sb = self.verticalScrollBar()
        sb.setValue(sb.value() - round(delta / 120.0 * self._scroll_step()))
        event.accept()

    def updateGeometries(self):
        # QListView resets the scrollbar singleStep here; re-apply ours so the
        # arrow buttons match the wheel step
        super().updateGeometries()
        self.verticalScrollBar().setSingleStep(self._scroll_step())

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_grid_size()
