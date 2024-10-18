from qfluentwidgets import InfoBar, InfoBarPosition


class Toast:
    def __init__(self, parent=None):
        self.parent = parent

    def show(self, state, title, content):
        """
        显示Toast通知
        :param state: 通知等级
        :param title: 标题
        :param content: 内容
        """
        info_state = {
            "info": InfoBar.info,
            "success": InfoBar.success,
            "warning": InfoBar.warning,
            "error": InfoBar.error
        }

        if state in info_state:
            info_state[state](
                title=title,
                content=content,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self.parent
            )
