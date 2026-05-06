from __future__ import annotations
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import Qt, pyqtSignal, QPoint, QSize
from PyQt6.QtGui import QPainter, QPixmap, QColor, QFont


class ImageCanvas(QWidget):
    next_requested = pyqtSignal()
    prev_requested = pyqtSignal()
    hover_bottom = pyqtSignal(bool)

    BOTTOM_HOVER_ZONE = 60

    def __init__(self, parent=None):
        super().__init__(parent)
        self._pixmap: QPixmap | None = None
        self._fit_pixmap: QPixmap | None = None
        self._fit_size: QSize = QSize()
        self._zoom_pixmap: QPixmap | None = None
        self._zoom_scale: float = -1.0
        self._scale = 1.0
        self._fit = True
        self._offset = QPoint(0, 0)
        self._in_bottom_zone = False
        self._drag_start: QPoint | None = None
        self._drag_offset_at_start = QPoint(0, 0)
        self.swap_mode = True   # False: wheel=zoom, XBtn=nav; True: wheel=nav, XBtn=zoom
        self.setMouseTracking(True)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setStyleSheet("background: #1E1E1E;")

    def set_pixmap(self, pixmap: QPixmap | None):
        self._pixmap = pixmap
        self._fit = True
        self._fit_pixmap = None
        self._zoom_pixmap = None
        self._zoom_scale = -1.0
        self._offset = QPoint(0, 0)
        self.update()

    def clear(self):
        self._pixmap = None
        self._fit_pixmap = None
        self._zoom_pixmap = None
        self.update()

    def _get_fit_pixmap(self) -> QPixmap | None:
        if self._pixmap is None or self._pixmap.isNull():
            return None
        current_size = QSize(self.width(), self.height())
        if self._fit_pixmap is None or self._fit_size != current_size:
            self._fit_pixmap = self._pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._fit_size = current_size
        return self._fit_pixmap

    def _get_zoom_pixmap(self) -> QPixmap | None:
        if self._pixmap is None or self._pixmap.isNull():
            return None
        if self._zoom_pixmap is None or self._zoom_scale != self._scale:
            w = int(self._pixmap.width() * self._scale)
            h = int(self._pixmap.height() * self._scale)
            self._zoom_pixmap = self._pixmap.scaled(
                w, h,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self._zoom_scale = self._scale
        return self._zoom_pixmap

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor("#1E1E1E"))

        if self._pixmap is None or self._pixmap.isNull():
            painter.setPen(QColor("#666666"))
            font = QFont()
            font.setPointSize(14)
            painter.setFont(font)
            painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, "画像がありません")
            return

        if self._fit:
            scaled = self._get_fit_pixmap()
            if scaled:
                x = (self.width() - scaled.width()) // 2
                y = (self.height() - scaled.height()) // 2
                painter.drawPixmap(x, y, scaled)
        else:
            scaled = self._get_zoom_pixmap()
            if scaled:
                x = (self.width() - scaled.width()) // 2 + self._offset.x()
                y = (self.height() - scaled.height()) // 2 + self._offset.y()
                painter.drawPixmap(x, y, scaled)

    def _clamp_offset(self, offset: QPoint) -> QPoint:
        if self._pixmap is None or self._pixmap.isNull():
            return QPoint(0, 0)
        sw = int(self._pixmap.width() * self._scale)
        sh = int(self._pixmap.height() * self._scale)
        max_x = max(0, (sw - self.width()) // 2)
        max_y = max(0, (sh - self.height()) // 2)
        return QPoint(
            max(-max_x, min(max_x, offset.x())),
            max(-max_y, min(max_y, offset.y())),
        )

    def _apply_zoom(self, factor: float):
        if self._pixmap is None or self._pixmap.isNull():
            return
        if self._fit:
            fw = self.width() / self._pixmap.width()
            fh = self.height() / self._pixmap.height()
            self._scale = min(fw, fh)
            self._fit = False
        self._scale = max(0.05, min(self._scale * factor, 20.0))
        self._zoom_pixmap = None   # invalidate zoom cache on scale change
        self._offset = self._clamp_offset(self._offset)
        self.update()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        if self.swap_mode:
            if delta > 0:
                self.prev_requested.emit()
            else:
                self.next_requested.emit()
        else:
            self._apply_zoom(1.1 if delta > 0 else 0.9)

    def mousePressEvent(self, event):
        btn = event.button()
        if btn == Qt.MouseButton.LeftButton and not self._fit:
            self._drag_start = event.pos()
            self._drag_offset_at_start = QPoint(self._offset)
            self.setCursor(Qt.CursorShape.ClosedHandCursor)
        elif btn == Qt.MouseButton.XButton2:
            if self.swap_mode:
                self._apply_zoom(1.1)
            else:
                self.next_requested.emit()
        elif btn == Qt.MouseButton.XButton1:
            if self.swap_mode:
                self._apply_zoom(0.9)
            else:
                self.prev_requested.emit()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_start = None
            self.setCursor(Qt.CursorShape.ArrowCursor)

    def mouseMoveEvent(self, event):
        if self._drag_start is not None:
            delta = event.pos() - self._drag_start
            self._offset = self._clamp_offset(self._drag_offset_at_start + delta)
            self.update()
            return

        in_zone = event.position().y() >= self.height() - self.BOTTOM_HOVER_ZONE
        if in_zone != self._in_bottom_zone:
            self._in_bottom_zone = in_zone
            self.hover_bottom.emit(in_zone)

    def leaveEvent(self, event):
        self._drag_start = None
        if self._in_bottom_zone:
            self._in_bottom_zone = False
            self.hover_bottom.emit(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._fit_pixmap = None
        self.update()
