import sys
from PySide6 import QtWidgets

from module import gui


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = gui.MyWidget()
    window.show()
    sys.exit(app.exec())
