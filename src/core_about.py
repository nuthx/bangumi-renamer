import time
import threading
import requests

from PySide6.QtWidgets import QDialog

from src.gui.aboutwindow import AboutWindow


class MyAboutWindow(QDialog, AboutWindow):
    def __init__(self):
        super().__init__()
        self.setupUI(self)
        self.checkPing()

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
