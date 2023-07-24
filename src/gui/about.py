from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QFrame
from PySide6.QtGui import QFontDatabase, QFont, QIcon, QPixmap

from src.module.resource import getResource
from src.module.version import currentVersion


class AboutWindow(object):
    def setupUI(self, this_window):
        font_id = QFontDatabase.addApplicationFont(getResource("src/font/Study-Bold.otf"))
        font_family = QFontDatabase.applicationFontFamilies(font_id)

        # 加载 QSS
        with open(getResource("src/style/style_light.qss"), "r", encoding="UTF-8") as file:
            style_sheet = file.read()
        this_window.setStyleSheet(style_sheet)

        this_window.setWindowTitle("关于")
        this_window.setWindowIcon(QIcon(getResource("src/image/icon.png")))
        this_window.resize(550, -1)
        this_window.setFixedSize(self.size())  # 禁止拉伸窗口

        # LOGO

        self.logo = QLabel()
        self.logo.setFixedSize(100, 100)
        self.logo.setPixmap(QPixmap(getResource("src/image/icon.png")))
        self.logo.setScaledContents(True)

        self.logoLayout = QHBoxLayout()
        self.logoLayout.setAlignment(Qt.AlignLeft)
        self.logoLayout.addStretch(0)
        self.logoLayout.addWidget(self.logo)
        self.logoLayout.addStretch(0)

        self.titleLabel = QLabel("BangumiRenamer")
        self.titleLabel.setObjectName("logoLabel")
        self.titleLabel.setFont(QFont(font_family))
        self.titleLabel.setAlignment(Qt.AlignCenter)

        self.titleLayout = QVBoxLayout()
        self.titleLayout.setSpacing(6)
        self.titleLayout.addLayout(self.logoLayout)
        self.titleLayout.addWidget(self.titleLabel)

        # 计数

        self.openTimesTitle = QLabel("软件启动")
        self.openTimes = QLabel("0")
        self.openTimesCard = self.usageCard(self.openTimesTitle, self.openTimes)

        self.analysisTimesTitle = QLabel("分析动画")
        self.analysisTimes = QLabel("0")
        self.analysisTimesCard = self.usageCard(self.analysisTimesTitle, self.analysisTimes)

        self.renameTimesTitle = QLabel("重命名动画")
        self.renameTimes = QLabel("0")
        self.renameTimescard = self.usageCard(self.renameTimesTitle, self.renameTimes)

        self.usageCardLayout = QHBoxLayout()
        self.usageCardLayout.setSpacing(12)
        self.usageCardLayout.setContentsMargins(0, 0, 0, 0)
        self.usageCardLayout.addWidget(self.openTimesCard)
        self.usageCardLayout.addWidget(self.analysisTimesCard)
        self.usageCardLayout.addWidget(self.renameTimescard)

        # PING

        self.anilistPingTitle = QLabel("AniList API")
        self.anilistPing = QLabel("Testing...")
        self.anilistPingCard = self.usageCard(self.anilistPingTitle, self.anilistPing)

        self.bangumiPingTitle = QLabel("Bangumi API")
        self.bangumiPing = QLabel("Testing...")
        self.bangumiPingCard = self.usageCard(self.bangumiPingTitle, self.bangumiPing)

        self.PingCardLayout = QHBoxLayout()
        self.PingCardLayout.setSpacing(12)
        self.PingCardLayout.setContentsMargins(0, 0, 0, 0)
        self.PingCardLayout.addWidget(self.anilistPingCard)
        self.PingCardLayout.addWidget(self.bangumiPingCard)

        # Github

        self.versionLabel = QLabel(f"Version {currentVersion()}")
        self.versionLabel.setObjectName("lightLabel")

        self.githubUrl = QLabel("<a href='https://github.com/nuthx/bangumi-renamer' style='color:#F09199'>"
                                "https://github.com/nuthx/bangumi-renamer</a>")
        self.githubUrl.setObjectName("urlLabel")
        self.githubUrl.setOpenExternalLinks(True)  # 允许打开外部链接

        self.githubLayout = QHBoxLayout()
        self.githubLayout.setSpacing(0)
        self.githubLayout.setAlignment(Qt.AlignLeft)
        self.githubLayout.addStretch(0)
        self.githubLayout.addWidget(self.versionLabel)
        self.githubLayout.addSpacing(12)
        self.githubLayout.addWidget(self.githubUrl)
        self.githubLayout.addStretch(0)

        # 叠叠乐

        layout = QVBoxLayout(this_window)
        layout.setSpacing(12)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.addLayout(self.titleLayout)
        layout.addSpacing(20)
        layout.addLayout(self.usageCardLayout)
        layout.addLayout(self.PingCardLayout)
        layout.addSpacing(24)
        layout.addLayout(self.githubLayout)

    def usageCard(self, usage_title, usage_times):
        usage_title.setObjectName("lightLabel")
        usage_times.setObjectName("lightLabel")

        self.card = QHBoxLayout()
        self.card.setContentsMargins(16, 12, 16, 12)
        self.card.addWidget(usage_title, 0)
        self.card.addStretch(0)
        self.card.addWidget(usage_times)

        self.cardFrame = QFrame()
        self.cardFrame.setObjectName("cardFrameFull")
        self.cardFrame.setLayout(self.card)

        return self.cardFrame
