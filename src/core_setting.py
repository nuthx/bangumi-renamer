from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Signal
from qfluentwidgets import Flyout, InfoBarIcon

from src.gui.settingwindow import SettingWindow

from src.module.folder import openFolder
from src.module.config import configFile, posterFolder, logFolder, formatCheck, readConfig


class MySettingWindow(QDialog, SettingWindow):
    save_notice = Signal(str)

    def __init__(self):
        super().__init__()
        self.setupUI(self)
        self.initConnect()
        self.config = readConfig()
        self.loadConfig()

    def initConnect(self):
        self.posterFolderButton.clicked.connect(self.openPosterFolder)
        self.logFolderButton.clicked.connect(self.openLogFolder)
        self.applyButton.clicked.connect(self.saveConfig)  # 保存配置
        self.cancelButton.clicked.connect(lambda: self.close())  # 关闭窗口

    def loadConfig(self):
        self.renameType.setText(self.config.get("Format", "rename_format"))
        self.dateType.setText(self.config.get("Format", "date_format"))
        self.bgmIdType.setText(self.config.get("Bangumi", "user_id"))

    def saveConfig(self):
        # 命名格式检查
        result = str(formatCheck(self.renameType.currentText()))
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

        self.config.set("Format", "rename_format", self.renameType.currentText())
        self.config.set("Format", "date_format", self.dateType.currentText())
        self.config.set("Bangumi", "user_id", self.bgmIdType.text())

        with open(configFile(), "w", encoding="utf-8") as content:
            self.config.write(content)

        self.save_notice.emit("配置已保存")
        self.close()

    def openPosterFolder(self):
        openFolder(posterFolder())

    def openLogFolder(self):
        openFolder(logFolder())
