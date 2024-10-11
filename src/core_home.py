import os
import time
import threading
import shutil
import arrow
import nltk

from PySide6.QtWidgets import QMainWindow, QTableWidgetItem, QListWidgetItem
from PySide6.QtCore import Qt, QUrl, QPoint
from PySide6.QtGui import QDesktopServices
from qfluentwidgets import InfoBar, InfoBarPosition, RoundMenu, Action, FluentIcon

from src.core_about import MyAboutWindow
from src.core_about import MySettingWindow

from src.gui.homewindow import HomeWindow
from src.gui.dialog import NameEditBox

from src.module.log import log
from src.module.list import initList
from src.module.folder import openFolder
from src.module.analysis import Analysis, getFinalName
from src.module.config import posterFolder, readConfig, oldConfigCheck
from src.module.version import Version
from src.module.resource import getResource


class MyHomeWindow(QMainWindow, HomeWindow):
    def __init__(self):
        super().__init__()
        self.setupUI(self)
        self.initConnect()
        self.initList()

        # 检查版本更新
        self.version = Version()
        self.version.has_update.connect(self.checkVersion)
        self.version.check()

        oldConfigCheck()
        self.config = readConfig()
        self.poster_folder = posterFolder()

        self.worker = Analysis()
        self.worker.main_state.connect(self.showState)
        self.worker.anime_state.connect(self.editTableState)
        self.worker.added_progress_count.connect(self.increaseProgress)
        nltk.data.path.append(getResource("lib/nltk_data"))

    def initConnect(self):
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)  # 自定义右键菜单
        self.table.customContextMenuRequested.connect(self.showMenu)
        self.table.itemSelectionChanged.connect(self.selectTable)

        self.searchList.setContextMenuPolicy(Qt.CustomContextMenu)  # 自定义右键菜单
        self.searchList.customContextMenuRequested.connect(self.showMenu2)

        self.newVersionButton.clicked.connect(self.openReleasePage)
        self.aboutButton.clicked.connect(self.openAboutWindow)
        self.settingButton.clicked.connect(self.openSettingWindow)

        self.idEdit.clicked.connect(self.editBgmId)

        self.clearButton.clicked.connect(self.cleanTable)
        self.analysisButton.clicked.connect(self.startAnalysis)
        self.renameButton.clicked.connect(self.startRename)

    def initList(self, clean_all=True):
        if clean_all:
            self.list_id = 0
            self.anime_list = []
            self.table.setRowCount(0)

        self.table.clearContents()
        self.progress.setValue(0)
        self.searchList.clear()
        self.searchList.addItem(QListWidgetItem("暂无搜索结果"))

        self.cnName.setText("暂无动画")
        self.jpName.setText("请先选中一个动画以展示详细信息")
        self.typeLabel.setText("类型：")
        self.dateLabel.setText("放送日期：")
        self.scoreLabel.setText("当前评分：")
        self.fileName.setText("文件名：")
        self.finalName.setText("重命名结果：")
        self.image.updateImage(getResource("src/image/empty.png"))
        self.idLabel.setText("")

    def checkVersion(self, has_update):
        """
        检查是否存在新版本，并在右上角显示下载新版本的按钮
        :param has_update: 是否存在新版本
        """
        if has_update:
            self.newVersionButton.setVisible(True)

    def showState(self, state):
        """
        在程序左下角展示状态文字
        :param state: 待展示的文字
        """
        self.stateLabel.setText(state)

    def editTableState(self, state):
        """
        点击分析后，在表格每一行显示当前动画的分析状态
        :param state: [坐标id, 状态文字]
        """
        list_id, anime_state = state
        self.table.setItem(list_id, 2, QTableWidgetItem(anime_state))

    def showProgressBar(self):
        """
        点击分析后，在左下角显示进度条，同时规定了进度条的最大值
        """
        self.progress.setVisible(True)
        step = 6 if self.config.get("Bangumi", "user_id") else 7  # 如果设置了用户id，则总进度条+1
        self.progress.setMaximum(len(self.anime_list) * step)

    def increaseProgress(self, count):
        """
        调用此函数让左下角的进度+1（或指定数值）
        :param count: 增加的数量
        """
        now_count = self.progress.value()
        self.progress.setValue(now_count + count)

    @staticmethod
    def openReleasePage():
        """
        打开github release页面
        """
        url = QUrl("https://github.com/nuthx/bangumi-renamer/releases/latest")
        QDesktopServices.openUrl(url)

    @staticmethod
    def openAboutWindow():
        """
        打开关于页面
        """
        about = MyAboutWindow()
        about.exec()

    def openSettingWindow(self):
        """
        打开设置页面。若保存了配置，会传递信号执行updateSetting
        """
        setting = MySettingWindow()
        setting.config_saved.connect(self.updateSetting)
        setting.exec()

    def updateSetting(self):
        """
        应用保存的配置内容
        """
        self.showInfo("success", "配置已保存", "配置修改成功")
        self.selectTable()  # 刷新UI展示出的内容
        for anime in self.anime_list:
            getFinalName(anime)  # 刷新所有文件的重命名信息，确保应用了设置中的命名格式

    def editBgmId(self):
        row = self.RowInTable()

        if row is None:
            self.showInfo("warning", "", "请选择要修改的动画")
            return

        if not self.idLabel.text():
            self.showInfo("warning", "", "请输入新的Bangumi ID")
            return
        else:
            id_want = self.idLabel.text()

        if not id_want.isdigit():
            self.showInfo("warning", "", "ID格式不正确")
            return

        if not self.anime_list or "bgm_id" not in self.anime_list[row]:
            id_now = 0
        else:
            id_now = self.anime_list[row]["bgm_id"]

        if str(id_now) == str(id_want):
            self.showInfo("warning", "未修改", "新的ID与当前ID一致")
            return

        self.correctThisAnime(row, id_want, search_init=True)

    def RowInTable(self):
        for selected in self.table.selectedRanges():
            row = selected.topRow()
            return row

    def cleanTable(self):
        if not self.anime_list:
            self.showInfo("warning", "", "列表为空")
        else:
            anime_count = len(self.anime_list)
            self.initList()
            self.showInfo("success", "", "列表已清空")
            log("————")
            log(f"清空了动画列表（{anime_count}个动画）")

    def dragEnterEvent(self, event):
        event.acceptProposedAction()

    def dropEvent(self, event):
        # 获取并格式化本地路径
        raw_list = event.mimeData().urls()
        result = initList(self.list_id, self.anime_list, raw_list)

        self.list_id = result[0]  # 此处的 list_id 已经比实际加了 1
        self.anime_list = result[1]
        log("————")
        log(f"拖入了{len(self.anime_list)}个动画：")
        for anime in self.anime_list:
            log(anime["file_path"])

        self.showInTable()

    def showInTable(self):
        self.table.setRowCount(len(self.anime_list))

        for anime in self.anime_list:
            list_id = anime["list_id"]

            if "list_id" in anime:
                self.table.setItem(list_id, 0, QTableWidgetItem(str(list_id + 1)))

            if "file_name" in anime:
                self.table.setItem(list_id, 1, QTableWidgetItem(anime["file_name"]))

            # 避免没分析完的时候覆盖第三列的进度提示
            if "cn_name" in anime and "final_name" in anime:
                self.table.setItem(list_id, 2, QTableWidgetItem(anime["cn_name"]))

            if "init_name" in anime and "final_name" in anime:
                self.table.setItem(list_id, 3, QTableWidgetItem(anime["init_name"]))

    def startAnalysis(self):
        self.start_time = time.time()

        # 是否存在文件
        if not self.anime_list:
            self.showInfo("warning", "", "请先添加文件夹")
            return

        # 初始化
        # 清空 anime_list 的关键值
        for anime in self.anime_list:
            anime.pop("cn_name", None)
            anime.pop("init_name", None)
            anime.pop("final_name", None)
        self.initList(clean_all=False)
        self.showInTable()
        self.showProgressBar()
        self.clearButton.setEnabled(False)
        self.analysisButton.setEnabled(False)
        self.renameButton.setEnabled(False)
        self.showState("正在分析中，请稍后")
        log("————")
        log("开始分析动画：")

        # 多线程分析
        for anime in self.anime_list:
            thread = threading.Thread(target=self.ThreadStandardAnalysis, args=(anime,))
            thread.start()

        # 检测是否结束并隐藏进度条
        thread = threading.Thread(target=self.ThreadFinishedCheck)
        thread.start()

    def ThreadFinishedCheck(self):
        list_count = len(self.anime_list)
        while True:
            if threading.active_count() == 2:  # 主线程 + 检查线程
                self.progress.setVisible(False)
                self.clearButton.setEnabled(True)
                self.analysisButton.setEnabled(True)
                self.renameButton.setEnabled(True)
                used_time = "{:.1f}".format(time.time() - self.start_time)  # 保留一位小数
                self.showState(f"分析完成，共{list_count}个动画，耗时{used_time}秒")
                log(f"分析完成，共{list_count}个动画，耗时{used_time}秒")
                return
            else:
                time.sleep(0.5)

    def ThreadStandardAnalysis(self, anime):
        # 开始分析
        self.worker.standardAnalysis(anime)

        # 使用 final_name 判断是否分析成功
        if "final_name" not in anime:
            # TODO: 获取失败时进度条增加应>1
            self.table.setItem(anime["list_id"], 3, QTableWidgetItem("==> 动画获取失败（逃"))
            return

        # 重新排序 anime_list 列表，避免串行
        self.anime_list = sorted(self.anime_list, key=lambda x: x["list_id"])

        # 在列表中显示
        self.showInTable()

    def selectTable(self):
        row = self.RowInTable()

        # 应对重命名完成后的 initList 操作
        if row is None or "final_name" not in self.anime_list[row]:
            self.collectionBadge.setVisible(False)
            self.cnName.setText("暂无动画")
            self.jpName.setText("请先选中一个动画以展示详细信息")
            self.typeLabel.setText("类型：")
            self.dateLabel.setText("放送日期：")
            self.scoreLabel.setText("当前评分：")
            self.fileName.setText("文件名：")
            self.finalName.setText("重命名结果：")
            self.image.updateImage(getResource("src/image/empty.png"))
            self.idLabel.setText("")
            self.searchList.clear()
            self.searchList.addItem(QListWidgetItem("暂无搜索结果"))
            return

        this_anime = self.anime_list[row]

        if "collection" in this_anime:
            if this_anime["collection"] != "":
                collection = this_anime["collection"]
                self.collectionBadge.setVisible(True)
                self.collectionBadge.setText(collection)
            else:
                self.collectionBadge.setVisible(False)
        else:
            self.collectionBadge.setVisible(False)

        if "cn_name" in this_anime:
            cn_name = this_anime["cn_name"]
            self.cnName.setText(cn_name)
        else:
            self.cnName.setText("暂无动画")

        if "jp_name" in this_anime:
            jp_name = this_anime["jp_name"]
            self.jpName.setText(jp_name)
        else:
            self.jpName.setText("请先选中一个动画以展示详细信息")

        if "types" in this_anime and "typecode" in this_anime:
            types = this_anime["types"]
            typecode = this_anime["typecode"]
            self.typeLabel.setText(f"类型：{types} ({typecode})")
        else:
            self.typeLabel.setText("类型：")

        if "release" in this_anime:
            release = this_anime["release"]
            release = arrow.get(release).format("YYYY年M月D日")
            self.dateLabel.setText(f"放送日期：{release}")
        else:
            self.dateLabel.setText("放送日期：")

        if "score" in this_anime:
            score = str(this_anime["score"])
            self.scoreLabel.setText(f"当前评分：{score}")
        else:
            self.scoreLabel.setText("当前评分：")

        if "file_name" in this_anime:
            file_name = this_anime["file_name"]
            self.fileName.setText(f"文件名：{file_name}")
        else:
            self.fileName.setText("文件名：")

        if "final_name" in this_anime:
            final_name = this_anime["final_name"].replace("/", " / ")
            self.finalName.setText(f"重命名结果：{final_name}")
        else:
            self.finalName.setText("重命名结果：")

        if "poster" in this_anime:
            poster_name = os.path.basename(this_anime["poster"])
            poster_path = os.path.join(self.poster_folder, poster_name)
            self.image.updateImage(poster_path)
        else:
            self.image.updateImage(getResource("src/image/empty.png"))

        if "bgm_id" in this_anime:
            bgm_id = str(this_anime["bgm_id"])
            self.idLabel.setText(bgm_id)
        else:
            self.idLabel.setText("")

        if "result" in this_anime:
        # if this_anime["result"]:
            self.searchList.clear()
            for this in this_anime["result"]:
                release = arrow.get(this["release"]).format("YY-MM-DD")
                cn_name = this["cn_name"]
                collection = ""
                if "collection" in this:
                    if this["collection"] != "":
                        collection = f" [{this['collection']}]"
                item = f"[{release}]{collection} {cn_name}"
                self.searchList.addItem(QListWidgetItem(item))
        else:
            self.searchList.clear()
            self.searchList.addItem(QListWidgetItem("暂无搜索结果"))
        # else:
        #     self.searchList.clear()
        #     self.searchList.addItem(QListWidgetItem("暂无搜索结果"))

    def showMenu(self, pos):
        edit_init_name = Action(FluentIcon.EDIT, "修改首季动画名")
        view_on_bangumi = Action(FluentIcon.LINK, "在 Bangumi 中查看")
        open_this_folder = Action(FluentIcon.FOLDER, "打开此文件夹")
        open_parent_folder = Action(FluentIcon.FOLDER, "打开上级文件夹")
        delete_this_anime = Action(FluentIcon.DELETE, "删除此动画")

        menu = RoundMenu(parent=self)
        menu.addAction(edit_init_name)
        menu.addSeparator()
        menu.addAction(view_on_bangumi)
        menu.addSeparator()
        menu.addAction(open_this_folder)
        menu.addAction(open_parent_folder)
        menu.addSeparator()
        menu.addAction(delete_this_anime)

        # 必须选中单元格才会显示
        if self.table.itemAt(pos) is not None:
            menu.exec(self.table.mapToGlobal(pos) + QPoint(0, 30), ani=True)  # 在微调菜单位置

            # 不使用RowInTable函数，使用当前pos点位计算行数
            # 目的是避免点击右键时，当前行若未选中，会报错
            # row = self.RowInTable()
            clicked_item = self.table.itemAt(pos)  # 计算坐标
            row = self.table.row(clicked_item)  # 计算行数

            edit_init_name.triggered.connect(lambda: self.editInitName(row))
            view_on_bangumi.triggered.connect(lambda: self.openBgmUrl(row))
            open_this_folder.triggered.connect(lambda: self.openThisFolder(row))
            open_parent_folder.triggered.connect(lambda: self.openParentFolder(row))
            delete_this_anime.triggered.connect(lambda: self.deleteThisAnime(row))

    def editInitName(self, row):
        if "init_name" in self.anime_list[row]:
            init_name = self.anime_list[row]["init_name"]
            w = NameEditBox(self, init_name)
            if w.exec():
                new_init_name = w.nameEdit.text()

                # 是否修改了名称
                if new_init_name == init_name:
                    self.showInfo("warning", "", "首季动画名未修改")
                    return
                else:
                    self.anime_list[row]["init_name"] = new_init_name
                    log("————")
                    log(f"手动修改了首季动画名：{init_name} ==> {new_init_name}")
                    getFinalName(self.anime_list[row])
                    self.showInTable()
                    self.selectTable()

        else:
            self.showInfo("warning", "无法修改", "请先进行动画分析")
            return

    def openBgmUrl(self, row):
        if "bgm_id" in self.anime_list[row]:
            bgm_id = str(self.anime_list[row]["bgm_id"])
            url = QUrl("https://bgm.tv/subject/" + bgm_id)
            QDesktopServices.openUrl(url)
        else:
            self.showInfo("warning", "链接无效", "请先进行动画分析")
            return

    def openThisFolder(self, row):
        path = self.anime_list[row]["file_path"]
        openFolder(path)

    def openParentFolder(self, row):
        this_path = self.anime_list[row]["file_path"]
        parent_path = os.path.dirname(this_path)
        openFolder(parent_path)

    def deleteThisAnime(self, row):
        log("————")
        log(f"删除了动画：{self.anime_list[row]['file_path']}")

        # 删除此行
        self.anime_list.pop(row)

        # 此行后面的 list_id 重新排序
        for i in range(row, len(self.anime_list)):
            self.anime_list[i]["list_id"] -= 1

        # 全局 list_id 减一
        self.list_id -= 1

        self.showInTable()

    def showMenu2(self, pos):
        instead_this_anime = Action(FluentIcon.LABEL, "更正为这个动画")
        view_on_bangumi = Action(FluentIcon.LINK, "在 Bangumi 中查看")

        menu = RoundMenu(parent=self)
        menu.addAction(instead_this_anime)
        menu.addSeparator()
        menu.addAction(view_on_bangumi)

        # 必须选中才会显示
        if self.searchList.itemAt(pos) is not None:
            # 计算子表格行
            clicked_item = self.searchList.itemAt(pos)  # 计算坐标
            list_row = self.searchList.row(clicked_item)  # 计算行数

            # 计算主表格行，不需要考虑选中问题，可直接使用RowInTable函数
            table_row = self.RowInTable()

            # 不出现在默认列表中
            if self.searchList.item(list_row).text() != "暂无搜索结果":
                menu.exec(self.searchList.mapToGlobal(pos), ani=True)

                bgm_id = self.anime_list[table_row]["result"][list_row]["bgm_id"]
                instead_this_anime.triggered.connect(lambda: self.correctThisAnime(table_row, bgm_id))
                view_on_bangumi.triggered.connect(lambda: self.openBgmUrl(table_row))

    def correctThisAnime(self, row, bgm_id, search_init=False):
        anime = self.anime_list[row]

        # 日志
        log("————")
        if search_init:
            log(f"直接通过Bangumi ID: {bgm_id}搜索动画名")
        else:
            log(f"更正当前动画：{anime['cn_name']}")

        # 开始分析
        self.worker.singleAnalysis(anime, bgm_id, search_init)

        # 在列表中显示
        self.showInTable()
        self.selectTable()

        # 日志
        if search_init:
            self.showState(f"搜索完成：{anime['cn_name']}")
            log(f"搜索完成：{anime['cn_name']}")
        else:
            log(f"更正结果：{anime['cn_name']}")

    def startRename(self):
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
        final_name_check = []
        for index, dictionary in enumerate(self.anime_list):
            if "final_name" in dictionary:
                rename_order_list.append(index)
                final_name_check.append(dictionary["final_name"])

        # 检查重命名的结果是否相同
        if len(set(final_name_check)) == 1 and len(final_name_check) != 1:
            self.showInfo("warning", "", "存在重复的重命名结果")
            return

        # 是否有需要命名的动画
        if not rename_order_list:
            self.showInfo("warning", "", "没有可以命名的动画")
            return

        # 开始命名
        log("————")
        log("开始重命名：")
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

            # 排除 Windows 不支持的字符
            final_name_1 = final_name_1.replace("\\", " ").replace("/", " ").replace(":", " ").replace("?", " ").replace("\"", " ")
            final_name_1 = final_name_1.replace("\"", " ").replace("<", " ").replace(">", " ").replace("|", " ")
            final_name_2 = final_name_2.replace("\\", " ").replace("/", " ").replace(":", " ").replace("?", " ").replace("\"", " ")
            final_name_2 = final_name_2.replace("\"", " ").replace("<", " ").replace(">", " ").replace("|", " ")

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

            log(f"重命名：{file_path} ==> {os.path.join(final_path_1, final_name_2)}")

        self.initList()
        self.showInfo("success", "", "重命名完成")
        log("重命名完成")

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
