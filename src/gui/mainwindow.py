from PySide6.QtCore import QMetaObject, Qt
from PySide6.QtGui import QFontDatabase, QFont, QIcon
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QAbstractItemView, QListWidgetItem
from qfluentwidgets import (setThemeColor, PushButton, ToolButton, TableWidget, PrimaryPushButton, FluentIcon,
                            IndeterminateProgressRing, TransparentPushButton, ListWidget)
from qfluentwidgets.common.style_sheet import styleSheetManager

from src.module.version import currentVersion
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

        this_window.setWindowTitle(f"BangumiRenamer {currentVersion()}")
        this_window.setWindowIcon(QIcon(getResource("src/image/icon.png")))
        this_window.resize(1280, 720)
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

        self.spinner = IndeterminateProgressRing()
        self.spinner.setFixedSize(24, 24)
        self.spinner.setStrokeWidth(3)
        self.spinner.setVisible(False)

        self.aboutButton = ToolButton(FluentIcon.INFO, self)
        self.settingButton = PushButton("设置", self, FluentIcon.SETTING)

        self.headerLayout = QHBoxLayout()
        self.headerLayout.setContentsMargins(0, 0, 0, 0)
        self.headerLayout.addLayout(self.titleLayout)
        self.headerLayout.addStretch(0)
        self.headerLayout.addWidget(self.spinner, 0)
        self.headerLayout.addSpacing(16)
        self.headerLayout.addWidget(self.aboutButton, 0)
        self.headerLayout.addSpacing(12)
        self.headerLayout.addWidget(self.settingButton, 0)

        # 表格区域

        self.table = TableWidget(self)
        self.table.verticalHeader().hide()  # 隐藏左侧表头
        self.table.horizontalHeader().setHighlightSections(False)  # 选中时表头不加粗
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)  # 单选模式
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)  # 禁止双击编辑
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "动画文件夹", "动画名", "首季动画名"])
        self.table.setColumnWidth(0, 46)  # 1206
        self.table.setColumnWidth(1, 540)
        self.table.setColumnWidth(2, 320)
        self.table.setColumnWidth(3, 300)
        styleSheetManager.deregister(self.table)  # 禁用皮肤，启用自定义 QSS
        with open(getResource("src/style/table.qss"), encoding="utf-8") as file:
            self.table.setStyleSheet(file.read())

        self.tableLayout = QHBoxLayout()
        self.tableLayout.setContentsMargins(0, 0, 0, 0)
        self.tableLayout.addWidget(self.table)

        self.tableFrame = QFrame()
        self.tableFrame.setObjectName("tableFrame")
        self.tableFrame.setLayout(self.tableLayout)

        # 1 => 图片

        self.image = RoundedLabel(getResource("src/image/empty.png"))

        # 2.1 => 标题

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

        self.linkButton = ToolButton(FluentIcon.LINK, self)

        self.titleLayout = QHBoxLayout()
        self.titleLayout.setSpacing(12)
        self.titleLayout.addLayout(self.nameLayout, 0)
        self.titleLayout.addStretch(0)
        self.titleLayout.addWidget(self.linkButton)
        self.titleLayout.addSpacing(12)

        # 2.2 => 详情

        self.separator = QFrame()
        self.separator.setObjectName("separator")
        self.separator.setMinimumHeight(1)
        self.separator.setMaximumHeight(1)

        self.typeLabel = QLabel("类型：")
        self.typeLabel.setObjectName("detailLabel")
        self.dateLabel = QLabel("放送日期：")
        self.dateLabel.setObjectName("detailLabel")
        # self.episodeLabel = QLabel("章节数量：")
        # self.episodeLabel.setObjectName("detailLabel")
        self.scoreLabel = QLabel("当前评分：")
        self.scoreLabel.setObjectName("detailLabel")
        self.fileName = QLabel("文件名：")
        self.fileName.setObjectName("detailLabel")
        self.finalName = QLabel("重命名：")
        self.finalName.setObjectName("detailLabel")

        self.detailLayout = QVBoxLayout()
        self.detailLayout.setSpacing(10)
        self.detailLayout.addLayout(self.titleLayout)
        self.detailLayout.addSpacing(4)
        self.detailLayout.addWidget(self.separator)
        self.detailLayout.addSpacing(4)
        self.detailLayout.addWidget(self.typeLabel)
        self.detailLayout.addWidget(self.dateLabel)
        # self.detailLayout.addWidget(self.episodeLabel)
        self.detailLayout.addWidget(self.scoreLabel)
        self.detailLayout.addWidget(self.fileName)
        self.detailLayout.addWidget(self.finalName)
        self.detailLayout.addStretch(0)

        # 3 => 列表

        self.separator2 = QFrame()
        self.separator2.setObjectName("separator")
        self.separator2.setFixedSize(1, 210)

        self.searchList = ListWidget(self)
        self.searchList.setFixedWidth(300)
        styleSheetManager.deregister(self.searchList)  # 禁用皮肤，启用自定义 QSS
        with open(getResource("src/style/list.qss"), encoding="utf-8") as file:
            self.searchList.setStyleSheet(file.read())

        self.infoLayout = QHBoxLayout()
        self.infoLayout.setSpacing(20)
        self.infoLayout.setContentsMargins(16, 16, 16, 16)
        self.infoLayout.addWidget(self.image)
        self.infoLayout.addLayout(self.detailLayout)
        self.infoLayout.addWidget(self.separator2)
        self.infoLayout.addSpacing(-8)
        self.infoLayout.addWidget(self.searchList)

        self.infoFrame = QFrame()
        self.infoFrame.setObjectName("infoFrame")
        self.infoFrame.setLayout(self.infoLayout)
        self.infoFrame.setFixedHeight(self.infoFrame.sizeHint().height())  # 高度自适应

        # 操作区域

        self.clearButton = PushButton("清空列表", self)
        self.clearButton.setFixedWidth(120)

        self.buttonSeparator = QFrame()
        self.buttonSeparator.setObjectName("buttonSeparator")
        self.buttonSeparator.setFixedSize(1, 30)

        self.analysisButton = PushButton("开始分析", self)
        self.analysisButton.setFixedWidth(120)
        self.renameButton = PrimaryPushButton("重命名", self)
        self.renameButton.setFixedWidth(120)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(12)
        self.buttonLayout.addStretch(0)
        self.buttonLayout.addWidget(self.clearButton)
        self.buttonLayout.addSpacing(8)
        self.buttonLayout.addWidget(self.buttonSeparator)
        self.buttonLayout.addSpacing(8)
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
