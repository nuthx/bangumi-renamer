import os
import re
import arrow
import threading
import shutil
from PySide6 import QtCore, QtGui, QtWidgets

from module import function

version = "1.0"

class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"Bangumi Renamer {version}")
        self.resize(1000, -1)
        # self.setFixedSize(self.size())    # 禁止拉伸窗口
        self.setAcceptDrops(True)
        self.setup_ui()

        self.anime_list = []        # 动画列表，存入所有数据
        self.file_path_exist = []   # 动画路径列表（仅用于对比是否存在相同项目）
        self.list_id = 1            # ID 计数器

    def setup_ui(self) -> None:
        self.type_label = QtWidgets.QLabel("命名格式：", self)
        self.type_input = QtWidgets.QLineEdit(self)
        self.type_how = QtWidgets.QPushButton("格式指南", self)
        self.type_how.setFixedWidth(100)
        self.type_how.clicked.connect(self.show_type_doc)
        self.type_confirm = QtWidgets.QPushButton("检查格式并保存", self)
        self.type_confirm.setFixedWidth(100)
        self.type_confirm.clicked.connect(self.save_config)
        self.load_text()  # 读取配置

        self.type_layout = QtWidgets.QHBoxLayout(self)      # 创建子布局：文本标签
        self.type_container = QtWidgets.QWidget()           # 创建子布局控件
        self.type_container.setLayout(self.type_layout)     # 添加内容到子布局
        self.type_layout.addWidget(self.type_label)
        self.type_layout.addWidget(self.type_input)
        self.type_layout.addWidget(self.type_how)
        self.type_layout.addWidget(self.type_confirm)

        self.tree = QtWidgets.QTreeWidget(self)
        self.tree.setFixedHeight(260)
        self.tree.setColumnCount(5)
        self.tree.setHeaderLabels(["ID", "文件名", "动画名（本季）", "动画名（首季）", "重命名"])
        self.tree.setColumnWidth(0, 25)
        self.tree.setColumnWidth(1, 280)
        self.tree.setColumnWidth(2, 170)
        self.tree.setColumnWidth(3, 170)
        self.tree.setColumnWidth(4, 300)
        self.tree.setRootIsDecorated(False)  # 禁止展开树
        self.tree.currentItemChanged.connect(self.show_select_list)

        self.pixmap = QtGui.QPixmap("img/default.png")
        self.pixmap = self.pixmap.scaledToWidth(142)

        self.image = QtWidgets.QLabel(self)
        self.image.setMinimumSize(142, 205)
        self.image.setMaximumSize(142, 205)
        self.image.setPixmap(self.pixmap)

        self.info_jp_name = QtWidgets.QLabel("动画：", self)
        self.info_jp_name.setMaximumWidth(4000)

        self.info_cn_name = QtWidgets.QLabel("中文名：", self)
        self.info_cn_name.setMaximumWidth(4000)

        self.b_initial_name = QtWidgets.QLabel("动画系列：", self)
        self.b_initial_name.setMaximumWidth(4000)

        self.info_type = QtWidgets.QLabel("动画类型：", self)
        self.info_type.setMaximumWidth(4000)

        self.info_release_date = QtWidgets.QLabel("放送日期：", self)
        self.info_release_date.setMaximumWidth(4000)

        self.info_file_name = QtWidgets.QLabel("文件名：", self)
        self.info_file_name.setMaximumWidth(4000)

        self.info_final_name = QtWidgets.QLabel("重命名结果：", self)
        self.info_final_name.setMaximumWidth(4000)

        self.label_layout = QtWidgets.QVBoxLayout(self)     # 创建子布局：文本标签
        self.label_container = QtWidgets.QWidget()          # 创建子布局控件
        self.label_container.setLayout(self.label_layout)   # 添加内容到子布局
        self.label_layout.addWidget(self.info_jp_name)
        self.label_layout.addWidget(self.info_cn_name)
        self.label_layout.addWidget(self.b_initial_name)
        self.label_layout.addWidget(self.info_type)
        self.label_layout.addWidget(self.info_release_date)
        self.label_layout.addStretch()
        self.label_layout.addWidget(self.info_file_name)
        self.label_layout.addWidget(self.info_final_name)

        self.info_layout = QtWidgets.QHBoxLayout(self)      # 创建子布局：动画信息
        self.info_container = QtWidgets.QWidget()           # 创建子布局控件
        self.info_container.setLayout(self.info_layout)     # 添加内容到子布局
        self.info_layout.addWidget(self.image)
        self.info_layout.addWidget(self.label_container)

        self.infobox = QtWidgets.QGroupBox("动画信息", self)
        self.infobox.setFixedHeight(260)
        self.infobox.setLayout(self.info_layout)

        # self.tree.topLevelItem(1).setText(4, "MainWindow")  # 更改内容

        self.state = QtWidgets.QLabel("请拖入文件夹", self)
        self.state.setMinimumWidth(400)
        self.state.setMaximumWidth(4000)

        self.btn_clear = QtWidgets.QPushButton("清空列表", self)
        self.btn_clear.setFixedWidth(100)
        self.btn_clear.clicked.connect(self.clear_list)

        self.btn_analysis = QtWidgets.QPushButton("开始识别", self)
        self.btn_analysis.setFixedWidth(100)
        self.btn_analysis.clicked.connect(self.start_analysis)

        self.btn_rename = QtWidgets.QPushButton("重命名", self)
        self.btn_rename.setFixedWidth(100)
        self.btn_rename.clicked.connect(self.start_rename)

        self.btn_layout = QtWidgets.QHBoxLayout(self)       # 创建子布局
        self.btn_container = QtWidgets.QWidget()            # 创建子布局控件
        self.btn_container.setLayout(self.btn_layout)       # 添加内容到子布局
        self.btn_layout.addWidget(self.state)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_clear)
        self.btn_layout.addWidget(self.btn_analysis)
        self.btn_layout.addWidget(self.btn_rename)

        # 添加布局
        self.layout = QtWidgets.QVBoxLayout(self)
        self.layout.addWidget(self.type_container)
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.infobox)
        self.layout.addWidget(self.btn_container)
        self.layout.addStretch()

    # 保存配置
    def save_config(self):
        input_text = self.type_input.text()

        # 花括号内容是否合规
        work_type = ["b_id", "romaji_name", "b_jp_name", "b_cn_name", "b_initial_name", "b_type", "b_typecode",
                         "b_release_date", "b_episodes"]
        pattern = r"\{(.*?)\}"
        matches = re.findall(pattern, input_text)
        for match in matches:
            if match not in work_type:
                self.warning_dialog("不支持的格式变量，请检查花括号内容")
                return

        # 花括号是否成对
        if not function.check_braces(input_text):
            self.warning_dialog("花括号结构有误，请检查")
            return

        # 是否有多个斜杠
        if input_text.count("/") > 1:
            self.warning_dialog("最多支持一个父文件夹嵌套")
            return

        # 写入配置
        settings = QtCore.QSettings("config.ini", QtCore.QSettings.IniFormat)
        settings.setValue("type", input_text)
        self.success_dialog("配置已保存<br>请重新分析后再开始重命名")

    # 读取配置
    def load_text(self):
        config_file = QtCore.QFileInfo("config.ini")
        settings = QtCore.QSettings("config.ini", QtCore.QSettings.IniFormat)

        # 如果不存在配置文件，则创建
        if not config_file.exists():
            open(config_file.filePath(), "w").write("")  # 创建配置文件，并写入空内容
            name_type = "{b_initial_name}/[{b_typecode}] [{b_release_date}] {b_jp_name}"  # 默认格式
            settings.setValue("type", name_type)

        input_text = settings.value("type", "")
        self.type_input.setText(str(input_text))

    # 警告对话框
    def warning_dialog(self, message):
        dialog = QtWidgets.QMessageBox(self)
        dialog.setWindowTitle("格式错误")
        dialog.setText(f"命名格式错误：<br>{message}")
        dialog.setIcon(QtWidgets.QMessageBox.Warning)
        dialog.exec()

    # 成功对话框
    def success_dialog(self, message):
        dialog = QtWidgets.QMessageBox(self)
        dialog.setWindowTitle("保存成功")
        dialog.setText(message)
        dialog.setIcon(QtWidgets.QMessageBox.Information)
        dialog.exec()

    # 命名指南对话框
    def show_type_doc(self):
        dialog = QtWidgets.QMessageBox(self)
        dialog.setWindowTitle("格式指南")
        dialog.setText("格式变量请使用花括号 { } 引用<br>"
                       "父文件夹请使用斜杠 / 分割，仅支持单层父文件夹<br><br>"
                       "{b_id}：Bangumi Subject ID<br>"
                       "{romaji_name}：动画罗马名<br>"
                       "{b_jp_name}：动画日文原名<br>"
                       "{b_cn_name}：动画中文译名<br>"
                       "{b_initial_name}：第一季度的中文译名<br>"
                       "{b_type}：动画类型（TV、剧场版、OVA、OAD）<br>"
                       "{b_typecode}：动画类型代码（01：TV、02：剧场版、03：OVA与OAD）<br>"
                       "{b_release_date}：动画放送日期<br>"
                       "{b_episodes}：动画集数（当前季）<br><br>"
                       "注意：完成修改后请重新分析")
        dialog.setIcon(QtWidgets.QMessageBox.Question)
        dialog.exec()

    # 打印列表
    @QtCore.Slot()
    def clear_list(self):
        self.anime_list = []        # 重置动画列表
        self.file_path_exist = []   # 重置动画路径列表
        self.list_id = 1            # 重置 ID 计数器
        self.tree.clear()           # 清空列表
        self.state.setText("内容已清空")

    # 显示选中动画的详情
    @QtCore.Slot()
    def show_select_list(self, current):
        select_order = self.tree.indexOfTopLevelItem(current)
        order_count = len(self.anime_list)

        # 选中了未分析的项目
        if order_count <= select_order:
            self.info_jp_name.setText("动画：")
            self.info_cn_name.setText("中文名：")
            self.b_initial_name.setText("动画系列：")
            self.info_type.setText("动画类型：")
            self.info_release_date.setText("放送日期：")
            self.info_file_name.setText("文件名：")
            self.info_final_name.setText("重命名结果：")
            pixmap = QtGui.QPixmap("img/default.png")
            pixmap = pixmap.scaledToWidth(142)
            self.image.setPixmap(pixmap)
            return

        # 选中行是否存在 b_initial_id 证明分析完成
        if "b_initial_id" in self.anime_list[select_order]:
            b_jp_name = self.anime_list[select_order]["b_jp_name"]
            self.info_jp_name.setText(f"动画：{b_jp_name}")

            b_cn_name = self.anime_list[select_order]["b_cn_name"]
            self.info_cn_name.setText(f"中文名：{b_cn_name}")

            b_initial_name = self.anime_list[select_order]["b_initial_name"]
            self.b_initial_name.setText(f"动画系列：{b_initial_name}")

            b_type = self.anime_list[select_order]["b_type"]
            self.info_type.setText(f"动画类型：{b_type}")

            b_release_date = self.anime_list[select_order]["b_release_date"]
            b_release_date = arrow.get(b_release_date, "YYMMDD")
            b_release_date = b_release_date.format("YYYY年M月D日")
            self.info_release_date.setText(f"放送日期：{b_release_date}")

            file_name = self.anime_list[select_order]["file_name"]
            self.info_file_name.setText(f"文件名：{file_name}")

            final_name = self.anime_list[select_order]["final_name"]
            final_name = final_name.replace("/", " / ")
            self.info_final_name.setText(f"重命名结果：{final_name}")

            b_image_name = self.anime_list[select_order]["b_image_name"]
            pixmap = QtGui.QPixmap(f"img/{b_image_name}")
            pixmap = pixmap.scaledToWidth(142)
            self.image.setPixmap(pixmap)
        else:
            self.info_jp_name.setText("动画：")
            self.info_cn_name.setText("中文名：")
            self.b_initial_name.setText("动画系列：")
            self.info_type.setText("动画类型：")
            self.info_release_date.setText("放送日期：")
            self.info_file_name.setText("文件名：")
            self.info_final_name.setText("重命名结果：")
            pixmap = QtGui.QPixmap("img/default.png")
            pixmap = pixmap.scaledToWidth(142)
            self.image.setPixmap(pixmap)

    # 开始分析
    @QtCore.Slot()
    def start_analysis(self):
        name_type = self.type_input.text()
        # 路径列表是否为空
        if not self.file_path_exist:
            self.state.setText("请先拖入文件夹")
            return

        # 分析过程
        self.anime_list = []  # 重置动画列表
        list_id = 1
        for file_path in self.file_path_exist:
            # 在单独的线程中运行get_anime_info函数
            thread = threading.Thread(target=self.start_analysis_thread, args=(list_id, file_path, name_type))
            thread.start()
            # self.state.setText(f"准备识别{list_id}个动画项目")
            list_id += 1

    # 开始分析线程
    def start_analysis_thread(self, list_id, file_path, name_type):
        # 获取本线程的动画信息，写入 anime_list
        this_anime_dict = function.get_anime_info(list_id, file_path, name_type)
        self.anime_list.append(this_anime_dict)

        # 重新排序 anime_list 列表，避免串行
        self.anime_list = sorted(self.anime_list, key=lambda x: x['list_id'])

        # 展示在列表中
        # 如果没有 b_initial_id 说明没分析完成
        if "b_initial_id" in this_anime_dict:
            list_id = this_anime_dict["list_id"]
            list_order = list_id - 1
            file_name = this_anime_dict["file_name"]
            b_cn_name = this_anime_dict["b_cn_name"]
            b_initial_name = this_anime_dict["b_initial_name"]
            final_name = this_anime_dict["final_name"]

            self.tree.topLevelItem(list_order).setText(0, str(list_id))
            self.tree.topLevelItem(list_order).setText(1, file_name)
            self.tree.topLevelItem(list_order).setText(2, b_cn_name)
            self.tree.topLevelItem(list_order).setText(3, b_initial_name)
            self.tree.topLevelItem(list_order).setText(4, final_name)
        else:
            print("该动画未获取到内容，已跳过")

    # 开始命名
    @QtCore.Slot()
    def start_rename(self):
        # anime_list 是否有数据
        if not self.anime_list:
            print("请先拖入文件或开始分析")
            return

        # 列出有 anime_list 中有 final_name 的索引
        final_name_order = []
        for index, dictionary in enumerate(self.anime_list):
            if "final_name" in dictionary:
                final_name_order.append(index)

        # 如果没有能命名的文件，退出
        if not final_name_order:
            print("当前没有需要重命名的文件夹")
            return
        else:
            print(f"即将重命名下列ID：{final_name_order}")

        # 开始命名
        for order in final_name_order:
            this_anime_dict = self.anime_list[order]

            # 拆分 final_name 的前后文件夹
            final_name = this_anime_dict['final_name']
            if '/' in final_name:
                final_name_list = final_name.split('/')
                final_name_1 = final_name_list[0]
                final_name_2 = final_name_list[1]
                print(final_name_1)
                print(final_name_2)
            else:
                final_name_1 = ""
                final_name_2 = final_name
                print(final_name_2)

            # 更名当前文件夹
            file_path = this_anime_dict['file_path']
            file_dir = os.path.dirname(file_path)
            final_path_2 = os.path.join(file_dir, final_name_2)
            os.rename(file_path, final_path_2)

            # 判断是否有父文件夹，
            if final_name_1 == "":
                return

            # 创建父文件夹
            final_path_1 = os.path.join(file_dir, final_name_1)
            if not os.path.exists(final_path_1):
                os.makedirs(final_path_1)

            # 修改 / 为当前系统下的正确分隔符
            separator = os.path.sep
            final_name = final_name.replace('/', separator)

            # 移动至父文件夹
            final_path = os.path.join(file_dir, final_name)
            shutil.move(final_path_2, final_path)
            b_cn_name = this_anime_dict['b_cn_name']
            print(f"{b_cn_name}重命名成功")

        # 输出结果
        self.state.setText("重命名完成")

    # 鼠标进入，检测是否为 URL 并允许拖放
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    # 鼠标松手，在 tree 中展示文件路径，写入 file_path_exist 路径列表
    def dropEvent(self, event):
        raw_path_list = event.mimeData().urls()
        for raw_path in raw_path_list:
            # 转换原始格式到文件路径
            file_path = raw_path.toLocalFile()

            # 解决 macOS 下路径无法识别
            if file_path.endswith('/'):
                file_path = file_path[:-1]

            # 过滤非文件夹
            if os.path.isdir(file_path):
                # 去重已存在的文件夹
                file_name = os.path.basename(file_path)
                if file_path not in self.file_path_exist:
                    # 写入动画路径列表
                    self.file_path_exist.append(file_path)

                    # 显示在 tree 中
                    this_column = QtWidgets.QTreeWidgetItem([str(self.list_id), file_name])
                    self.tree.addTopLevelItem(this_column)
                    print(f"新增了{file_name}")

                    # 更新数量信息
                    self.state.setText(f"当前有{self.list_id}个动画项目")
                    self.list_id += 1
                else:
                    print(f"{file_name}已存在")
            else:
                print(f"已过滤文件{file_path}")
