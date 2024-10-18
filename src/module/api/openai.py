import requests

from src.module.config import readConfig


class OpenAI:
    def __init__(self):
        self.url = readConfig("AI", "url")
        self.token = readConfig("AI", "token")
        self.model = readConfig("AI", "model")

    @staticmethod
    def test(url, token, model):
        url = url.rstrip('/') + "/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {token}"}
        body = {"model": model, "messages": [{"role": "user", "content": "hello"}]}

        try:
            response = requests.post(url, json=body, headers=headers).json()
            if "error" in response:
                print(response["error"]["message"])
            else:
                print("测试成功")

        except Exception as e:
            print(f"连接失败：{e}")
