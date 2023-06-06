import os
import arrow
from PySide6 import QtCore, QtGui, QtWidgets

from module import function


class MyWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bangumi Renamer")
        self.resize(1000, -1)
        # self.setFixedSize(self.size())  # 禁止拉伸窗口
        self.setAcceptDrops(True)
        self.setup_ui()

        self.anime_list = []        # 动画列表，存入所有数据
        self.file_path_exist = []   # 动画路径列表（仅用于对比是否存在相同项目）
        self.list_id = 1            # ID 计数器

    def setup_ui(self) -> None:
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

        # image_url = "https://lain.bgm.tv/pic/cover/l/98/5e/386809_1yR81.jpg"
        # image_data = requests.get(image_url).content
        # self.image = QtGui.QPixmap().scaled(142, 205)
        # self.image.loadFromData(image_data)

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

        self.label_layout = QtWidgets.QVBoxLayout(self)       # 创建子布局
        self.label_container = QtWidgets.QWidget()            # 创建子布局控件
        self.label_container.setLayout(self.label_layout)       # 添加内容到子布局
        self.label_layout.addWidget(self.info_jp_name)
        self.label_layout.addWidget(self.info_cn_name)
        self.label_layout.addWidget(self.b_initial_name)
        self.label_layout.addWidget(self.info_type)
        self.label_layout.addWidget(self.info_release_date)
        self.label_layout.addStretch()
        self.label_layout.addWidget(self.info_file_name)
        self.label_layout.addWidget(self.info_final_name)

        self.info_layout = QtWidgets.QHBoxLayout(self)       # 创建子布局
        self.info_container = QtWidgets.QWidget()            # 创建子布局控件
        self.info_container.setLayout(self.info_layout)       # 添加内容到子布局
        self.info_layout.addWidget(self.image)
        self.info_layout.addWidget(self.label_container)

        self.infobox = QtWidgets.QGroupBox("动画信息", self)
        self.infobox.setFixedHeight(260)
        self.infobox.setLayout(self.info_layout)

        # column1 = QtWidgets.QTreeWidgetItem(["1", "Column 2", "Column 3", "Column 4"])
        # self.tree.addTopLevelItem(column1)
        #
        # self.tree.topLevelItem(1).setText(4, "MainWindow")  # 更改内容

        self.state = QtWidgets.QLabel("等待拖入文件", self)
        self.state.setMinimumWidth(400)
        self.state.setMaximumWidth(4000)

        self.progress = QtWidgets.QProgressBar()

        self.btn_clear = QtWidgets.QPushButton("print", self)
        self.btn_clear.setFixedWidth(100)
        self.btn_clear.clicked.connect(self.print_list)

        self.btn_analysis = QtWidgets.QPushButton("开始识别", self)
        self.btn_analysis.setFixedWidth(100)
        self.btn_analysis.clicked.connect(self.start_analysis)

        self.btn_rename = QtWidgets.QPushButton("重命名", self)
        self.btn_rename.setFixedWidth(100)

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
        self.layout.addWidget(self.tree)
        self.layout.addWidget(self.infobox)
        self.layout.addWidget(self.progress)
        self.layout.addWidget(self.btn_container)
        self.layout.addStretch()

    # 打印列表
    @QtCore.Slot()
    def print_list(self):
        print(f"anime_list: {self.anime_list}")
        print(f"file_path_exist: {self.file_path_exist}")
        self.state.setText(str(self.anime_list))

    # 显示选中动画的详情
    @QtCore.Slot()
    def show_select_list(self, current):
        # 根据选中的行数索引计算 list_id
        select_order = self.tree.indexOfTopLevelItem(current)
        list_id = select_order + 1
        list_count = len(self.anime_list)

        # 选中的行是否已经分析过并写入列表
        if list_id <= list_count:
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

            final_name = self.anime_list[select_order]["file_name"]
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
        # 清空动画列表
        self.anime_list = []

        # 判断路径列表是否为空
        if not self.file_path_exist:
            print("请先拖入文件夹")
        else:
            list_id = 1
            for file_path in self.file_path_exist:

                # 获取循环内单个动画的数据，并写入 anime_list
                this_anime_dict = function.get_anime_info(list_id, file_path)
                self.anime_list.append(this_anime_dict)
                print(self.anime_list)

                # 展示在列表中
                # 如果没有 b_initial_id 说明没执行到最后一步
                if "b_initial_id" in this_anime_dict:
                    list_id = this_anime_dict["list_id"]
                    list_order = list_id - 1
                    file_name = this_anime_dict["file_name"]
                    b_cn_name = this_anime_dict["b_cn_name"]
                    b_initial_name = this_anime_dict["b_initial_name"]

                    self.tree.topLevelItem(list_order).setText(0, str(list_id))
                    self.tree.topLevelItem(list_order).setText(1, file_name)
                    self.tree.topLevelItem(list_order).setText(2, b_cn_name)
                    self.tree.topLevelItem(list_order).setText(3, b_initial_name)
                else:
                    print("该动画未获取到内容，已跳过")

                # 进入下一轮前修改 ID
                list_id += 1

    # 鼠标进入同时，检测对象是否为 URL 并允许拖放
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    # 鼠标松手以后，在 tree 中展示文件路径，并写入 file_path_exist 列表
    def dropEvent(self, event):
        raw_path_list = event.mimeData().urls()
        for raw_path in raw_path_list:
            # 转换原始格式到文件路径
            file_path = raw_path.toLocalFile()

            # 解决 macOS 下路径无法识别
            if file_path.endswith('/'):
                file_path = file_path[:-1]

            # 判断是文件夹还是文件
            if os.path.isdir(file_path):
                file_name = os.path.basename(file_path)
                # 是否存在相同文件夹
                if file_path not in self.file_path_exist:
                    # 写入动画路径列表,用于识别去重
                    self.file_path_exist.append(file_path)

                    # 显示在 tree 中
                    this_column = QtWidgets.QTreeWidgetItem([str(self.list_id), file_name])
                    self.tree.addTopLevelItem(this_column)
                    print(f"新增了{file_name}")

                    self.list_id += 1
                else:
                    print(f"{file_name}已存在")
            else:
                print(f"已过滤文件{file_path}")
