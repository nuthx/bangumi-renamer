import os
import re
import arrow
import threading
import shutil
from PySide6 import QtCore, QtGui, QtWidgets
from module import function


from PySide6.QtCore import Qt, Signal, QUrl, QEvent
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QFrame, QTableWidgetItem, QAbstractItemView

from qfluentwidgets import setThemeColor, PushButton, ToolButton, TableWidget, PrimaryPushButton, FluentIcon
from qfluentwidgets.common.style_sheet import styleSheetManager


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()
        setThemeColor("#F09199")
        self.setWindowTitle("Bangumi Renamer")
        self.resize(1000, 720)
        self.setAcceptDrops(True)
        # self.setFixedSize(self.size())  # 禁止拉伸窗口

        self.titleLabel = QLabel("Bangumi Renamer", self)
        self.titleLabel.setObjectName("titleLabel")
        self.subtitleLabel = QLabel("略微先进的动画重命名工具", self)
        self.subtitleLabel.setObjectName('subtitleLabel')

        self.table = TableWidget(self)
        self.table.verticalHeader().hide()  # 隐藏左侧表头
        self.table.horizontalHeader().setHighlightSections(False)  # 选中时表头不加粗
        self.table.setSelectionMode(QAbstractItemView.SingleSelection)  # 单选模式
        self.table.setColumnCount(5)
        self.table.setRowCount(3)
        self.table.setHorizontalHeaderLabels(["ID", "文件夹", "动画名（本季）", "动画名（首季）", "重命名"])
        self.table.setColumnWidth(0, 36)  # 928
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 180)
        self.table.setColumnWidth(3, 180)
        self.table.setColumnWidth(4, 330)
        # self.table.resizeColumnsToContents()
        styleSheetManager.deregister(self.table)  # 禁用皮肤，启用自定义 QSS
        with open("style/table.qss", encoding="utf-8") as file:
            self.table.setStyleSheet(file.read())

        self.table.setItem(0, 0, QTableWidgetItem("24"))
        self.table.setItem(0, 1, QTableWidgetItem("文件名文件名文件名文件名文件名"))
        self.table.setItem(0, 2, QTableWidgetItem("动画动画名动画名"))
        self.table.setItem(0, 3, QTableWidgetItem("动画名动画名动名文件名画名动画名"))
        self.table.setItem(0, 4, QTableWidgetItem("动画名动画名动名文件名名文件名画名动画名"))
        self.table.setItem(1, 0, QTableWidgetItem("27"))
        self.table.setItem(1, 1, QTableWidgetItem("文件名文件名文件名文件名文件名"))
        self.table.setItem(1, 2, QTableWidgetItem("动画名动画名动画名动画名"))
        self.table.setItem(2, 0, QTableWidgetItem("23"))
        self.table.setItem(2, 1, QTableWidgetItem("文件名文件名文件名文件名文件名"))
        self.table.setItem(2, 2, QTableWidgetItem("动画名动画名动画名动画名"))

        self.pixmap = QPixmap("image/empty.png")
        self.pixmap = self.pixmap.scaledToWidth(142)
        self.image = QLabel(self)
        self.image.setMinimumSize(150, 210)
        self.image.setMaximumSize(150, 210)
        self.image.setPixmap(self.pixmap)

        self.cnLabel = QLabel("澳门永利礼享", self)
        self.cnLabel.setObjectName("cnLabel")
        self.jpLabel = QLabel("澳门永利礼享", self)
        self.jpLabel.setObjectName("jpLabel")

        self.editButton = ToolButton(FluentIcon.EDIT, self)
        self.linkButton = ToolButton(FluentIcon.LINK, self)

        self.separator = QFrame()
        self.separator.setObjectName("separator")
        self.separator.setMinimumHeight(1)
        self.separator.setMaximumHeight(1)

        self.typeLabel = QLabel("类型：", self)
        self.typeLabel.setObjectName("typeLabel")
        self.dateLabel = QLabel("放送日期：", self)
        self.dateLabel.setObjectName("dateLabel")
        self.fileNameLabel = QLabel("文件名：", self)
        self.fileNameLabel.setObjectName("fileNameLabel")
        self.finalNameLabel = QLabel("重命名结果：", self)
        self.finalNameLabel.setObjectName("finalNameLabel")

        self.settingButton = PushButton("格式设置", self)
        self.settingButton.setFixedWidth(120)
        self.analysisButton = PushButton("开始分析", self)
        self.analysisButton.setFixedWidth(120)
        self.renameButton = PrimaryPushButton("重命名", self)
        self.renameButton.setFixedWidth(120)

        self.__initLayout()

    def __initLayout(self):
        self.tableLayout = QHBoxLayout()
        self.tableLayout.setSpacing(0)
        self.tableLayout.setContentsMargins(0, 0, 0, 0)
        self.tableLayout.addWidget(self.table)

        self.tableFrame = QFrame()
        self.tableFrame.setObjectName("tableFrame")
        self.tableFrame.setLayout(self.tableLayout)

        self.nameLayout = QVBoxLayout()
        self.nameLayout.setSpacing(8)
        self.nameLayout.setContentsMargins(0, 0, 0, 0)
        self.nameLayout.addSpacing(10)
        self.nameLayout.addWidget(self.cnLabel)
        self.nameLayout.addWidget(self.jpLabel)

        self.titleLayout = QHBoxLayout()
        self.titleLayout.setSpacing(12)
        self.titleLayout.setContentsMargins(0, 0, 0, 0)
        self.titleLayout.addLayout(self.nameLayout, 0)
        self.titleLayout.addStretch(1)
        self.titleLayout.addWidget(self.editButton)
        self.titleLayout.addWidget(self.linkButton)
        self.titleLayout.addSpacing(12)

        self.detailLayout = QVBoxLayout()
        self.detailLayout.setSpacing(8)
        self.detailLayout.setContentsMargins(0, 0, 0, 0)
        self.detailLayout.addLayout(self.titleLayout, 0)
        self.detailLayout.addSpacing(8)
        self.detailLayout.addWidget(self.separator)
        self.detailLayout.addSpacing(8)
        self.detailLayout.addWidget(self.typeLabel)
        self.detailLayout.addWidget(self.dateLabel)
        self.detailLayout.addWidget(self.fileNameLabel)
        self.detailLayout.addWidget(self.finalNameLabel)
        self.detailLayout.addStretch(1)

        self.infoLayout = QHBoxLayout()
        self.infoLayout.setSpacing(12)
        self.infoLayout.setContentsMargins(16, 16, 16, 16)
        self.infoLayout.setObjectName("infoLayout")
        self.infoLayout.addWidget(self.image)
        self.infoLayout.addLayout(self.detailLayout, 0)

        self.infoFrame = QFrame(self)
        self.infoFrame.setObjectName("infoFrame")
        self.infoFrame.setLayout(self.infoLayout)
        self.infoFrame.setMaximumHeight(242)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(12)
        self.buttonLayout.setContentsMargins(0, 0, 0, 0)
        self.buttonLayout.setObjectName("infoLayout")
        self.buttonLayout.addWidget(self.settingButton)
        self.buttonLayout.addStretch(1)
        self.buttonLayout.addWidget(self.analysisButton)
        self.buttonLayout.addWidget(self.renameButton)

        self.buttonFrame = QFrame(self)
        self.buttonFrame.setObjectName("buttonFrame")
        self.buttonFrame.setLayout(self.buttonLayout)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(36, 24, 36, 24)
        self.vBoxLayout.addWidget(self.titleLabel, 0, Qt.AlignTop)
        self.vBoxLayout.addSpacing(4)
        self.vBoxLayout.addWidget(self.subtitleLabel, 0, Qt.AlignTop)
        self.vBoxLayout.addSpacing(24)
        self.vBoxLayout.addWidget(self.tableFrame, 0)
        self.vBoxLayout.addWidget(self.infoFrame, 0)
        self.vBoxLayout.addSpacing(24)
        self.vBoxLayout.addWidget(self.buttonFrame, 0)
