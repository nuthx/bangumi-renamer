import os
import re
import anitopy

from src.module.api import *
from src.module.config import posterFolder, readConfig


def getRomajiName(file_name):
    # 加载文件名忽略列表
    ignored = ["BD-BOX", "BD"]

    # 将指定字符加入忽略列表，并更新 file_name为忽略后的名字
    pattern_ignored = '|'.join(ignored)
    file_name = re.sub(pattern_ignored, '', file_name)

    # 使用 anitopy 识别动画名
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

    # Bangumi Search

    bangumi_search = bangumiSearch(jp_name_anilist)
    if bangumi_search:
        anime["bgm_id"] = bangumi_search[0]
        anime["poster"] = bangumi_search[1]
        anime["jp_name"] = bangumi_search[2]
        anime["cn_name"] = bangumi_search[3]
    else:
        return

    # bangumi Subject

    bangumi_subject = bangumiSubject(anime["bgm_id"])
    if bangumi_subject:
        anime["types"] = bangumi_subject[0]
        anime["typecode"] = bangumi_subject[1]
        anime["release"] = bangumi_subject[2]
        anime["episodes"] = bangumi_subject[3]
        anime["score"] = bangumi_subject[4]
    else:
        return

    # Bangumi Previous

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
    anime["init_name"] = prev_name


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
    rename_format = config.get("Format", "rename_format")

    jp_name = anime["jp_name"]
    cn_name = anime["cn_name"]
    init_name = anime["init_name"]
    romaji_name = anime["romaji_name"]

    types = anime["types"]
    typecode = anime["typecode"]
    release = anime["release"]
    episodes = anime["episodes"]

    score = anime["score"]
    bgm_id = anime["bgm_id"]

    # 保留 string 输出
    final_name = eval(f'f"{rename_format}"')
    anime["final_name"] = final_name
