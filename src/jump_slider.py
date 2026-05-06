from __future__ import annotations
from PyQt6.QtWidgets import QSlider, QStyleOptionSlider, QStyle
from PyQt6.QtCore import Qt


class JumpSlider(QSlider):
    """QSlider that jumps directly to the clicked position instead of page-stepping."""

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            opt = QStyleOptionSlider()
            self.initStyleOption(opt)
            handle = self.style().subControlRect(
                QStyle.ComplexControl.CC_Slider, opt,
                QStyle.SubControl.SC_SliderHandle, self,
            )
            if not handle.contains(event.pos()):
                groove = self.style().subControlRect(
                    QStyle.ComplexControl.CC_Slider, opt,
                    QStyle.SubControl.SC_SliderGroove, self,
                )
                if self.orientation() == Qt.Orientation.Horizontal:
                    pos = int(event.position().x()) - groove.left()
                    span = groove.width()
                else:
                    pos = int(event.position().y()) - groove.top()
                    span = groove.height()
                value = QStyle.sliderValueFromPosition(
                    self.minimum(), self.maximum(), pos, span,
                    self.invertedAppearance(),
                )
                self.setValue(value)
                event.accept()
                return
        super().mousePressEvent(event)
