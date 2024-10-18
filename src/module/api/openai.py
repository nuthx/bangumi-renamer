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

    def getRomaji(self, file_name):
        """
        使用AI提取文件的罗马名
        :param file_name: 原始文件名
        :return: 识别成功则返回罗马名，否则返回None
        """
        prompt = """\
        You will now play the role of a super assistant.
        Your task is to extract structured data from unstructured text content and output the anime romaji name in string ONLY.
        If you are unable to extract any information, please return '' WITHOUT FABRICATE DATA!

        Example:

        ```
        input: "[Deadmau- RAWS] Pandora.Hearts.S01.Specials.2009.X264.AC3.DVDRip-AVC.Deadmauvlad"
        output: "Pandora Hearts"

        input: "[Moozzi2] World Trigger S2 BD-BOX [ x265-10Bit Ver. ] - TV + SP"
        output: "World Trigger S2"

        input: "[Nekomoe kissaten][Shikanoko Nokonoko Koshitantanl]["
        output: "Shikanoko Nokonoko Koshitantanl"
        ```
        """

        url = self.url.rstrip('/') + "/v1/chat/completions"
        headers = {"Content-Type": "application/json", "Authorization": f"Bearer {self.token}"}
        body = {
            "model": self.model,
            "messages": [{"role": "system", "content": prompt}, {"role": "user", "content": file_name}]
        }

        try:
            response = requests.post(url, json=body, headers=headers).json()
            content = response["choices"][0]["message"]["content"].replace("\"", "").replace("\'", "")
            return content

        except Exception as e:
            print(f"OpenAI - {file_name}: {e}")
            return None
