from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Signal
from qfluentwidgets import Flyout, InfoBarIcon

from src.gui.settingwindow import SettingWindow

from src.module.config import openFolder, posterFolder, logFolder, checkNameFormat, readConfig, writeConfig


class MySettingWindow(QDialog, SettingWindow):
    config_saved = Signal(str)

    def __init__(self):
        super().__init__()
        self.setupUI(self)
        self.initConnect()
        self.loadConfig()

    def initConnect(self):
        self.posterFolderButton.clicked.connect(self.openPosterFolder)
        self.logFolderButton.clicked.connect(self.openLogFolder)
        self.applyButton.clicked.connect(self.saveConfig)
        self.cancelButton.clicked.connect(lambda: self.close())

    def loadConfig(self):
        """
        在UI中加载保存的配置项
        """
        self.renameType.setText(readConfig("Format", "rename_format"))
        self.dateType.setText(readConfig("Format", "date_format"))
        self.bgmIdType.setText(readConfig("Bangumi", "user_id"))

    @staticmethod
    def openPosterFolder():
        """
        打开海报文件夹
        """
        openFolder(posterFolder())

    @staticmethod
    def openLogFolder():
        """
        打开日志文件夹
        """
        openFolder(logFolder())

    def saveConfig(self):
        """
        保存配置项
        """
        error = checkNameFormat(self.renameType.currentText())  # 检查"命名格式"的合法性
        if error:
            self.showFlyout(error)
        else:
            writeConfig("Format", "rename_format", self.renameType.currentText())
            writeConfig("Format", "date_format", self.dateType.currentText())
            writeConfig("Bangumi", "user_id", self.bgmIdType.text())
            self.config_saved.emit("配置已保存")
            self.close()

    def showFlyout(self, content):
        """
        显示Flyout通知
        :param content: 内容
        """
        Flyout.create(
            icon=InfoBarIcon.ERROR,
            title="",
            content=content,
            target=self.renameType,
            parent=self,
            isClosable=False
        )
