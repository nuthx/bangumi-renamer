import os
import re
import anitopy
import arrow
import jieba

from src.module.api import *
from src.module.config import posterFolder, readConfig


def getRomajiName(file_name):
    # 加载文件名忽略列表
    ignored = ["BD-BOX", "BD"]

    # 将指定字符加入忽略列表，并更新 file_name为忽略后的名字
    pattern_ignored = '|'.join(ignored)
    file_name = re.sub(pattern_ignored, '', file_name)

    # anitopy 识别动画名
    aniparse_options = {'allowed_delimiters': ' .-+[]'}
    romaji_name = anitopy.parse(file_name, options=aniparse_options)

    # 如果没识别到动画名返回 None
    if "anime_title" in romaji_name:
        anime_title = romaji_name["anime_title"]
        return anime_title


def getApiInfo(anime):
    romaji_name = anime["romaji_name"]

    # Anilist
    jp_name_anilist = anilistSearch(romaji_name)
    if jp_name_anilist:
        anime["jp_name_anilist"] = jp_name_anilist
    else:
        return

    # Bangumi 搜索
    bangumi_search = bangumiSearch(anime["jp_name_anilist"], 2)
    if bangumi_search:
        anime["bgm_id"] = bangumi_search
    else:
        return

    # Bangumi 条目
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

    # Bangumi 额外搜索
    search_result = bangumiSearch(anime["init_name"], 1)
    search_clean = removeTrash(anime["init_name"], search_result)
    anime["result"] = search_clean


def removeTrash(init_name, search_list):
    # 获取列表
    name_list = []
    for item in search_list:
        anime = item["cn_name"].lower()
        name_list.append(anime)

    # jieba 分词，并计算余弦相似度
    def similarity(s1, s2):
        tokens1 = set(jieba.cut(s1))
        tokens2 = set(jieba.cut(s2))
        intersection = tokens1 & tokens2
        union = tokens1 | tokens2
        similarity_threshold = len(intersection) / len(union)
        # print(similarity_threshold)
        return similarity_threshold

    # 过滤动画列表
    result1 = []
    result2 = []
    for result in name_list:
        if similarity(result, init_name) >= 0.15:
            result1.append(result)
        else:
            result2.append(result)

    # 在 search_list 中删除排除的动画
    search_list = [item for item in search_list if item["cn_name"].lower() not in result2]
    return search_list


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
