import sys
from PySide6.QtWidgets import QApplication

from src.core import MyMainWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyMainWindow()
    window.show()
    app.exec()
