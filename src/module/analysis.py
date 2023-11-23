import os
import anitopy
import arrow
from fuzzywuzzy import fuzz
from nltk.corpus import words

from PySide6.QtCore import QObject, Signal

from src.module.api import *
from src.module.config import posterFolder, readConfig


class Analysis(QObject):
    anime_state = Signal(list)
    added_progress_count = Signal(int)

    def standardAnalysis(self, anime):
        romaji_name = anime["romaji_name"]

        # Anilist
        self.added_progress_count.emit(1)
        self.anime_state.emit([anime["list_id"], "==> [2/6] 搜索日文名"])
        if isPureEnglish(romaji_name):
            anime["jp_name_anilist"] = romaji_name
        else:
            jp_name_anilist = anilistSearch(romaji_name)
            if jp_name_anilist:
                anime["jp_name_anilist"] = jp_name_anilist
            else:
                return

        # Bangumi ID
        self.added_progress_count.emit(1)
        self.anime_state.emit([anime["list_id"], "==> [3/6] 搜索动画信息"])
        bangumi_search_id = bangumiSearchId(anime["jp_name_anilist"])
        if bangumi_search_id:
            anime["bgm_id"] = bangumi_search_id
        else:
            return

        # Bangumi 条目
        self.added_progress_count.emit(1)
        self.anime_state.emit([anime["list_id"], "==> [4/6] 写入动画信息"])
        bangumi_subject = bangumiSubject(anime["bgm_id"])
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

        # Bangumi 前传
        self.added_progress_count.emit(1)
        self.anime_state.emit([anime["list_id"], "==> [5/6] 搜索首季信息"])
        bgm_id = anime["bgm_id"]
        bangumi_previous = bangumiPrevious(bgm_id, anime["cn_name"])
        prev_id = bangumi_previous[0]
        prev_name = bangumi_previous[1]

        while bgm_id != prev_id:  # 如果 ID 不同，说明有前传
            bgm_id = prev_id
            bangumi_previous = bangumiPrevious(bgm_id, prev_name)
            prev_id = bangumi_previous[0]
            prev_name = bangumi_previous[1]

        anime["init_id"] = prev_id
        anime["init_name"] = prev_name.replace("/", " ")  # 移除结果中的斜杠

        # Bangumi 搜索
        self.added_progress_count.emit(1)
        self.anime_state.emit([anime["list_id"], "==> [6/6] 列出所有季度"])
        search_result = bangumiSearch(anime["init_name"])
        search_clean = removeUnrelated(anime["init_name"], search_result)
        if search_clean:
            anime["result"] = search_clean
        else:
            return


def getRomajiName(file_name):
    # 忽略文件名中特殊字符
    pattern_ignored = '|'.join(["BD-BOX", "BD", "DVD", "- TV"])
    file_name = re.sub(pattern_ignored, '', file_name)

    # anitopy 识别动画名
    aniparse_options = {'allowed_delimiters': ' .-+[]'}
    romaji_name = anitopy.parse(file_name, options=aniparse_options)

    # 如果没识别到动画名返回 None
    if "anime_title" in romaji_name:
        anime_title = romaji_name["anime_title"]
        return anime_title


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


def downloadPoster(anime):
    poster_url = anime["poster"]
    poster_name = os.path.basename(poster_url)
    poster_folder = posterFolder()
    poster_path = os.path.join(poster_folder, poster_name)

    # 如果存在这张海报则不下载
    if os.path.exists(poster_path):
        return

    response = requests.get(poster_url)
    with open(poster_path, "wb") as file:
        file.write(response.content)


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
