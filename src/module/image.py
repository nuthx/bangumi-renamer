from PySide6.QtCore import Qt, QRectF
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtWidgets import QLabel


class RoundedLabel(QLabel):
    def __init__(self, imagePath, parent=None):
        super().__init__(parent)
        image = QPixmap(imagePath)
        width = image.width() * 210 / image.height()
        self.setFixedSize(width, 210)
        self.setPixmap(image)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        pixmap = self.pixmap().scaled(
            self.size() * self.devicePixelRatioF(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        radius = 8
        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), radius, radius)
        painter.setClipPath(path)
        painter.drawPixmap(self.rect(), pixmap)
