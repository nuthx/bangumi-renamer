import os

from PySide6.QtCore import QObject


class Rename(QObject):
    @staticmethod
    def check(anime_list):
        """
        重命名条件检查
        :param anime_list: 动画列表
        :return: 如果不满足重命名条件，返回错误信息
        """
        final_path_list = [anime["final_path"] for anime in anime_list]

        if not anime_list:
            return "请先添加动画"

        if len(set(final_path_list)) == 1 and len(final_path_list) != 1:  # 排除只有一个动画的情况
            return "请先开始分析"

        if len(set(final_path_list)) != len(final_path_list):
            return "存在重复的重命名结果"

        # if "" in final_path_list:
        #     return "存在分析失败的动画，请先移除"

        for anime in anime_list:
            if os.path.commonpath([anime["file_name"]]) == os.path.commonpath([anime["file_name"], anime["final_name"]]):
                return f"无法将动画重命名到其子目录中：{anime['name_cn']}"

    @staticmethod
    def start(anime_list):
        # 开始命名
        for anime in anime_list:
            if anime["final_name"] != "":
                current_path = anime["file_path"]
                final_path = anime["final_path"]

                # 确保final_path存在
                if not os.path.exists(os.path.dirname(final_path)):
                    os.makedirs(os.path.dirname(final_path))

                # 重命名
                os.rename(current_path, final_path)
