from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PySide6.QtGui import QIcon
from qfluentwidgets import PushButton, FluentIcon, PrimaryPushButton, EditableComboBox

from src.module.resource import getResource
from src.module.config import posterFolder


class SettingWindow(object):
    def setupUI(self, this_window):
        # 加载 QSS
        with open(getResource("src/style/style_light.qss"), "r", encoding="UTF-8") as file:
            style_sheet = file.read()
        this_window.setStyleSheet(style_sheet)

        this_window.setWindowTitle("设置")
        this_window.setWindowIcon(QIcon(getResource("src/image/icon.png")))
        this_window.resize(850, -1)
        this_window.setFixedSize(self.size())  # 禁止拉伸窗口

        # 命名格式

        self.renameTypeTitle = QLabel("命名格式")
        self.renameTypeInfo = QLabel("变量必须包含花括号；单斜杠用于文件夹嵌套")

        self.renameType = EditableComboBox(self)
        self.renameType.setMinimumWidth(480)
        self.renameType.setMaximumWidth(400)
        self.renameType.addItems(["{init_name}/[{score}] [{typecode}] [{release}] {jp_name}",
                                  "{init_name}/[{typecode}][{release}] {jp_name}",
                                  "{types}/{cn_name} ({jp_name})",
                                  "[{release}] {cn_name} ({episodes})"])

        self.renameTypeCard = self.settingCard(self.renameTypeTitle, self.renameTypeInfo, self.renameType, "half")

        # 命名说明

        self.t1 = self.tutorialCard("jp_name", "日文名")
        self.t2 = self.tutorialCard("cn_name", "中文名")
        self.t3 = self.tutorialCard("init_name", "首季中文名")
        self.t4 = self.tutorialCard("romaji_name", "罗马名")

        self.f1 = QHBoxLayout()
        self.f1.setSpacing(12)
        self.f1.setContentsMargins(0, 0, 0, 0)
        self.f1.addWidget(self.t1)
        self.f1.addWidget(self.t2)
        self.f1.addWidget(self.t3)
        self.f1.addWidget(self.t4)

        self.t5 = self.tutorialCard("types", "动画类型")
        self.t6 = self.tutorialCard("typecode", "类型编号")
        self.t7 = self.tutorialCard("release", "放送日期")
        self.t8 = self.tutorialCard("episodes", "章节数量")

        self.f2 = QHBoxLayout()
        self.f2.setSpacing(12)
        self.f2.setContentsMargins(0, 0, 0, 0)
        self.f2.addWidget(self.t5)
        self.f2.addWidget(self.t6)
        self.f2.addWidget(self.t7)
        self.f2.addWidget(self.t8)

        self.t9 = self.tutorialCard("score", "当前评分")
        self.t10 = self.tutorialCard("bgm_id", "Bangumi ID")
        # self.t11 = self.tutorialCard("", "")
        # self.t12 = self.tutorialCard("", "")

        self.f3 = QHBoxLayout()
        self.f3.setSpacing(12)
        self.f3.setContentsMargins(0, 0, 0, 0)
        self.f3.addWidget(self.t9)
        self.f3.addWidget(self.t10)
        # self.f3.addWidget(self.t11)
        # self.f3.addWidget(self.t12)
        self.f3.addStretch(0)

        self.renameTutorialLayout = QVBoxLayout()
        self.renameTutorialLayout.setSpacing(12)
        self.renameTutorialLayout.setContentsMargins(20, 16, 20, 16)
        self.renameTutorialLayout.addLayout(self.f1)
        self.renameTutorialLayout.addLayout(self.f2)
        self.renameTutorialLayout.addLayout(self.f3)

        self.renameTutorialCard = QFrame()
        self.renameTutorialCard.setObjectName("cardFrameHalf2")
        self.renameTutorialCard.setLayout(self.renameTutorialLayout)

        # 日期格式

        self.dateTypeTitle = QLabel("日期格式")

        self.dateTypeInfo = QLabel("指定 release_date 的显示格式，")
        self.dateTypeInfo.setObjectName("cardInfoLabel")

        self.dateTypeUrl = QLabel("<a href='https://arrow.readthedocs.io/en/latest/guide.html#supported-tokens' "
                                  "style='font-size:12px;color:#F09199;'>查看在线文档</a>")
        self.dateTypeUrl.setOpenExternalLinks(True)

        self.dataInfoLayout = QHBoxLayout()
        self.dataInfoLayout.setSpacing(0)
        self.dataInfoLayout.setContentsMargins(0, 0, 0, 0)
        self.dataInfoLayout.setAlignment(Qt.AlignLeft)
        self.dataInfoLayout.addWidget(self.dateTypeInfo)
        self.dataInfoLayout.addWidget(self.dateTypeUrl)

        self.dateInfoFrame = QFrame()
        self.dateInfoFrame.setLayout(self.dataInfoLayout)

        self.dateType = EditableComboBox(self)
        self.dateType.setMinimumWidth(200)
        self.dateType.setMaximumWidth(200)
        self.dateType.addItems(["YYMMDD", "YYYY-MM", "MMM YYYY"])

        self.dateTypeCard = self.settingCard(self.dateTypeTitle, self.dateInfoFrame, self.dateType, "full")

        # 图片缓存

        self.posterFolderTitle = QLabel("动画海报")
        self.posterFolderInfo = QLabel(posterFolder())

        self.posterFolderButton = PushButton("打开", self, FluentIcon.FOLDER)
        self.posterFolderButton.setFixedWidth(100)

        self.posterFolderCard = self.settingCard(
            self.posterFolderTitle, self.posterFolderInfo, self.posterFolderButton, "full")

        # 按钮

        self.applyButton = PrimaryPushButton("保存", self)
        self.applyButton.setFixedWidth(120)
        self.cancelButton = PushButton("取消", self)
        self.cancelButton.setFixedWidth(120)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(12)
        self.buttonLayout.addStretch(0)
        self.buttonLayout.addWidget(self.applyButton)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.addStretch(0)

        # 叠叠乐

        layout = QVBoxLayout(this_window)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(self.renameTypeCard)
        layout.addSpacing(-15)
        layout.addWidget(self.renameTutorialCard)
        layout.addWidget(self.dateTypeCard)
        layout.addWidget(self.posterFolderCard)
        layout.addSpacing(12)
        layout.addLayout(self.buttonLayout)

    def settingCard(self, card_title, card_info, card_func, size):
        card_title.setObjectName("cardTitleLabel")
        card_info.setObjectName("cardInfoLabel")

        self.infoPart = QVBoxLayout()
        self.infoPart.setSpacing(3)
        self.infoPart.setContentsMargins(0, 0, 0, 0)
        self.infoPart.addWidget(card_title)
        self.infoPart.addWidget(card_info)

        self.card = QHBoxLayout()
        self.card.setContentsMargins(20, 16, 20, 16)
        self.card.addLayout(self.infoPart, 0)
        self.card.addStretch(0)
        self.card.addWidget(card_func)

        self.cardFrame = QFrame()
        self.cardFrame.setLayout(self.card)

        if size == "half":
            self.cardFrame.setObjectName("cardFrameHalf")
        elif size == "full":
            self.cardFrame.setObjectName("cardFrameFull")

        return self.cardFrame

    def tutorialCard(self, card_token, card_explain):
        self.tokenLabel = QLabel(card_token)
        self.tokenLabel.setObjectName("lightLabel")
        self.explainLabel = QLabel(card_explain)
        self.explainLabel.setObjectName("lightLabel")

        self.tutorialLayout = QHBoxLayout()
        self.tutorialLayout.setContentsMargins(12, 8, 12, 8)
        self.tutorialLayout.addWidget(self.tokenLabel)
        self.tutorialLayout.addStretch(0)
        self.tutorialLayout.addWidget(self.explainLabel)

        self.card = QFrame()
        self.card.setMinimumWidth(181)
        self.card.setMaximumWidth(181)
        self.card.setObjectName("cardFrameTutorial")
        self.card.setLayout(self.tutorialLayout)

        return self.card
