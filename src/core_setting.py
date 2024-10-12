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
        self.applyButton.clicked.connect(self.saveConfig)  # 保存配置
        self.cancelButton.clicked.connect(lambda: self.close())  # 关闭窗口

    def loadConfig(self):
        self.renameType.setText(readConfig("Format", "rename_format"))
        self.dateType.setText(readConfig("Format", "date_format"))
        self.bgmIdType.setText(readConfig("Bangumi", "user_id"))

    def saveConfig(self):
        # 命名格式检查
        result = str(checkNameFormat(self.renameType.currentText()))
        if result != "True":
            Flyout.create(
                icon=InfoBarIcon.ERROR,
                title="",
                content=result,
                target=self.renameType,
                parent=self,
                isClosable=False
            )
            return

        writeConfig("Format", "rename_format", self.renameType.currentText())
        writeConfig("Format", "date_format", self.dateType.currentText())
        writeConfig("Bangumi", "user_id", self.bgmIdType.text())

        self.config_saved.emit("配置已保存")
        self.close()

    def openPosterFolder(self):
        openFolder(posterFolder())

    def openLogFolder(self):
        openFolder(logFolder())
