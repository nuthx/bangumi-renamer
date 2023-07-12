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
        this_window.setWindowIcon(QIcon(getResource("image/icon.png")))
        this_window.resize(850, -1)
        this_window.setFixedSize(self.size())  # 禁止拉伸窗口

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
        self.dateType.setCurrentIndex(0)

        self.dateTypeCard = self.settingCard(self.dateTypeTitle, self.dateInfoFrame, self.dateType)

        # 图片缓存

        self.posterFolderTitle = QLabel("动画海报")
        self.posterFolderInfo = QLabel(posterFolder())

        self.posterFolderButton = PushButton("打开", self, FluentIcon.FOLDER)
        self.posterFolderButton.setFixedWidth(100)

        self.posterFolderCard = self.settingCard(self.posterFolderTitle, self.posterFolderInfo, self.posterFolderButton)

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
        layout.addWidget(self.renameTypeCard)
        layout.addWidget(self.renameTutorialCard)
        layout.addWidget(self.dateTypeCard)
        layout.addWidget(self.posterFolderCard)
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
