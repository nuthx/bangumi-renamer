import re
import anitopy

from src.module.api import *


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
        anime["bgm_image"] = bangumi_search[1]
        anime["jp_name"] = bangumi_search[2]
        anime["cn_name"] = bangumi_search[3]
    else:
        return

    # bangumi Subject

    bangumi_subject = bangumiSubject(anime["bgm_id"])
    if bangumi_subject:
        anime["bgm_type"] = bangumi_subject[0]
        anime["bgm_typecode"] = bangumi_subject[1]
        anime["release_date"] = bangumi_subject[2]
        anime["episodes"] = bangumi_subject[3]
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

    anime["initial_id"] = prev_id
    anime["initial_name"] = prev_name


def getFinalName(anime):
    # 写入命名结果
    b_id = this_anime_dict["b_id"]
    romaji_name = this_anime_dict["romaji_name"]
    b_jp_name = this_anime_dict["b_jp_name"]
    b_cn_name = this_anime_dict["b_cn_name"]
    b_initial_name = this_anime_dict["b_initial_name"]
    b_type = this_anime_dict["b_type"]
    b_typecode = this_anime_dict["b_typecode"]
    b_release_date = this_anime_dict["b_release_date"]
    b_episodes = this_anime_dict["b_episodes"]

    final_name = eval(f'f"{name_type}"')  # 保留 string 输出
    return final_name

    anime["final_name"] = final_name
