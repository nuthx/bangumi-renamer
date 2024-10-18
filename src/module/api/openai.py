import requests

from src.module.config import readConfig


class OpenAI:
    def __init__(self):
        self.url = readConfig("AI", "url")
        self.token = readConfig("AI", "token")
        self.model = readConfig("AI", "model")

    @staticmethod
    def test(toast, url, token, model):
        """
        测试用户输入的AI服务器是否可用
        :param toast: toast通知组件，直接在此函数中调用
        :param url: 当前输入的url
        :param token: 当前输入的token
        :param model: 当前输入的model
        """
        url = url.rstrip('/') + "/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        body = {"model": model, "messages": [{"role": "user", "content": "hello"}]}

        try:
            response = requests.post(url, json=body, headers=headers).json()
            if "error" in response:
                toast.show("error", "", response["error"]["message"])
            else:
                toast.show("success", "", "测试成功")

        except Exception as e:
            toast.show("error", "", f"连接失败：{e}")
