import time
import threading
import platform
import subprocess
from PySide6.QtWidgets import QMainWindow, QTableWidgetItem, QDialog
from PySide6.QtCore import Qt, QPoint, QThread, QObject, Signal
from qfluentwidgets import MessageBox, InfoBar, InfoBarPosition, RoundMenu, Action, FluentIcon

from src.gui.mainwindow import MainWindow
from src.gui.about import AboutWindow
from src.gui.setting import SettingWindow

from src.function import initList
from src.module.analysis import getRomajiName, getApiInfo, getFinalName
from src.module.config import configPath, posterFolder


class MyMainWindow(QMainWindow, MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI(self)
        self.initUI()
        self.initList()

    def initUI(self):
        self.aboutButton.clicked.connect(self.openAbout)
        self.settingButton.clicked.connect(self.openSetting)
        self.clearButton.clicked.connect(self.initList)
        self.analysisButton.clicked.connect(self.startAnalysis)
        # self.renameButton.clicked.connect(self.startRename)

    def initList(self):
        self.list_id = 0
        self.anime_list = []
        self.table.clearContents()
        self.table.setRowCount(0)

    def openAbout(self):
        about = MyAboutWindow()
        about.exec()

    def openSetting(self):
        setting = MySettingWindow()
        setting.exec()

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        # 获取并格式化本地路径
        raw_list = event.mimeData().urls()
        result = initList(self.list_id, self.anime_list, raw_list)

        self.list_id = result[0]  # 此处的 list_id 已经比实际加了 1
        self.anime_list = result[1]

        self.showInTable()

    def showInTable(self):
        self.table.setRowCount(len(self.anime_list))

        for anime in self.anime_list:
            list_id = anime["list_id"]
            anime_id = str(list_id + 1)
            file_name = anime["file_name"]
            self.table.setItem(list_id, 0, QTableWidgetItem(anime_id))
            self.table.setItem(list_id, 1, QTableWidgetItem(file_name))

    def startAnalysis(self):
        start_time = time.time()

        # 是否存在文件
        if not self.anime_list:
            self.showInfo("warning", "", "请先添加文件夹")
            return

        # 多线程分析
        threads = []
        for anime in self.anime_list:
            thread = threading.Thread(target=self.analysisThread, args=(anime,))
            thread.start()
            # threads.append(thread)

        # 等待所有线程执行完毕
        # for thread in threads:
        #     thread.join()

        used_time = (time.time() - start_time) * 1000
        if used_time > 1000:
            used_time_s = "{:.2f}".format(used_time / 1000)  # 取 2 位小数
            self.showInfo("success", "分析完成", f"耗时{used_time_s}s")
        else:
            used_time_ms = "{:.0f}".format(used_time)  # 舍弃小数
            self.showInfo("success", "分析完成", f"耗时{used_time_ms}ms")

    def analysisThread(self, anime):
        # 获取并写入罗马名
        file_name = anime["file_name"]
        romaji_name = getRomajiName(file_name)
        anime["romaji_name"] = romaji_name

        # 获取并写入分析信息
        getApiInfo(anime)

        # 获取并写入重命名
        getFinalName(anime)

        # 重新排序 anime_list 列表，避免串行
        self.anime_list = sorted(self.anime_list, key=lambda x: x["list_id"])

        # 如果没有 jp_name_anilist 说明分析失败
        if "jp_name_anilist" in anime:
            self.table.setItem(anime["list_id"], 2, QTableWidgetItem(anime["cn_name"]))
            self.table.setItem(anime["list_id"], 3, QTableWidgetItem(anime["initial_name"]))
            self.table.setItem(anime["list_id"], 4, QTableWidgetItem(anime["initial_name"]))
        else:
            self.table.setItem(anime["list_id"], 2, QTableWidgetItem("分析失败..."))
















    def showInfo(self, state, title, content):
        info_state = {
            "info": InfoBar.info,
            "success": InfoBar.success,
            "warning": InfoBar.warning,
            "error": InfoBar.error
        }

        if state in info_state:
            info_state[state](
                title=title, content=content,
                orient=Qt.Horizontal, isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000, parent=self
            )


class MyAboutWindow(QDialog, AboutWindow):
    def __init__(self):
        super().__init__()
        self.setupUI(self)


class MySettingWindow(QDialog, SettingWindow):
    def __init__(self):
        super().__init__()
        self.setupUI(self)
        self.initUI()

    def initUI(self):
        self.posterFolderButton.clicked.connect(self.openPosterFolder)

    def openPosterFolder(self):
        poster_folder = posterFolder()
        if poster_folder != "N/A":
            if platform.system() == "Windows":
                subprocess.call(["explorer", poster_folder])
            elif platform.system() == "Darwin":
                subprocess.call(["open", poster_folder])
            elif platform.system() == "Linux":
                subprocess.call(["xdg-open", poster_folder])











