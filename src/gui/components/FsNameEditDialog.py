from PySide6.QtCore import QUrl
from qfluentwidgets import MessageBoxBase, SubtitleLabel, LineEdit


class FsNameEditDialog(MessageBoxBase):
    def __init__(self, parent, init_name):
        super().__init__(parent)
        self.widget.setMinimumWidth(350)

        self.titleLabel = SubtitleLabel("首季动画名", self)

        self.nameEdit = LineEdit(self)
        self.nameEdit.setText(init_name)

        self.viewLayout.addWidget(self.titleLabel)
        self.viewLayout.addWidget(self.nameEdit)

        self.yesButton.setText("应用")
        self.yesButton.setDisabled(True)
        self.cancelButton.setText("取消")

        self.nameEdit.textChanged.connect(self._validateUrl)

    def _validateUrl(self, text):
        self.yesButton.setEnabled(QUrl(text).isValid())
