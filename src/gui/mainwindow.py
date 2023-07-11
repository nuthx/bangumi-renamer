from PySide6.QtCore import QMetaObject
from PySide6.QtGui import QFontDatabase, QFont, QIcon
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QAbstractItemView
from qfluentwidgets import setThemeColor, PushButton, ToolButton, TableWidget, PrimaryPushButton, FluentIcon
from qfluentwidgets.common.style_sheet import styleSheetManager

from src.module.resource import getResource
from src.module.image import RoundedLabel


class MainWindow(object):
    def setupUI(self, this_window):
        # 配置主题色与字体
        setThemeColor("#F09199")
        font_id = QFontDatabase.addApplicationFont(getResource("src/font/Study-Bold.otf"))
        font_family = QFontDatabase.applicationFontFamilies(font_id)

        # 加载 QSS
        with open(getResource("src/style/style_light.qss"), "r", encoding="UTF-8") as file:
            style_sheet = file.read()
        this_window.setStyleSheet(style_sheet)

        this_window.setWindowTitle("BangumiRenamer")
        this_window.setWindowIcon(QIcon(getResource("image/icon.png")))
        this_window.resize(1100, 720)
        this_window.setAcceptDrops(True)

        # 标题区域

        self.titleLabel = QLabel("BangumiRenamer")
        self.titleLabel.setObjectName("titleLabel")
        self.titleLabel.setFont(QFont(font_family))

        self.subtitleLabel = QLabel("略微先进的动画文件夹重命名工具")
        self.subtitleLabel.setObjectName('subtitleLabel')

        self.titleLayout = QVBoxLayout()
        self.titleLayout.setContentsMargins(0, 0, 0, 0)
        self.titleLayout.addWidget(self.titleLabel)
        self.titleLayout.addSpacing(4)
        self.titleLayout.addWidget(self.subtitleLabel)

        self.aboutButton = ToolButton(FluentIcon.INFO, self)
        self.settingButton = PushButton("设置", self, FluentIcon.SETTING)

        self.headerLayout = QHBoxLayout()
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLayout.addLayout(self.titleLayout)
        self.headerLayout.addStretch(0)
        self.headerLayout.addWidget(self.aboutButton, 0)
        self.headerLayout.addSpacing(12)
        self.headerLayout.addWidget(self.settingButton, 0)

        # 表格区域

        self.table = TableWidget(self)
        self.table.verticalHeader().hide()  # 隐藏左侧表头
        self.table.horizontalHeader().setHighlightSections(False)  # 选中时表头不加粗
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)  # 单选模式
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止双击编辑
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["ID", "文件夹", "动画名（本季）", "动画名（首季）", "重命名"])
        self.table.setColumnWidth(0, 36)  # 1028
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(3, 180)
        self.table.setColumnWidth(4, 430)
        styleSheetManager.deregister(self.table)  # 禁用皮肤，启用自定义 QSS
        with open(getResource("src/style/table.qss"), encoding="utf-8") as file:
            self.table.setStyleSheet(file.read())

        self.tableLayout = QHBoxLayout()
        self.tableLayout.setContentsMargins(0, 0, 0, 0)
        self.tableLayout.addWidget(self.table)

        self.tableFrame = QFrame()
        self.tableFrame.setObjectName("tableFrame")
        self.tableFrame.setLayout(self.tableLayout)

        # 图片区域（从类中定义）

        self.image = RoundedLabel(getResource("image/empty.png"))

        # 右侧标题

        self.cnName = QLabel("暂无动画")
        self.cnName.setObjectName("cnName")
        self.jpName = QLabel("请先选中一个动画以展示详细信息")
        self.jpName.setObjectName("jpName")

        self.nameLayout = QVBoxLayout()
        self.nameLayout.setSpacing(8)
        self.nameLayout.setContentsMargins(0, 0, 0, 0)
        self.nameLayout.addSpacing(6)
        self.nameLayout.addWidget(self.cnName)
        self.nameLayout.addWidget(self.jpName)

        self.editButton = ToolButton(FluentIcon.EDIT, self)
        self.linkButton = ToolButton(FluentIcon.LINK, self)

        self.titleLayout = QHBoxLayout()
        self.titleLayout.setSpacing(12)
        self.titleLayout.addLayout(self.nameLayout, 0)
        self.titleLayout.addStretch(0)
        self.titleLayout.addWidget(self.editButton)
        self.titleLayout.addWidget(self.linkButton)
        self.titleLayout.addSpacing(12)

        # 右侧详细

        self.separator = QFrame()
        self.separator.setObjectName("separator")
        self.separator.setMinimumHeight(1)
        self.separator.setMaximumHeight(1)

        self.typeLabel = QLabel("类型：")
        self.typeLabel.setObjectName("detailLabel")
        self.dateLabel = QLabel("放送日期：")
        self.dateLabel.setObjectName("detailLabel")
        self.fileName = QLabel("文件名：")
        self.fileName.setObjectName("detailLabel")
        self.finalName = QLabel("重命名结果：")
        self.finalName.setObjectName("detailLabel")

        self.rightLayout = QVBoxLayout()
        self.rightLayout.setSpacing(10)
        self.rightLayout.addLayout(self.titleLayout)
        self.rightLayout.addSpacing(4)
        self.rightLayout.addWidget(self.separator)
        self.rightLayout.addSpacing(4)
        self.rightLayout.addWidget(self.typeLabel)
        self.rightLayout.addWidget(self.dateLabel)
        self.rightLayout.addWidget(self.fileName)
        self.rightLayout.addWidget(self.finalName)
        self.rightLayout.addStretch(0)

        self.infoLayout = QHBoxLayout()
        self.infoLayout.setSpacing(20)
        self.infoLayout.setContentsMargins(16, 16, 16, 16)
        self.infoLayout.addWidget(self.image)
        self.infoLayout.addLayout(self.rightLayout, 0)

        self.infoFrame = QFrame()
        self.infoFrame.setObjectName("infoFrame")
        self.infoFrame.setLayout(self.infoLayout)
        self.infoFrame.setFixedHeight(self.infoFrame.sizeHint().height())  # 高度自适应

        # 操作区域

        self.clearButton = PushButton("清空列表", self)
        self.clearButton.setFixedWidth(120)
        # self.clearButton.clicked.connect(self.clearList)
        self.analysisButton = PushButton("开始分析", self)
        self.analysisButton.setFixedWidth(120)
        # self.analysisButton.clicked.connect(self.startAnalysis)
        self.renameButton = PrimaryPushButton("重命名", self)
        self.renameButton.setFixedWidth(120)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(12)
        self.buttonLayout.addWidget(self.clearButton)
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.analysisButton)
        self.buttonLayout.addWidget(self.renameButton)

        # 框架叠叠乐

        self.centralWidget = QWidget(this_window)

        self.layout = QVBoxLayout(self.centralWidget)
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(36, 20, 36, 24)
        self.layout.addLayout(self.headerLayout)
        self.layout.addSpacing(24)
        self.layout.addWidget(self.tableFrame)
        self.layout.addWidget(self.infoFrame)
        self.layout.addSpacing(24)
        self.layout.addLayout(self.buttonLayout)

        this_window.setCentralWidget(self.centralWidget)

        QMetaObject.connectSlotsByName(this_window)
