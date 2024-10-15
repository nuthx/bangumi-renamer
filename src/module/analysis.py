import os
import time
import anitopy
import arrow
import threading
from fuzzywuzzy import fuzz
from nltk.corpus import words

from PySide6.QtCore import QObject, Signal

from src.module.apis import *
from src.module.api.anilist import anilistSearch
from src.module.api.bangumi_link import bangumiLinkRelate
from src.module.config import posterFolder, readConfig


class Analysis(QObject):
    main_state = Signal(str)
    anime_state = Signal(list)
    added_progress_count = Signal(int)

    def __init__(self):
        super().__init__()
        self.total_process = 6

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
        bangumi_id = api_bgmIdSearch(anime["name_jp_anilist"])

        if bangumi_id:
            anime["bangumi_id"] = bangumi_id
            self.added_progress_count.emit(1)
        else:
            self.added_progress_count.emit(self.total_process - 3)
            return

        # 4. 搜索动画详细信息
        self.anime_state.emit([anime["id"], f"==> [4/{self.total_process}] 搜索动画信息"])
        bangumi_subject = api_bgmSubject(anime["bangumi_id"])

        if bangumi_subject:
            anime["poster"] = bangumi_subject[0]
            anime["jp_name"] = bangumi_subject[1].replace("/", " ")  # 移除结果中的斜杠
            anime["cn_name"] = bangumi_subject[2].replace("/", " ")  # 移除结果中的斜杠
            anime["types"] = bangumi_subject[3]
            anime["typecode"] = bangumi_subject[4]
            anime["release"] = bangumi_subject[5]
            anime["episodes"] = bangumi_subject[6]
            anime["score"] = bangumi_subject[7]
            self.added_progress_count.emit(1)
        else:
            self.added_progress_count.emit(self.total_process - 4)
            return

        # 5. 搜索关联条目
        self.anime_state.emit([anime["id"], f"==> [5/{self.total_process}] 搜索关联条目"])
        relate = getRelate(anime["bangumi_id"])

        if relate:
            anime["fs_id"] = relate[0]
            anime["fs_name_cn"] = relate[1]
            anime["relate"] = relate[2]
            self.added_progress_count.emit(1)
        else:
            self.added_progress_count.emit(self.total_process - 5)
            return

        # 6. 下载海报
        downloadPoster(anime["poster"])

        # 7. 写入重命名结果
        # getFinalName(anime)

    def singleAnalysis(self, anime, bangumi_id, search_init):
        # 获取用户预留 ID 判断是否搜索收藏状态
        user_id = readConfig("Bangumi", "user_id")

        # 罗马名
        romaji_name = getRomaji(anime["file_name"])
        if romaji_name:
            anime["romaji_name"] = romaji_name
        else:
            return

        # 跳过：Anilist 日文名

        # Bangumi ID
        anime["bangumi_id"] = bangumi_id

        # 动画条目
        bangumi_subject = api_bgmSubject(bangumi_id)
        if bangumi_subject:
            anime["poster"] = bangumi_subject[0]
            anime["jp_name"] = bangumi_subject[1].replace("/", " ")  # 移除结果中的斜杠
            anime["cn_name"] = bangumi_subject[2].replace("/", " ")  # 移除结果中的斜杠
            anime["types"] = bangumi_subject[3]
            anime["typecode"] = bangumi_subject[4]
            anime["release"] = bangumi_subject[5]
            anime["episodes"] = bangumi_subject[6]
            anime["score"] = bangumi_subject[7]
        else:
            return

        # 前传（可选）
        if search_init:
            init_info = getRelate(anime["bangumi_id"])
            if init_info:
                anime["init_id"] = init_info[0]
                anime["init_name"] = init_info[1].replace("/", " ")  # 移除结果中的斜杠
            else:
                return

        # 跳过：所有季度

        # 主条目收藏状态
        if user_id:
            # 如果存在所有季度中，则直接获取
            if "result" in anime:
                for item in anime["result"]:
                    if item["bangumi_id"] == anime["bangumi_id"]:
                        anime["collection"] = item["collection"]
                        break

            # 少数情况动画名与首季差异较大，被所有季度排除了，则重新获取收藏状态
            if "collection" not in anime:
                anime["collection"] = api_collectionCheck(user_id, anime["bangumi_id"])

        # 下载图片
        downloadPoster(anime["poster"])

        # 写入重命名
        getFinalName(anime)


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


def getRelate(bangumi_id):
    """
    使用bangumi link获取动画首季的信息
    :param bangumi_id: Bangumi ID
    :return: [首季id, 首季名称(中)]
    """
    result = bangumiLinkRelate(bangumi_id)

    if result:
        result_anime = [item for item in result if item["type"] == 2]  # 只保留动画，移除小说、游戏等类别
        result_anime = [item for item in result_anime if item["platform"] != "WEB"]  # 移除web类别
        result_fs = next((item for item in result_anime if item["platform"] == "TV"), None)  # 搜索首季动画
        return result_fs["id"], result_fs["nameCN"], result_anime
    else:
        return


def downloadPoster(poster_url):
    poster_path = os.path.join(posterFolder(), os.path.basename(poster_url))

    # 如果存在这张海报则不下载
    if os.path.exists(poster_path):
        return

    with open(poster_path, "wb") as file:
        file.write(requests.get(poster_url).content)


def getFinalName(anime):
    data_format = readConfig("Format", "date_format")
    rename_format = readConfig("Format", "rename_format")

    jp_name = anime["jp_name"]
    cn_name = anime["cn_name"]
    init_name = anime["init_name"]
    romaji_name = anime["romaji_name"]

    types = anime["types"]
    typecode = anime["typecode"]
    release = arrow.get(anime["release"]).format(data_format)
    episodes = anime["episodes"]

    score = anime["score"]
    bangumi_id = anime["bangumi_id"]

    # 保留 string 输出
    final_name = eval(f'f"{rename_format}"')
    anime["final_name"] = final_name
