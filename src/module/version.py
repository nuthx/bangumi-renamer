import re
import requests
import threading

from PySide6.QtCore import QObject, Signal


class Version(QObject):
    has_update = Signal(bool)

    @staticmethod
    def current():
        current_version = "2.1.0"
        return current_version

    @staticmethod
    def latest():
        url = "https://raw.githubusercontent.com/nuthx/bangumi-renamer/main/build-mac.spec"
        response = requests.get(url)
        response_text = response.text.split('\n')

        version_raw = response_text[-3].strip()
        re1 = re.findall(r'\'(.*?)\'', version_raw)
        latest_version = re1[0]

        return latest_version

    def check(self):
        thread = threading.Thread(target=self._thread_check_version)
        thread.start()
        thread.join()

    def _thread_check_version(self):
        current_version = self.current()
        latest_version = self.latest()

        if current_version != latest_version:
            self.has_update.emit(True)
        else:
            self.has_update.emit(False)
