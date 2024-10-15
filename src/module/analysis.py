import os
import re
import arrow
import anitopy
import requests

from PySide6.QtCore import QObject, Signal

from src.module.api.anilist import anilistSearch
from src.module.api.bangumi import bangumiIDSearch, bangumiSubject
from src.module.api.bangumi_link import bangumiLink
from src.module.config import posterFolder, readConfig


class Analysis(QObject):
    main_state = Signal(str)
    anime_state = Signal(list)
    added_progress_count = Signal(int)

    def __init__(self):
        super().__init__()
        self.total_process = 6

    # TODO: 整合singleAnalysis
    def start(self, anime):
        """
        完整分析动画的详细信息，下载海报图片，并根据配置项生成重命名结果
        :param anime: 动画信息字典
        :return: 仅在分析失败时return None
        """
        # 1. 提取罗马名
        self.anime_state.emit([anime["id"], f"==> [1/{self.total_process}] 提取罗马名"])
        name_romaji = getRomaji(anime["file_name"])

        if name_romaji:
            anime["name_romaji"] = name_romaji
            self.added_progress_count.emit(1)
        else:
            self.added_progress_count.emit(self.total_process - 1)
            return

        # 2. 使用anilist搜索日文名
        self.anime_state.emit([anime["id"], f"==> [2/{self.total_process}] 搜索日文名"])
        name_jp_anilist = anilistSearch(anime["name_romaji"])

        if name_jp_anilist:
            anime["name_jp_anilist"] = name_jp_anilist
            self.added_progress_count.emit(1)
        else:
            self.added_progress_count.emit(self.total_process - 2)
            return

        # 3. 搜索bangumi id
        self.anime_state.emit([anime["id"], f"==> [3/{self.total_process}] 搜索动画条目"])
        bangumi_id = bangumiIDSearch(anime["name_jp_anilist"])

        if bangumi_id:
            anime["bangumi_id"] = bangumi_id
            self.added_progress_count.emit(1)
        else:
            self.added_progress_count.emit(self.total_process - 3)
            return

        # 4. 搜索动画详细信息
        self.anime_state.emit([anime["id"], f"==> [4/{self.total_process}] 搜索动画信息"])
        bangumi_subject = bangumiSubject(anime["bangumi_id"])

        if bangumi_subject:
            anime["name_jp"] = bangumi_subject["name_jp"].replace("/", " ")  # 移除结果中的斜杠
            anime["name_cn"] = bangumi_subject["name_cn"].replace("/", " ")  # 移除结果中的斜杠
            anime["poster"] = bangumi_subject["poster"]
            anime["type"] = bangumi_subject["type"]
            anime["typecode"] = bangumi_subject["typecode"]
            anime["release_raw"] = bangumi_subject["release_raw"]
            anime["release_end_raw"] = bangumi_subject["release_end_raw"]
            anime["release_week"] = bangumi_subject["release_week"]
            anime["episodes"] = bangumi_subject["episodes"]
            anime["score"] = bangumi_subject["score"]
            self.added_progress_count.emit(1)
        else:
            self.added_progress_count.emit(self.total_process - 4)
            return

        # 5. 搜索关联条目
        self.anime_state.emit([anime["id"], f"==> [5/{self.total_process}] 搜索关联条目"])
        relate_anime = bangumiLink(anime)

        if relate_anime:
            # 搜索首季TV，如果没有则返回第一个项目(如剧场版)
            fs_anime = next((item for item in relate_anime if item["platform"] == "TV"), relate_anime[0])
            anime["fs_id"] = fs_anime["id"]
            anime["fs_name_cn"] = fs_anime["nameCN"]
            anime["relate"] = relate_anime
            self.added_progress_count.emit(1)
        else:
            self.added_progress_count.emit(self.total_process - 5)
            return

        # 6. 下载海报
        downloadPoster(anime["poster"])

        # 7. 写入重命名(由于在其他位置调用，因此直接在函数内写入内容到anime)
        getFinal(anime)

    # def singleAnalysis(self, anime, bangumi_id, search_init):
    #     # 获取用户预留 ID 判断是否搜索收藏状态
    #     user_id = readConfig("Bangumi", "user_id")
    #
    #     # 罗马名
    #     romaji_name = getRomaji(anime["file_name"])
    #     if romaji_name:
    #         anime["romaji_name"] = romaji_name
    #     else:
    #         return
    #
    #     # 跳过：Anilist 日文名
    #
    #     # Bangumi ID
    #     anime["bangumi_id"] = bangumi_id
    #
    #     # 动画条目
    #     bangumi_subject = api_bgmSubject(bangumi_id)
    #     if bangumi_subject:
    #         anime["poster"] = bangumi_subject[0]
    #         anime["jp_name"] = bangumi_subject[1].replace("/", " ")  # 移除结果中的斜杠
    #         anime["cn_name"] = bangumi_subject[2].replace("/", " ")  # 移除结果中的斜杠
    #         anime["types"] = bangumi_subject[3]
    #         anime["typecode"] = bangumi_subject[4]
    #         anime["release"] = bangumi_subject[5]
    #         anime["episodes"] = bangumi_subject[6]
    #         anime["score"] = bangumi_subject[7]
    #     else:
    #         return
    #
    #     # 前传（可选）
    #     # if search_init:
    #     #     init_info = getRelate(anime["bangumi_id"])
    #     #     if init_info:
    #     #         anime["init_id"] = init_info[0]
    #     #         anime["init_name"] = init_info[1].replace("/", " ")  # 移除结果中的斜杠
    #     #     else:
    #     #         return
    #
    #     # 跳过：所有季度
    #
    #     # 主条目收藏状态
    #     if user_id:
    #         # 如果存在所有季度中，则直接获取
    #         if "result" in anime:
    #             for item in anime["result"]:
    #                 if item["bangumi_id"] == anime["bangumi_id"]:
    #                     anime["collection"] = item["collection"]
    #                     break
    #
    #         # 少数情况动画名与首季差异较大，被所有季度排除了，则重新获取收藏状态
    #         if "collection" not in anime:
    #             anime["collection"] = api_collectionCheck(user_id, anime["bangumi_id"])
    #
    #     # 下载图片
    #     downloadPoster(anime["poster"])
    #
    #     # 写入重命名(由于在其他位置调用，因此直接在函数内写入内容到anime)
    #     getFinal(anime)


