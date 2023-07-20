import os
import time
import threading
import shutil
import arrow
from PySide6.QtWidgets import QMainWindow, QTableWidgetItem, QDialog, QListWidgetItem
from PySide6.QtCore import Qt, QUrl, Signal, QPoint, QCoreApplication
from PySide6.QtGui import QDesktopServices
from qfluentwidgets import InfoBar, InfoBarPosition, Flyout, InfoBarIcon, RoundMenu, Action, FluentIcon

from src.gui.mainwindow import MainWindow
from src.gui.about import AboutWindow
from src.gui.setting import SettingWindow

from src.function import initList, addTimes, openFolder
from src.module.analysis import getRomajiName, getApiInfo, downloadPoster, getFinalName
from src.module.config import configFile, posterFolder, formatCheck, readConfig
from src.module.resource import getResource


class MyMainWindow(QMainWindow, MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUI(self)
        self.initUI()
        self.initList()
        addTimes("open_times")
        self.poster_folder = posterFolder()

    def initUI(self):
        self.table.itemSelectionChanged.connect(self.selectTable)
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.table.customContextMenuRequested.connect(self.showMenu)

        self.linkButton.clicked.connect(self.openUrl)

        self.aboutButton.clicked.connect(self.openAbout)
        self.settingButton.clicked.connect(self.openSetting)

        self.newVersionButton.clicked.connect(self.openGithub)
        self.clearButton.clicked.connect(self.cleanTable)
        self.analysisButton.clicked.connect(self.startAnalysis)
        self.renameButton.clicked.connect(self.startRename)

    def initList(self):
        self.list_id = 0
        self.anime_list = []
        self.table.clearContents()
        self.table.setRowCount(0)

        self.cnName.setText("暂无动画")
        self.jpName.setText("请先选中一个动画以展示详细信息")
        self.typeLabel.setText("类型：")
        self.dateLabel.setText("放送日期：")
        self.scoreLabel.setText("当前评分：")
        self.fileName.setText("文件名：")
        self.finalName.setText("重命名结果：")
        self.image.updateImage(getResource("src/image/empty.png"))
        self.searchList.clear()
        self.searchList.addItem(QListWidgetItem("暂无搜索结果"))

    def openAbout(self):
        about = MyAboutWindow()
        about.exec()

    def openSetting(self):
        setting = MySettingWindow()
        setting.save_notice.connect(self.closeSetting)
        setting.exec()

    def closeSetting(self, title):
        self.showInfo("success", title, "请重新开始分析")

    def openGithub(self):
        url = QUrl("https://github.com/nuthx/bangumi-renamer/releases")
        QDesktopServices.openUrl(url)

    def currentLine(self):
        rows = []
        for item in self.table.selectedItems():
            rows.append(item.row())
        if rows:
            this_line = rows[0]
            return this_line
        else:
            return None

    def openUrl(self):
        this_line = self.currentLine()
        if this_line is not None or this_line == 0:
            if "bgm_id" in self.anime_list[this_line]:
                bgm_id = str(self.anime_list[this_line]["bgm_id"])
                url = QUrl("https://bgm.tv/subject/" + bgm_id)
                QDesktopServices.openUrl(url)
            else:
                self.showInfo("warning", "链接无效", "请先尝试分析该动画")
                return
        else:
            self.showInfo("warning", "", "请先选择一个动画")

    def cleanTable(self):
        if not self.anime_list:
            self.showInfo("warning", "", "列表为空")
        else:
            self.initList()
            self.showInfo("success", "", "列表已清空")

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        # 获取并格式化本地路径
        raw_list = event.mimeData().urls()
        result = initList(self.list_id, self.anime_list, raw_list)

        self.list_id = result[0]  # 此处的 list_id 已经比实际加了 1
        self.anime_list = result[1]

        self.showInTable()
        print(f"drop{self.anime_list}")

    def showInTable(self):
        self.table.setRowCount(len(self.anime_list))

        for anime in self.anime_list:
            list_id = anime["list_id"]
            anime_id = str(list_id + 1)

            if "list_id" in anime:
                self.table.setItem(list_id, 0, QTableWidgetItem(anime_id))

            if "file_name" in anime:
                self.table.setItem(list_id, 1, QTableWidgetItem(anime["file_name"]))

            if "cn_name" in anime:
                self.table.setItem(list_id, 2, QTableWidgetItem(anime["cn_name"]))

            if "init_name" in anime:
                self.table.setItem(list_id, 3, QTableWidgetItem(anime["init_name"]))

            if "final_name" in anime:
                self.table.setItem(list_id, 4, QTableWidgetItem(anime["final_name"].replace("/", " / ")))

    def startAnalysis(self):
        # 是否存在文件
        if not self.anime_list:
            self.showInfo("warning", "", "请先添加文件夹")
            return

        # 开始分析
        addTimes("analysis_times")
        start_time = time.time()
        self.spinner.setVisible(True)
        self.clearButton.setEnabled(False)
        self.analysisButton.setEnabled(False)
        self.renameButton.setEnabled(False)

        # 标出分析中
        anime_len = len(self.anime_list)
        for i in range(anime_len):
            self.table.setItem(i, 2, QTableWidgetItem("==> 分析中"))

        # 多线程分析
        for anime in self.anime_list:
            thread = threading.Thread(target=self.analysisThread, args=(anime,))
            thread.start()

            # 等待线程完成，不阻塞 UI 界面
            while thread.is_alive():
                QCoreApplication.processEvents()

        # 分析完成
        self.spinner.setVisible(False)
        self.clearButton.setEnabled(True)
        self.analysisButton.setEnabled(True)
        self.renameButton.setEnabled(True)
        used_time = (time.time() - start_time) * 1000  # 计时结束

        # 计时
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

        # 使用 init_name 判断是否分析成功
        if "init_name" not in anime:
            self.table.setItem(anime["list_id"], 2, QTableWidgetItem("==> 动画获取失败（逃"))
            return

        # 下载图片
        downloadPoster(anime)

        # 获取并写入重命名
        getFinalName(anime)
        print(anime)

        # 重新排序 anime_list 列表，避免串行
        self.anime_list = sorted(self.anime_list, key=lambda x: x["list_id"])

        # 在列表中显示
        self.showInTable()

    def startRename(self):
        start_time = time.time()

        # anime_list 是否有数据
        if not self.anime_list:
            self.showInfo("warning", "", "请先添加动画")
            return

        # 是否开始过分析
        if self.table.item(0, 2) is None:
            self.showInfo("warning", "", "请先开始分析")
            return

        # 列出 anime_list 中有 final_name 的索引
        rename_order_list = []
        for index, dictionary in enumerate(self.anime_list):
            if "final_name" in dictionary:
                rename_order_list.append(index)

        # 是否有需要命名的动画
        if not rename_order_list:
            self.showInfo("warning", "", "没有可以命名的动画")
            return

        # 开始命名
        for order in rename_order_list:
            this_anime = self.anime_list[order]

            # 拆分 final_name 文件夹结构
            final_name = this_anime["final_name"]
            if '/' in final_name:
                final_name_list = final_name.split('/')
                final_name_1 = final_name_list[0]
                final_name_2 = final_name_list[1]
            else:
                final_name_1 = ""
                final_name_2 = final_name

            # 更名当前文件夹
            file_path = this_anime["file_path"]
            file_dir = os.path.dirname(file_path)
            final_path_2 = os.path.join(file_dir, final_name_2)
            os.rename(file_path, final_path_2)

            # 是否有父文件夹
            if final_name_1 == "":
                return

            # 创建父文件夹
            final_path_1 = os.path.join(file_dir, final_name_1)
            if not os.path.exists(final_path_1):
                os.makedirs(final_path_1)

            # 移动至父文件夹
            final_path_1 = os.path.join(file_dir, final_name_1)
            shutil.move(final_path_2, final_path_1)

        self.initList()
        addTimes("rename_times")

        used_time = (time.time() - start_time) * 1000
        if used_time > 1000:
            used_time_s = "{:.2f}".format(used_time / 1000)  # 取 2 位小数
            self.showInfo("success", "重命名完成", f"耗时{used_time_s}s")
        else:
            used_time_ms = "{:.0f}".format(used_time)  # 舍弃小数
            self.showInfo("success", "重命名完成", f"耗时{used_time_ms}ms")

    def selectTable(self):
        this_line = self.currentLine()

        # 应对重命名完成后的 initList 操作
        if this_line is None:
            return

        if "cn_name" in self.anime_list[this_line]:
            cn_name = self.anime_list[this_line]["cn_name"]
            self.cnName.setText(cn_name)
        else:
            self.cnName.setText("暂无动画")

        if "jp_name" in self.anime_list[this_line]:
            jp_name = self.anime_list[this_line]["jp_name"]
            self.jpName.setText(jp_name)
        else:
            self.jpName.setText("请先选中一个动画以展示详细信息")

        if "types" in self.anime_list[this_line] and "typecode" in self.anime_list[this_line]:
            types = self.anime_list[this_line]["types"].upper()
            typecode = self.anime_list[this_line]["typecode"]
            self.typeLabel.setText(f"类型：{types} ({typecode})")
        else:
            self.typeLabel.setText("类型：")

        if "release" in self.anime_list[this_line]:
            release = self.anime_list[this_line]["release"]
            release = arrow.get(release).format("YYYY年M月D日")
            self.dateLabel.setText(f"放送日期：{release}")
        else:
            self.dateLabel.setText("放送日期：")

        if "score" in self.anime_list[this_line]:
            score = str(self.anime_list[this_line]["score"])
            self.scoreLabel.setText(f"当前评分：{score}")
        else:
            self.scoreLabel.setText("当前评分：")

        if "file_name" in self.anime_list[this_line]:
            file_name = self.anime_list[this_line]["file_name"]
            self.fileName.setText(f"文件名：{file_name}")
        else:
            self.fileName.setText("文件名：")

        if "final_name" in self.anime_list[this_line]:
            final_name = self.anime_list[this_line]["final_name"].replace("/", " / ")
            self.finalName.setText(f"重命名：{final_name}")
        else:
            self.finalName.setText("重命名：")

        if "poster" in self.anime_list[this_line]:
            poster_name = os.path.basename(self.anime_list[this_line]["poster"])
            poster_path = os.path.join(self.poster_folder, poster_name)
            self.image.updateImage(poster_path)
        else:
            self.image.updateImage(getResource("src/image/empty.png"))

        if "result" in self.anime_list[this_line]:

            self.searchList.clear()
            for this in self.anime_list[this_line]["result"]:
                release = arrow.get(this['release']).format("YY-MM-DD")
                cn_name = this['cn_name']
                item = f"[{release}] {cn_name}"
                self.searchList.addItem(QListWidgetItem(item))
        else:
            self.searchList.clear()
            self.searchList.addItem(QListWidgetItem("暂无搜索结果"))

    def showMenu(self, pos):
        menu = RoundMenu(parent=self)
        open_this_folder = Action(FluentIcon.FOLDER, "打开此文件夹")
        open_parent_folder = Action(FluentIcon.FOLDER, "打开上级文件夹")
        delete_this_anime = Action(FluentIcon.DELETE, "删除此动画")
        menu.addAction(open_this_folder)
        menu.addAction(open_parent_folder)
        menu.addSeparator()
        menu.addAction(delete_this_anime)

        # 必须选中单元格才会显示
        if self.table.itemAt(pos) is not None:
            # 在微调后的位置显示
            menu.exec(self.table.mapToGlobal(pos) + QPoint(0, 30), ani=True)

            # 计算单元格坐标
            clicked_item = self.table.itemAt(pos)
            row = self.table.row(clicked_item)

            open_this_folder.triggered.connect(lambda: self.openThisFolder(row))
            open_parent_folder.triggered.connect(lambda: self.openParentFolder(row))
            delete_this_anime.triggered.connect(lambda: self.deleteThisAnime(row))

    def openThisFolder(self, row):
        path = self.anime_list[row]["file_path"]
        openFolder(path)

    def openParentFolder(self, row):
        this_path = self.anime_list[row]["file_path"]
        parent_path = os.path.dirname(this_path)
        openFolder(parent_path)

    def deleteThisAnime(self, row):
        # 删除此行
        self.anime_list.pop(row)

        # 此行后面的 list_id 重新排序
        for i in range(row, len(self.anime_list)):
            self.anime_list[i]["list_id"] -= 1

        # 全局 list_id 减一
        self.list_id -= 1

        self.showInTable()

        print(f"after{self.anime_list}")

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
        self.config = readConfig()
        self.loadConfig()

    def loadConfig(self):
        self.openTimes.setText(self.config.get("Counter", "open_times"))
        self.analysisTimes.setText(self.config.get("Counter", "analysis_times"))
        self.renameTimes.setText(self.config.get("Counter", "rename_times"))
        self.anilistApi.setText(self.config.get("Counter", "anilist_api"))
        self.bangumiApi.setText(self.config.get("Counter", "bangumi_api"))


class MySettingWindow(QDialog, SettingWindow):
    save_notice = Signal(str)

    def __init__(self):
        super().__init__()
        self.setupUI(self)
        self.initUI()
        self.config = readConfig()
        self.loadConfig()

    def initUI(self):
        self.applyButton.clicked.connect(self.saveConfig)  # 保存配置
        self.cancelButton.clicked.connect(lambda: self.close())  # 关闭窗口

        self.posterFolderButton.clicked.connect(self.openPosterFolder)

    def loadConfig(self):
        self.renameType.setText(self.config.get("Format", "rename_format"))
        self.dateType.setText(self.config.get("Format", "date_format"))

    def saveConfig(self):
        # 格式检查
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

        with open(configFile(), "w") as content:
            self.config.write(content)

        self.save_notice.emit("配置已保存")
        self.close()

    def openPosterFolder(self):
        poster_folder = posterFolder()
        if poster_folder != "N/A":
            openFolder(poster_folder)
