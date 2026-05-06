from __future__ import annotations
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, pyqtProperty
from PyQt6.QtGui import QPainter, QColor
from jump_slider import JumpSlider


class HoverSlider(QWidget):
    index_changed = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._count = 0
        self._opacity = 0.0

        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.setInterval(500)
        self._hide_timer.timeout.connect(self._fade_out)

        self._slider = JumpSlider(Qt.Orientation.Horizontal, self)
        self._slider.setInvertedAppearance(True)
        self._slider.valueChanged.connect(self._on_value_changed)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 8, 16, 8)
        layout.addWidget(self._slider)

        self.setVisible(False)
        self.setMouseTracking(True)

        self._anim = QPropertyAnimation(self, b"opacity_val")
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)
        self._anim.setDuration(150)
        self._anim.finished.connect(self._on_anim_finished)

        self._apply_style()

    def _apply_style(self):
        self._slider.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 4px;
                background: rgba(255,255,255,0.3);
                border-radius: 2px;
            }
            QSlider::handle:horizontal {
                width: 14px;
                height: 14px;
                margin: -5px 0;
                background: white;
                border-radius: 7px;
            }
            QSlider::sub-page:horizontal {
                background: rgba(255,255,255,0.8);
                border-radius: 2px;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.fillRect(self.rect(), QColor(0, 0, 0, int(160 * self._opacity)))

    @pyqtProperty(float)
    def opacity_val(self) -> float:
        return self._opacity

    @opacity_val.setter
    def opacity_val(self, v: float):
        self._opacity = v
        self.update()

    def set_count(self, count: int):
        self._count = count
        if count > 1:
            self._slider.blockSignals(True)
            self._slider.setMinimum(0)
            self._slider.setMaximum(count - 1)
            self._slider.blockSignals(False)

    def set_index(self, index: int):
        self._slider.blockSignals(True)
        self._slider.setValue(index)
        self._slider.blockSignals(False)

    def _on_value_changed(self, value: int):
        if self._count > 1:
            self.index_changed.emit(value)

    def show_slider(self):
        self._hide_timer.stop()
        self.setVisible(True)
        self._animate_to(1.0)

    def start_hide(self):
        self._hide_timer.start()

    def _fade_out(self):
        self._animate_to(0.0)

    def _animate_to(self, target: float):
        self._anim.stop()
        self._anim.setStartValue(self._opacity)
        self._anim.setEndValue(target)
        self._anim.start()

    def enterEvent(self, event):
        self.show_slider()

    def leaveEvent(self, event):
        self.start_hide()

    def _on_anim_finished(self):
        if self._opacity < 0.01:
            self.setVisible(False)
