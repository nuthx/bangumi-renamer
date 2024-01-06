import os
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

    def standardAnalysis(self, anime):
        # 获取用户预留 ID 判断是否搜索收藏状态
        config = readConfig()
        user_id = config.get("Bangumi", "user_id")
        total = 7 if user_id else 6

        # 罗马名
        self.anime_state.emit([anime["list_id"], f"==> [1/{total}] 提取罗马名"])
        romaji_name = getRomajiName(anime["file_name"])
        if romaji_name:
            anime["romaji_name"] = romaji_name
        else:
            return
        self.added_progress_count.emit(1)

        # Anilist 日文名
        self.anime_state.emit([anime["list_id"], f"==> [2/{total}] 搜索日文名"])
        jp_name_anilist = getAnilistJpName(anime["romaji_name"])
        if jp_name_anilist:
            anime["jp_name_anilist"] = jp_name_anilist
        else:
            return
        self.added_progress_count.emit(1)

        # Bangumi ID
        self.anime_state.emit([anime["list_id"], f"==> [3/{total}] 搜索动画信息"])
        bgm_id = api_bgmIdSearch(anime["jp_name_anilist"])
        if bgm_id:
            anime["bgm_id"] = bgm_id
        else:
            return
        self.added_progress_count.emit(1)

        # 动画条目
        self.anime_state.emit([anime["list_id"], f"==> [4/{total}] 写入动画信息"])
        bangumi_subject = api_bgmSubject(anime["bgm_id"])
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
        self.added_progress_count.emit(1)

        # 前传
        self.anime_state.emit([anime["list_id"], f"==> [5/{total}] 搜索首季信息"])
        init_info = getInitInfo(anime["bgm_id"], anime["cn_name"])
        if init_info:
            anime["init_id"] = init_info[0]
            anime["init_name"] = init_info[1].replace("/", " ")  # 移除结果中的斜杠
        else:
            return
        self.added_progress_count.emit(1)

        # 所有季度
        self.anime_state.emit([anime["list_id"], f"==> [6/{total}] 列出所有季度"])
        cleaned_search_list = removeUnrelated(anime["init_name"], api_bgmRelated(anime["init_name"]))
        if user_id:
            self.anime_state.emit([anime["list_id"], f"==> [7/{total}] 获取收藏状态"])
            anime["result"] = checkAnimeCollection(user_id, cleaned_search_list)
            self.added_progress_count.emit(1)
        else:
            anime["result"] = cleaned_search_list
        self.added_progress_count.emit(1)

        # 主条目收藏状态
        if user_id:
            # 如果存在所有季度中，则直接获取
            for item in anime["result"]:
                if item["bgm_id"] == anime["bgm_id"]:
                    anime["collection"] = item["collection"]
                    break

            # 少数情况动画名与首季差异较大，被所有季度排除了，则重新获取收藏状态
            if "collection" not in anime:
                anime["collection"] = api_collectionCheck(user_id, anime["bgm_id"])

        # 下载图片
        downloadPoster(anime["poster"])

        # 写入重命名
        getFinalName(anime)

    def singleAnalysis(self, anime, bgm_id, search_init):
        # 获取用户预留 ID 判断是否搜索收藏状态
        config = readConfig()
        user_id = config.get("Bangumi", "user_id")

        # 罗马名
        romaji_name = getRomajiName(anime["file_name"])
        if romaji_name:
            anime["romaji_name"] = romaji_name
        else:
            return

        # 跳过：Anilist 日文名

        # Bangumi ID
        anime["bgm_id"] = bgm_id

        # 动画条目
        bangumi_subject = api_bgmSubject(bgm_id)
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
            init_info = getInitInfo(anime["bgm_id"], anime["cn_name"])
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
                    if item["bgm_id"] == anime["bgm_id"]:
                        anime["collection"] = item["collection"]
                        break

            # 少数情况动画名与首季差异较大，被所有季度排除了，则重新获取收藏状态
            if "collection" not in anime:
                anime["collection"] = api_collectionCheck(user_id, anime["bgm_id"])

        # 下载图片
        downloadPoster(anime["poster"])

        # 写入重命名
        getFinalName(anime)


def getRomajiName(file_name):
    # 忽略文件名中特殊字符
    pattern_ignored = '|'.join(["BD-BOX", "BD", "DVD", "- TV", "- TV + OAD"])
    file_name = re.sub(pattern_ignored, '', file_name)

    # anitopy 识别动画名
    aniparse_options = {'allowed_delimiters': ' .-+[]'}
    romaji_name = anitopy.parse(file_name, options=aniparse_options)

    # 如果没识别到动画名返回 None
    if "anime_title" in romaji_name:
        return romaji_name["anime_title"]
    else:
        return None


def getAnilistJpName(file_name):
    if isPureEnglish(file_name):
        return file_name

    jp_name_anilist = api_anilist(file_name)
    if jp_name_anilist:
        return jp_name_anilist
    else:
        return None


def getInitInfo(bgm_id, cn_name):
    bangumi_previous = api_bangumiInit(bgm_id, cn_name)
    prev_id = bangumi_previous[0]
    prev_name = bangumi_previous[1]

    while bgm_id != prev_id:  # 如果 ID 不同，说明有前传
        bgm_id = prev_id
        bangumi_previous = api_bangumiInit(bgm_id, prev_name)
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
    anime["collection"] = api_collectionCheck(user_id, anime["bgm_id"])


def downloadPoster(poster_url):
    poster_path = os.path.join(posterFolder(), os.path.basename(poster_url))

    # 如果存在这张海报则不下载
    if os.path.exists(poster_path):
        return

    with open(poster_path, "wb") as file:
        file.write(requests.get(poster_url).content)


def getFinalName(anime):
    config = readConfig()
    data_format = config.get("Format", "date_format")
    rename_format = config.get("Format", "rename_format")

    jp_name = anime["jp_name"]
    cn_name = anime["cn_name"]
    init_name = anime["init_name"]
    romaji_name = anime["romaji_name"]

    types = anime["types"]
    typecode = anime["typecode"]
    release = arrow.get(anime["release"]).format(data_format)
    episodes = anime["episodes"]

    score = anime["score"]
    bgm_id = anime["bgm_id"]

    # 保留 string 输出
    final_name = eval(f'f"{rename_format}"')
    anime["final_name"] = final_name
