from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PySide6.QtGui import QIcon, QDesktopServices
from qfluentwidgets import PushButton, ToolButton, FluentIcon, PrimaryPushButton, EditableComboBox

from src.module.resource import getResource
from src.module.config import configPath, posterFolder


class SettingWindow(object):
    def setupUI(self, this_window):
        # 加载 QSS
        with open(getResource("src/style/style_light.qss"), "r", encoding="UTF-8") as file:
            style_sheet = file.read()
        this_window.setStyleSheet(style_sheet)

        this_window.setWindowTitle("设置")
        this_window.setWindowIcon(QIcon(getResource("image/icon.png")))
        this_window.resize(850, -1)
        this_window.setFixedSize(self.size())  # 禁止拉伸窗口

        # 标题

        self.basicTitle = QLabel("基础设置")
        self.basicTitle.setObjectName("settingTitle")
        self.basicTitle.setIndent(22)  # 缩进

        # 命名格式

        self.renameTypeTitle = QLabel("命名格式")
        self.renameTypeInfo = QLabel("请参考说明填写，避免出现错误")

        self.renameType = EditableComboBox(self)
        self.renameType.setMinimumWidth(480)
        self.renameType.setMaximumWidth(400)
        self.renameType.addItems(["{initial_name}/[{bgm_typecode}] [{release_date}] {jp_name}",
                                  "[{bgm_type}] [{release_date}] {jp_name}",
                                  "[EP{episodes}] [{release_date}] {cn_name}"])
        self.renameType.setCurrentIndex(0)

        self.renameTypeCard = self.settingCard(self.renameTypeTitle, self.renameTypeInfo, self.renameType)

        # 命名说明

        self.renameTutorial = QLabel("file_name：文件名<br>"
                                     "bgm_id：Bangumi动画ID<br>"
                                     "romaji_name：动画罗马名<br>"
                                     "jp_name：动画日文名<br>"
                                     "cn_name：动画中文名<br>"
                                     "initial_name：动画首季度中文名<br>"
                                     "bgm_type：动画类型<br>"
                                     "bgm_typecode：动画类型编码<br>"
                                     "release_date：上映日期<br>"
                                     "episodes：章节数量")

        self.renameTutorialLayout = QHBoxLayout()
        self.renameTutorialLayout.setContentsMargins(20, 16, 20, 16)
        self.renameTutorialLayout.addWidget(self.renameTutorial)

        self.renameTutorialCard = QFrame()
        self.renameTutorialCard.setObjectName("cardFrame")
        self.renameTutorialCard.setLayout(self.renameTutorialLayout)

        # 日期格式

        self.dateTypeTitle = QLabel("日期格式")
        self.dateTypeInfo = QLabel("为release_date指定日期格式")

        self.dateType = EditableComboBox(self)
        self.dateType.setMinimumWidth(200)
        self.dateType.setMaximumWidth(200)
        self.dateType.addItems(["YYMMDD", "YYYY-MM", "MMM YYYY"])
        self.dateType.setCurrentIndex(0)

        self.dateToken = ToolButton(FluentIcon.LINK, self)
        self.dateToken.clicked.connect(self.openDateTypeTokenLink)

        self.dateTypeLayout = QHBoxLayout()
        self.dateTypeLayout.setSpacing(0)
        self.dateTypeLayout.setContentsMargins(0, 0, 0, 0)
        self.dateTypeLayout.addWidget(self.dateType)
        self.dateTypeLayout.addSpacing(-36)  # 硬算的间距，只要其他宽度不变就不要动
        self.dateTypeLayout.addWidget(self.dateToken)
        self.dateTypeLayout.addSpacing(-48)  # 硬算的间距，只要其他宽度不变就不要动

        self.dateTypeFrame = QFrame()
        self.dateTypeFrame.setLayout(self.dateTypeLayout)

        self.dateTypeCard = self.settingCard(self.dateTypeTitle, self.dateTypeInfo, self.dateTypeFrame)

        # 标题

        self.folderTitle = QLabel("储存位置")
        self.folderTitle.setObjectName("settingTitle")
        self.folderTitle.setIndent(22)  # 缩进

        # 图片缓存

        self.posterFolderTitle = QLabel("动画海报")
        self.posterFolderInfo = QLabel(posterFolder())

        self.posterFolderButton = PushButton("打开", self, FluentIcon.FOLDER)
        self.posterFolderButton.setFixedWidth(100)

        self.posterFolderCard = self.settingCard(self.posterFolderTitle, self.posterFolderInfo, self.posterFolderButton)

        # 配置文件

        self.configFolderTitle = QLabel("配置文件")
        self.configFolderInfo = QLabel(configPath())

        self.configFolderButton = PushButton("打开", self, FluentIcon.FOLDER)
        self.configFolderButton.setFixedWidth(100)

        self.configFolderCard = self.settingCard(self.configFolderTitle, self.configFolderInfo, self.configFolderButton)

        # 按钮

        self.cancelButton = PushButton("取消", self)
        self.cancelButton.setFixedWidth(120)
        self.applyButton = PrimaryPushButton("保存", self)
        self.applyButton.setFixedWidth(120)

        self.buttonLayout = QHBoxLayout()
        self.buttonLayout.setSpacing(12)
        self.buttonLayout.addStretch(0)
        self.buttonLayout.addWidget(self.cancelButton)
        self.buttonLayout.addWidget(self.applyButton)
        self.buttonLayout.addStretch(0)

        # 叠叠乐

        layout = QVBoxLayout(this_window)
        layout.setSpacing(8)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(self.basicTitle)
        layout.addSpacing(16)
        layout.addWidget(self.renameTypeCard)
        layout.addWidget(self.renameTutorialCard)
        layout.addWidget(self.dateTypeCard)
        layout.addSpacing(20)
        layout.addWidget(self.folderTitle)
        layout.addSpacing(16)
        layout.addWidget(self.posterFolderCard)
        layout.addWidget(self.configFolderCard)
        layout.addSpacing(12)
        layout.addLayout(self.buttonLayout)

    def settingCard(self, card_title, card_info, card_func):
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
        self.cardFrame.setObjectName("cardFrame")
        self.cardFrame.setLayout(self.card)

        return self.cardFrame

    def openDateTypeTokenLink(self):
        url = "https://arrow.readthedocs.io/en/latest/guide.html#supported-tokens"
        QDesktopServices.openUrl(url)
