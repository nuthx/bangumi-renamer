import sys
from PySide6 import QtGui, QtWidgets

from module import gui


if __name__ == "__main__":
    app = QtWidgets.QApplication([])
    window = gui.MyWidget()
    icon = QtGui.QIcon("icon/icon.png")
    window.setWindowIcon(icon)
    window.show()
    sys.exit(app.exec())
