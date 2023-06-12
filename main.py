import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from module import gui


if __name__ == "__main__":
    app = QApplication([])
    window = gui.MyWidget()

    # 加载图标
    icon = QIcon("image/icon.png")
    window.setWindowIcon(icon)

    # 加载 QSS
    style_file = "style/style_light.qss"
    with open(style_file, "r", encoding="UTF-8") as file:
        style_sheet = file.read()
    window.setStyleSheet(style_sheet)

    window.show()
    sys.exit(app.exec())
