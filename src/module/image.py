from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtWidgets import QLabel


class roundedLabel(QLabel):
    def __init__(self, imagePath, radius, parent=None):
        super().__init__(parent)
        self.setFixedSize(150, 210)
        self.setPixmap(QPixmap(imagePath))
        self.radius = radius

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        pixmap = self.pixmap().scaled(
            self.size() * self.devicePixelRatioF(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        radius = self.radius
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(self.rect(), pixmap)
