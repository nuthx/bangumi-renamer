import time
import send2trash
import subprocess
import multiprocessing
import cProfile
import pstats
from PySide6.QtWidgets import QMainWindow, QTableWidgetItem, QDialog
from PySide6.QtCore import Qt, QPoint, QThread, QObject, Signal
from qfluentwidgets import MessageBox, InfoBar, InfoBarPosition, RoundMenu, Action, FluentIcon

from src.gui.mainwindow import MainWindow


class MyMainWindow(QMainWindow, MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI(self)
