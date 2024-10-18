from PySide6.QtWidgets import QDialog
from PySide6.QtCore import Signal
from qfluentwidgets import Flyout, InfoBarIcon

from src.gui.settingwindow import SettingWindow

from src.module.api.openai import OpenAI
from src.module.config import openFolder, posterFolder, logFolder, checkNameFormat, readConfig, writeConfig


class MySettingWindow(QDialog, SettingWindow):
    config_saved = Signal(str)

    def __init__(self):
        super().__init__()
        self.setupUI(self)
        self.initConnect()
        self.loadConfig()

    def initConnect(self):
        self.posterFolderButton.clicked.connect(lambda: openFolder(posterFolder()))
        self.logFolderButton.clicked.connect(lambda: openFolder(logFolder()))
        self.ai_setting.test.clicked.connect(self.testConnect)
        self.applyButton.clicked.connect(self.saveConfig)
        self.cancelButton.clicked.connect(lambda: self.close())

    def loadConfig(self):
        """
        在UI中加载保存的配置项
        """
        self.renameType.setText(readConfig("Format", "rename_format"))
        self.dateType.setText(readConfig("Format", "date_format"))

        self.ai_setting.usage.setCurrentIndex(int(readConfig("AI", "usage")))
        self.ai_setting.url.setText(readConfig("AI", "url"))
        self.ai_setting.token.setText(readConfig("AI", "token"))
        self.ai_setting.model.setText(readConfig("AI", "model"))

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

            writeConfig("AI", "usage", str(self.ai_setting.usage.currentIndex()))
            writeConfig("AI", "url", self.ai_setting.url.text())
            writeConfig("AI", "token", self.ai_setting.token.text())
            writeConfig("AI", "model", self.ai_setting.model.text())

            self.config_saved.emit("配置已保存")
            self.close()

    def testConnect(self):
        url = self.ai_setting.url.text()
        token = self.ai_setting.token.text()
        model = self.ai_setting.model.text()

        if not url or not token or not model:
            print("请完整填写服务器信息")
        elif not (url.startswith("http://") or url.startswith("https://")):
            print("服务器地址需以 http:// 或 https:// 开头")
        else:
            OpenAI().test(url, token, model)

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
