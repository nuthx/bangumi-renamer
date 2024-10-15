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
from src.core_setting import MySettingWindow

from src.gui.homewindow import HomeWindow
from src.gui.components.FsNameEditDialog import FsNameEditDialog

from src.module.data import createAnimeData
from src.module.analysis import Analysis, getFinal
from src.module.config import openFolder, posterFolder, checkConfigVersion
from src.module.version import Version
from src.module.utils import getResource


class MyHomeWindow(QMainWindow, HomeWindow):
    def __init__(self):
        super().__init__()
        self.setupUI(self)
        self.initConnect()
        self.initData()
        self.initUI()

        # 检查版本更新
        self.version = Version()
        self.version.has_update.connect(self.checkVersion)
        self.version.check()

        # 检查配置文件版本
        checkConfigVersion()

        # 加载动画分析类
        self.analysis = Analysis()
        self.analysis.main_state.connect(self.showState)
        self.analysis.anime_state.connect(self.showStateInTable)
        self.analysis.added_progress_count.connect(self.increaseProgress)
        nltk.data.path.append(getResource("lib/nltk_data"))

    def initConnect(self):
        self.table.setContextMenuPolicy(Qt.CustomContextMenu)  # 自定义右键菜单
        self.table.customContextMenuRequested.connect(self.showMenu)
        self.table.itemSelectionChanged.connect(self.showAnimeInDetail)

        self.searchList.setContextMenuPolicy(Qt.CustomContextMenu)  # 自定义右键菜单
        self.searchList.customContextMenuRequested.connect(self.showMenu2)

        self.newVersionButton.clicked.connect(self.openReleasePage)
        self.aboutButton.clicked.connect(self.openAboutWindow)
        self.settingButton.clicked.connect(self.openSettingWindow)

        self.idEdit.clicked.connect(self.editBangumiID)

        self.clearButton.clicked.connect(self.cleanTable)
        self.analysisButton.clicked.connect(self.startAnalysis)
        self.renameButton.clicked.connect(self.startRename)

    def initData(self):
        """
        清空保存的数据
        """
        self.anime_id = 0  # 重置动画计数器
        self.anime_list = []  # 清空动画列表
        self.table.setRowCount(0)  # 重置表格行数

    def initUI(self):
        """
        初始化UI界面显示的内容
        """
        self.progress.setValue(0)  # 清空进度条
        self.table.clearContents()  # 清空表格
        self.searchList.clear()  # 清空搜索列表
        self.searchList.addItem(QListWidgetItem("暂无搜索结果"))  # 为搜索列表添加默认提示

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

    def showStateInTable(self, state):
        """
        在表格指定列显示当前动画的分析状态
        :param state: [坐标id, 状态文字]
        """
        list_id, anime_state = state
        self.table.setItem(list_id, 2, QTableWidgetItem(anime_state))

    def showProgressBar(self):
        """
        在左下角显示进度条，同时规定了进度条的最大值
        """
        self.progress.setVisible(True)
        self.progress.setMaximum(len(self.anime_list) * 6)

    def increaseProgress(self, count):
        """
        增加左下角的进度条的值
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
        setting.config_saved.connect(self.saveSetting)
        setting.exec()

    def saveSetting(self):
        """
        应用保存的配置内容并刷新相关信息
        """
        # 刷新所有文件的重命名信息，确保应用了设置中的命名格式
        for anime in self.anime_list:
            getFinal(anime)

        self.showToast("success", "", "配置修改成功")
        self.showAnimeInDetail()

    def selectedRowInTable(self) -> int:
        """
        获取表格选中行的行号，若选中多行，则只显示第一行
        :return: 选中行的行号
        """
        for selected in self.table.selectedRanges():
            row = selected.topRow()
            return row

    def cleanTable(self):
        """
        若列表不为空，则调用initList初始化列表
        """
        if not self.anime_list:
            self.showToast("warning", "", "列表为空")
        else:
            self.initData()
            self.initUI()
            self.showToast("success", "", "列表已清空")

    def dragEnterEvent(self, event):
        """
        处理拖动进入事件，以允许拖放操作
        :param event: 拖入的文件
        """
        event.acceptProposedAction()

    def dropEvent(self, event):
        """
        将拖入的文件写入anime_list，并展示在表格
        :param event: 拖入的文件
        """
        file_list = event.mimeData().urls()
        anime_data = createAnimeData(self.anime_id, self.anime_list, file_list)
        self.anime_id, self.anime_list = anime_data
        self.showAnimeInTable()

    def showAnimeInTable(self):
        """
        根据anime_list，在表格中展示所有动画条目
        """
        self.table.setRowCount(len(self.anime_list))

        for anime in self.anime_list:
            self.table.setItem(anime["id"], 0, QTableWidgetItem(str(anime["id"] + 1)))
            self.table.setItem(anime["id"], 1, QTableWidgetItem(anime["file_name"]))

            # 存在final_name确保分析结束
            if anime["final_name"] != "":
                self.table.setItem(anime["id"], 2, QTableWidgetItem(anime["name_cn"]))
                self.table.setItem(anime["id"], 3, QTableWidgetItem(anime["fs_name_cn"]))

    def editBangumiID(self):
        """
        手动指定选中动画的Bangumi ID，并重新分析该动画
        """
        row = self.selectedRowInTable()
        id_current = self.anime_list[row]["bangumi_id"] if row is not None else ""
        id_new = self.idLabel.text()

        if row is None:
            self.showToast("warning", "", "请选择要修改的动画")
        elif not id_new:
            self.showToast("warning", "", "请输入新的Bangumi ID")
        elif id_current == id_new:
            self.showToast("warning", "未修改", "新的ID与当前ID一致")
        else:
            self.startAnalysisByID(row, id_new)

    def startAnalysis(self):
        """
        分析全部动画
        """
        if not self.anime_list:
            self.showToast("warning", "", "请先添加文件夹")
            return

        # 初始化界面
        self.initUI()
        self.showAnimeInTable()
        self.showProgressBar()
        self.clearButton.setEnabled(False)
        self.analysisButton.setEnabled(False)
        self.renameButton.setEnabled(False)
        self.showState("正在分析中，请稍后")

        # 多线程分析
        for anime in self.anime_list:
            thread = threading.Thread(target=self._threadAnalysis, args=(anime,))
            thread.start()

        # 检测是否结束并隐藏进度条(与多线程分析处于同时进行状态)
        thread = threading.Thread(target=self._threadFinishCheck)
        thread.start()

    def startAnalysisByID(self, row, bangumi_id):
        """
        根据bangumi id，强制刷新动画信息
        :param row: 重新分析的动画序号
        :param bangumi_id: 手动指定的bangumi id
        """
        self.analysis.start(self.anime_list[row], bangumi_id)
        self.showState(f"搜索完成：{self.anime_list[row]['name_cn']}")

        # 在列表中显示
        self.showAnimeInTable()
        self.showAnimeInDetail()

    def _threadAnalysis(self, anime):
        """
        创建子线程，分析单个动画
        :param anime: 要分析的动画
        """
        # 开始分析
        self.analysis.start(anime)

        # 通过是否存在final_name值检测分析成功
        if anime["final_name"] == "":
            self.table.setItem(anime["id"], 3, QTableWidgetItem("==> 动画获取失败（逃"))
        else:
            self.showAnimeInTable()

    def _threadFinishCheck(self):
        """
        每0.5秒检测一次线程数量，判断是否分析成功
        """
        list_count = len(self.anime_list)
        while True:
            if threading.active_count() == 2:  # 因为存在主线程 + 检查线程
                self.progress.setVisible(False)
                self.clearButton.setEnabled(True)
                self.analysisButton.setEnabled(True)
                self.renameButton.setEnabled(True)
                self.showState(f"分析完成，共{list_count}个动画")
                return
            else:
                time.sleep(0.5)

    def showAnimeInDetail(self):
        row = self.selectedRowInTable()

        # 应对重命名完成后的 initList 操作
        if row is None or "final_name" not in self.anime_list[row]:
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

        if this_anime["name_cn"] != "":
            name_cn = this_anime["name_cn"]
            self.cnName.setText(name_cn)
        else:
            self.cnName.setText("暂无动画")

        if this_anime["name_jp"] != "":
            name_jp = this_anime["name_jp"]
            self.jpName.setText(name_jp)
        else:
            self.jpName.setText("请先选中一个动画以展示详细信息")

        if this_anime["type"] != "":
            types = this_anime["type"]
            typecode = this_anime["typecode"]
            self.typeLabel.setText(f"类型：{types} ({typecode})")
        else:
            self.typeLabel.setText("类型：")

        if this_anime["release_raw"] != "":
            release = arrow.get(this_anime["release_raw"]).format("YYYY年MM月DD日")
            self.dateLabel.setText(f"放送日期：{release}")
        else:
            self.dateLabel.setText("放送日期：")

        if this_anime["score"] != "":
            score = str(this_anime["score"])
            self.scoreLabel.setText(f"当前评分：{score}")
        else:
            self.scoreLabel.setText("当前评分：")

        if this_anime["file_name"] != "":
            file_name = this_anime["file_name"]
            self.fileName.setText(f"文件名：{file_name}")
        else:
            self.fileName.setText("文件名：")

        if this_anime["final_name"] != "":
            final_name = this_anime["final_name"].replace("/", " / ")
            self.finalName.setText(f"重命名结果：{final_name}")
        else:
            self.finalName.setText("重命名结果：")

        if this_anime["poster"] != "":
            poster_name = os.path.basename(this_anime["poster"])
            poster_path = os.path.join(posterFolder(), poster_name)
            self.image.updateImage(poster_path)
        else:
            self.image.updateImage(getResource("src/image/empty.png"))

        if this_anime["bangumi_id"] != "":
            bgm_id = str(this_anime["bangumi_id"])
            self.idLabel.setText(bgm_id)
        else:
            self.idLabel.setText("")

        print(this_anime)

        if this_anime["fs_detail"] != "":
            self.searchList.clear()
            for this in this_anime["fs_detail"]:
                release = arrow.get(this["release"]).format("YY-MM-DD")
                name_cn = this["nameCN"]
                item = f"[{release}] {name_cn}"
                self.searchList.addItem(QListWidgetItem(item))
        else:
            self.searchList.clear()
            self.searchList.addItem(QListWidgetItem("暂无搜索结果"))

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
            w = FsNameEditDialog(self, init_name)
            if w.exec():
                new_init_name = w.nameEdit.text()

                # 是否修改了名称
                if new_init_name == init_name:
                    self.showToast("warning", "", "首季动画名未修改")
                    return
                else:
                    self.anime_list[row]["init_name"] = new_init_name
                    getFinal(self.anime_list[row])
                    self.showAnimeInTable()
                    self.showAnimeInDetail()

        else:
            self.showToast("warning", "无法修改", "请先进行动画分析")
            return

    def openBgmUrl(self, row):
        if "bgm_id" in self.anime_list[row]:
            bgm_id = str(self.anime_list[row]["bgm_id"])
            url = QUrl("https://bgm.tv/subject/" + bgm_id)
            QDesktopServices.openUrl(url)
        else:
            self.showToast("warning", "链接无效", "请先进行动画分析")
            return

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

        # 此行后面的 anime_id 重新排序
        for i in range(row, len(self.anime_list)):
            self.anime_list[i]["id"] -= 1

        # 全局 anime_id 减一
        self.anime_id -= 1

        self.showAnimeInTable()

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
            table_row = self.selectedRowInTable()

            # 不出现在默认列表中
            if self.searchList.item(list_row).text() != "暂无搜索结果":
                menu.exec(self.searchList.mapToGlobal(pos), ani=True)

                bangumi_id = self.anime_list[table_row]["result"][list_row]["bgm_id"]
                instead_this_anime.triggered.connect(lambda: self.startAnalysisByID(table_row, bangumi_id))
                view_on_bangumi.triggered.connect(lambda: self.openBgmUrl(table_row))

    def startRename(self):
        # anime_list 是否有数据
        if not self.anime_list:
            self.showToast("warning", "", "请先添加动画")
            return

        # 是否开始过分析
        if self.table.item(0, 2) is None:
            self.showToast("warning", "", "请先开始分析")
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
            self.showToast("warning", "", "存在重复的重命名结果")
            return

        # 是否有需要命名的动画
        if not rename_order_list:
            self.showToast("warning", "", "没有可以命名的动画")
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

        print(self.anime_list)
        self.initData()
        self.initUI()
        self.showToast("success", "", "重命名完成")

    def showToast(self, state, title, content):
        """
        显示Toast通知
        :param state: 通知等级
        :param title: 标题
        :param content: 内容
        """
        info_state = {
            "info": InfoBar.info,
            "success": InfoBar.success,
            "warning": InfoBar.warning,
            "error": InfoBar.error
        }

        if state in info_state:
            info_state[state](
                title=title,
                content=content,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            )
