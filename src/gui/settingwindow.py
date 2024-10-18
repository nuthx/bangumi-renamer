from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame, QMainWindow, QWidget
from qfluentwidgets import PushButton, FluentIcon, PrimaryPushButton, EditableComboBox, SingleDirectionScrollArea, \
    SettingCard, GroupHeaderCardWidget, SearchLineEdit, ComboBox, IconWidget, InfoBarIcon, BodyLabel, CardWidget, \
    CaptionLabel, TransparentToolButton, SwitchButton, IndicatorPosition, ExpandGroupSettingCard, LineEdit

from src.module.utils import getResource
from src.module.config import posterFolder, logFolder


class SettingWindow(object):
    def setupUI(self, this_window):
        # 加载 QSS
        with open(getResource("src/style/style_light.qss"), "r", encoding="UTF-8") as file:
            style_sheet = file.read()
        this_window.setStyleSheet(style_sheet)

        this_window.setWindowTitle("设置")
        this_window.setWindowIcon(QIcon(getResource("src/image/icon_win.png")))
        this_window.resize(850, -1)
        this_window.setFixedSize(self.size())  # 禁止拉伸窗口

        # 命名格式

        self.renameTypeTitle = QLabel("命名格式")
        self.renameTypeInfo = QLabel("变量必须包含花括号；单斜杠用于文件夹嵌套")

        self.renameType = EditableComboBox(self)
        self.renameType.setMinimumWidth(480)
        self.renameType.setMaximumWidth(400)
        self.renameType.addItems(["{fs_name_cn}/[{typecode}] [{release}] {name_jp}",
                                  "{fs_name_cn}/[{score}] [{typecode}] [{release}] {name_jp}",
                                  "{type}/{name} ({name_jp})",
                                  "[{release}] {name_cn} ({release_week})"])

        self.renameTypeCard = self.settingCard(self.renameTypeTitle, self.renameTypeInfo, self.renameType, "half")

        # 命名说明

        self.t1 = self.tutorialCard("name_jp", "日文名")
        self.t2 = self.tutorialCard("name_cn", "中文名")
        self.t3 = self.tutorialCard("fs_name_cn", "首季中文名")
        self.t4 = self.tutorialCard("bangumi_id", "Bangumi ID")

        self.f1 = QHBoxLayout()
        self.f1.setSpacing(12)
        self.f1.setContentsMargins(0, 0, 0, 0)
        self.f1.addWidget(self.t1)
        self.f1.addWidget(self.t2)
        self.f1.addWidget(self.t3)
        self.f1.addWidget(self.t4)

        self.t5 = self.tutorialCard("type", "动画类型")
        self.t6 = self.tutorialCard("typecode", "类型编号")
        self.t7 = self.tutorialCard("episodes", "当前评分")
        self.t8 = self.tutorialCard("score", "章节数量")

        self.f2 = QHBoxLayout()
        self.f2.setSpacing(12)
        self.f2.setContentsMargins(0, 0, 0, 0)
        self.f2.addWidget(self.t5)
        self.f2.addWidget(self.t6)
        self.f2.addWidget(self.t7)
        self.f2.addWidget(self.t8)

        self.t9 = self.tutorialCard("release", "放送开始日期")
        self.t10 = self.tutorialCard("release_end", "放送结束日期")
        self.t11 = self.tutorialCard("release_week", "放送星期")
        self.t12 = self.tutorialCard("release_week", "放送星期")

        self.f3 = QHBoxLayout()
        self.f3.setSpacing(12)
        self.f3.setContentsMargins(0, 0, 0, 0)
        self.f3.addWidget(self.t9)
        self.f3.addWidget(self.t10)
        self.f3.addWidget(self.t11)
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

        # 动画海报

        self.posterFolderTitle = QLabel("动画海报")
        self.posterFolderInfo = QLabel(posterFolder())

        self.posterFolderButton = PushButton("打开", self, FluentIcon.FOLDER)
        self.posterFolderButton.setFixedWidth(100)

        self.posterFolderCard = self.settingCard(
            self.posterFolderTitle, self.posterFolderInfo, self.posterFolderButton, "full")

        # 日志

        self.logFolderTitle = QLabel("日志")
        self.logFolderInfo = QLabel(logFolder())

        self.logFolderButton = PushButton("打开", self, FluentIcon.FOLDER)
        self.logFolderButton.setFixedWidth(100)

        self.logFolderCard = self.settingCard(
            self.logFolderTitle, self.logFolderInfo, self.logFolderButton, "full")

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
        layout = QVBoxLayout()
        # layout = QVBoxLayout(this_window)
        layout.setSpacing(14)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addWidget(self.renameTypeCard)
        layout.addSpacing(-15)
        layout.addWidget(self.renameTutorialCard)
        layout.addWidget(self.dateTypeCard)
        layout.addWidget(self.posterFolderCard)
        layout.addWidget(self.logFolderCard)

        self.ai_setting = AISetting()
        layout.addWidget(self.ai_setting)
        layout.addSpacing(12)
        layout.addLayout(self.buttonLayout)

        this_window.setLayout(layout)

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


class AISetting(GroupHeaderCardWidget):
    def __init__(self):
        super().__init__()
        # TODO: 重写边框样式、副标题尺寸(尝试大改)
        self.setTitle("AI 设置")
        self.setBorderRadius(8)

        self.usage = ComboBox()
        self.usage.setFixedWidth(320)
        self.usage.addItems(["不使用", "优先本地分析，失败时尝试 AI 分析", "优先 AI 分析，失败时尝试本地分析", "始终使用 AI 分析"])
        self.addGroup(InfoBarIcon.INFORMATION, "启用 AI", "使用 AI 提取动画罗马名，获取更准确（或更离谱）的结果", self.usage)

        self.url = LineEdit()
        self.url.setFixedWidth(320)
        # self.url.setPlaceholderText("https://")
        self.addGroup(InfoBarIcon.INFORMATION, "服务器地址", "输入 AI 服务器的域名地址", self.url)

        self.token = LineEdit()
        self.token.setFixedWidth(320)
        # self.token.setPlaceholderText("sk-")
        self.addGroup(InfoBarIcon.INFORMATION, "API Key", "输入用于连接 AI 服务器的授权 Token，通常以 sk 开头", self.token)

        self.model = EditableComboBox()
        self.model.setFixedWidth(320)
        self.model.addItems(["", "gpt-3.5-turbo", "gpt-4o", "gpt-4o-mini", "qwen2-1.5b-instruct", "hunyuan-lite"])
        self.addGroup(InfoBarIcon.INFORMATION, "AI 模型", "选择你想使用的 AI 模型", self.model)

        self.test = PushButton("开始测试", self)
        self.test.setFixedWidth(100)
        self.addGroup(InfoBarIcon.INFORMATION, "连接测试", "通过发送简短的请求，测试填写的 AI 服务器是否可用", self.test)
