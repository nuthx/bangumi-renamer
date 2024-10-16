import time
import threading
import requests

from PySide6.QtWidgets import QDialog

from src.gui.aboutwindow import AboutWindow


class MyAboutWindow(QDialog, AboutWindow):
    def __init__(self):
        super().__init__()
        self.setupUI(self)
        self.ping()

    def ping(self):
        """
        检查网站是否可访问
        """
        thread1 = threading.Thread(target=self._threadPing, args=("http://anilist.co/", self.anilistPing))
        thread2 = threading.Thread(target=self._threadPing, args=("http://api.bgm.tv/", self.bangumiPing))
        thread1.start()
        thread2.start()

    @staticmethod
    def _threadPing(url, label):
        """
        检查网站是否可访问的子线程
        :param url: 要访问的网址
        :param label: UI上显示结果的Text标签名
        """
        for retry in range(3):
            try:
                if requests.get(url).status_code == 200:
                    label.setText("Online")
                    return
            except requests.ConnectionError:
                pass
            time.sleep(0.1)
        label.setText("Offline")
        label.setStyleSheet("color: #F44336")
