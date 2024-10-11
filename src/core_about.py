import time
import threading
import requests

from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Signal
from qfluentwidgets import Flyout, InfoBarIcon

from src.gui.aboutwindow import AboutWindow
from src.gui.settingwindow import SettingWindow

from src.function import openFolder
from src.module.config import configFile, posterFolder, logFolder, formatCheck, readConfig


class MyAboutWindow(QDialog, AboutWindow):
    def __init__(self):
        super().__init__()
        self.setupUI(self)
        self.checkPing()
        self.config = readConfig()

    def checkPing(self):
        thread1 = threading.Thread(target=self.checkPingThread, args=("anilist.co", self.anilistPing))
        thread2 = threading.Thread(target=self.checkPingThread, args=("api.bgm.tv", self.bangumiPing))
        thread1.start()
        thread2.start()

    def checkPingThread(self, url, label):
        for retry in range(3):
            try:
                response = requests.get(f"http://{url}/")
                if response.status_code == 200:
                    label.setText("Online")
                    return
            except requests.ConnectionError:
                pass
            time.sleep(0.1)
        label.setText("Offline")
        label.setStyleSheet("color: #F44336")


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