def getRomaji(file_name):
    """
    根据文件名，使用anitopy提取动画名
    :param file_name: 完整的文件名
    :return: 动画罗马名，若无法识别则返回None
    """
    # 忽略文件名中特殊字符
    pattern_ignored = '|'.join(["BD-BOX", "BD", "DVD", "- TV", "- TV + OAD"])
    file_name = re.sub(pattern_ignored, '', file_name)

    # anitopy 识别动画名
    aniparse_options = {'allowed_delimiters': ' .-+[]'}
    romaji_name = anitopy.parse(file_name, options=aniparse_options)

    if "anime_title" in romaji_name:
        return romaji_name["anime_title"]
    else:
        return


def downloadPoster(poster_url):
    """
    下载海报，保存到指定地址
    :param poster_url: 海报图片地址
    """
    poster_path = os.path.join(posterFolder(), os.path.basename(poster_url))

    # 如果存在这张海报则不下载
    if os.path.exists(poster_path):
        return

    with open(poster_path, "wb") as file:
        file.write(requests.get(poster_url).content)


def getFinal(anime):
    """
    根据配置文件，导出文件的最终名称，直接将新值写入anime
    :param anime: 动画详情
    """
    data_format = readConfig("Format", "date_format")
    rename_format = readConfig("Format", "rename_format")

    # 格式化release日期到字典
    anime["release"] = arrow.get(anime["release_raw"]).format(data_format)
    anime["release_end"] = arrow.get(anime["release_end_raw"]).format(data_format)

    # 写入final_name到字典
    rename_format_final = rename_format.format(**anime)  # 替换为anime字典中对应值
    final_name = eval(f'f"{rename_format_final}"')
    anime["final_name"] = final_name

    # 写入final_dir到字典
    final_dir = os.path.dirname(anime["file_path"])
    anime["final_dir"] = final_dir

    # 写入final_path到字典
    final_path = os.path.join(final_dir, os.path.normpath(final_name))  # 保证路径在windows下合法化
    anime["final_path"] = final_path
