import os
import time
import anitopy
import arrow
import threading
from fuzzywuzzy import fuzz
from nltk.corpus import words

from PySide6.QtCore import QObject, Signal

from src.module.api import *
from src.module.config import posterFolder, readConfig


class Analysis(QObject):
    main_state = Signal(str)
    anime_state = Signal(list)
    added_progress_count = Signal(int)

    def __init__(self):
        super().__init__()
        self.user_id = readConfig("Bangumi", "user_id")
        self.total_process = 7 if self.user_id else 6  # 根据id存在情况，判断是否搜索用户收藏状态

    def standardAnalysis(self, anime):
        """
        完整分析动画的详细信息，下载海报图片，并根据配置项生成重命名结果
        :param anime: 动画信息字典
        :return: 仅在分析失败时return None
        """
        # 1. 提取罗马名
        self.anime_state.emit([anime["id"], f"==> [1/{self.total_process}] 提取罗马名"])
        name_romaji = getNameRomaji(anime["file_name"])

        if name_romaji:
            anime["name_romaji"] = name_romaji
            self.added_progress_count.emit(1)
        else:
            self.added_progress_count.emit(self.total_process - 1)
            return

        # 2. 使用anilist搜索日文名
        self.anime_state.emit([anime["id"], f"==> [2/{self.total_process}] 搜索日文名"])
        name_jp_anilist = getNameJPAnilist(anime["name_romaji"])

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

        # 5. 搜索前传与续集
        self.anime_state.emit([anime["id"], f"==> [5/{self.total_process}] 搜索关联条目"])
        init_info = getInitInfo(anime["bangumi_id"], anime["cn_name"])

        if init_info:
            anime["init_id"] = init_info[0]
            anime["init_name"] = init_info[1].replace("/", " ")  # 移除结果中的斜杠
        else:
            return
        self.added_progress_count.emit(1)

        # 所有季度
        self.anime_state.emit([anime["id"], f"==> [6/{self.total_process}] 列出所有季度"])
        cleaned_search_list = removeUnrelated(anime["init_name"], api_bgmRelated(anime["init_name"]))
        if self.user_id:
            self.anime_state.emit([anime["id"], f"==> [7/{self.total_process}] 获取收藏状态"])
            anime["result"] = checkAnimeCollection(self.user_id, cleaned_search_list)
            self.added_progress_count.emit(1)
        else:
            anime["result"] = cleaned_search_list
        self.added_progress_count.emit(1)

        # 主条目收藏状态
        if self.user_id:
            # 如果存在所有季度中，则直接获取
            for item in anime["result"]:
                if item["bangumi_id"] == anime["bangumi_id"]:
                    anime["collection"] = item["collection"]
                    break

            # 少数情况动画名与首季差异较大，被所有季度排除了，则重新获取收藏状态
            if "collection" not in anime:
                anime["collection"] = api_collectionCheck(self.user_id, anime["bangumi_id"])

        # 下载图片
        downloadPoster(anime["poster"])

        # 写入重命名
        getFinalName(anime)

    def singleAnalysis(self, anime, bangumi_id, search_init):
        # 获取用户预留 ID 判断是否搜索收藏状态
        user_id = readConfig("Bangumi", "user_id")

        # 罗马名
        romaji_name = getNameRomaji(anime["file_name"])
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
            init_info = getInitInfo(anime["bangumi_id"], anime["cn_name"])
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


def getNameRomaji(file_name):
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


def getNameJPAnilist(name_romaji):
    if isPureEnglish(name_romaji):
        return name_romaji

    jp_name_anilist = api_anilist(name_romaji)
    if jp_name_anilist:
        return jp_name_anilist
    else:
        return


def getInitInfo(bangumi_id, cn_name):
    bangumi_previous = api_bangumiInit(bangumi_id, cn_name)
    prev_id = bangumi_previous[0]
    prev_name = bangumi_previous[1]

    while bangumi_id != prev_id:  # 如果 ID 不同，说明有前传
        bangumi_id = prev_id
        bangumi_previous = api_bangumiInit(bangumi_id, prev_name)
        prev_id = bangumi_previous[0]
        prev_name = bangumi_previous[1]

    return prev_id, prev_name


def isPureEnglish(name):
    name = name.replace(".", " ")
    try:
        for word in name.split():
            if word.lower() not in words.words():
                return False
    except Exception as e:
        # print(f"nltk异常，即将重试 ({e})")
        time.sleep(0.2)
        return isPureEnglish(name)
    return True


def removeUnrelated(init_name, search_list):
    if not search_list:
        return

    # 获取全部列表
    init_name = init_name.lower()
    name_list = [item["cn_name"].lower() for item in search_list]

    # fuzzywuzzy 模糊匹配
    name_list_related = []
    for name in name_list:
        if fuzz.partial_ratio(init_name, name) > 90:
            name_list_related.append(name)

    # 在 search_list 中删除排除的动画
    search_list_related = []
    for item in search_list:
        if item["cn_name"].lower() in name_list_related:
            search_list_related.append(item)

    return search_list_related


def checkAnimeCollection(user_id, anime_list):
    threads = []
    for anime in anime_list:
        thread = threading.Thread(target=ThreadCheckAnimeCollection, args=(anime, user_id,))
        thread.start()
        threads.append(thread)

    # 等待线程完成
    for thread in threads:
        thread.join()

    return anime_list


def ThreadCheckAnimeCollection(anime, user_id):
    anime["collection"] = api_collectionCheck(user_id, anime["bangumi_id"])


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
