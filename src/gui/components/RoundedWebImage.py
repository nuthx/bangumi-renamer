import requests

from PySide6.QtCore import Qt, QRectF, QByteArray
from PySide6.QtGui import QPixmap, QPainter, QPainterPath
from PySide6.QtWidgets import QLabel


# 没有用到此组件，仅做备份
class RoundedWebImage(QLabel):
    def __init__(self, imagePath):
        super().__init__()
        self.radius = 8

        response = requests.get(imagePath)
        image_data = QByteArray(response.content)

        image = QPixmap()
        image.loadFromData(image_data)

        self.setFixedSize(150, 210)
        self.setPixmap(image)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)

        pixmap = self.pixmap().scaled(
            self.size() * self.devicePixelRatioF(), Qt.IgnoreAspectRatio, Qt.SmoothTransformation)

        path = QPainterPath()
        path.addRoundedRect(QRectF(self.rect()), self.radius, self.radius)
        painter.setClipPath(path)
        painter.drawPixmap(self.rect(), pixmap)
