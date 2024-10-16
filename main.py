import sys
from PySide6.QtWidgets import QApplication

from src.core_home import MyHomeWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MyHomeWindow()
    window.show()
    app.exec()
