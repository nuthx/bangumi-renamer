import re
import requests

from src.module.utils import log


# Bangumi ID
# https://bangumi.github.io/api/
def api_bgmIdSearch(jp_name):
    jp_name = jp_name.replace("!", " ").replace("-", " ").replace("/", " ").strip()  # 搜索时移除特殊符号避免报错

    headers = {"accept": "application/json", "User-Agent": "nuthx/bangumi-renamer"}
    url = "https://api.bgm.tv/search/subject/" + jp_name + "?type=2&responseGroup=large&max_results=25"

    try:
        result = requests.post(url, headers=headers).json()

        # 搜索无结果，则返回空内容
        if "code" in result and result["code"] == 404:
            return

        return result["list"][0]["id"]

    except Exception as e:
        log(e)
        return


# Bangumi 条目
def api_bgmSubject(bgm_id):
    headers = {"accept": "application/json", "User-Agent": "nuthx/bangumi-renamer"}
    url = "https://api.bgm.tv/v0/subjects/" + str(bgm_id)

    try:
        result = requests.get(url, headers=headers).json()

        # 搜索无结果，则返回空内容
        if "code" in result and result["code"] == 404:
            return

        poster = result["images"]["medium"]
        jp_name = result["name"]
        cn_name = result["name_cn"] if result["name_cn"] else result["name"]
        release = result["date"] if result["date"] else "1000-01-01"
        episodes = result["eps"] if result["eps"] else "0"
        score = format(float(result["rating"]["score"]), ".1f")

        types = result["platform"]

        if types in ["TV"]:
            typecode = "01"
        elif types in ["剧场版"]:
            typecode = "02"
        elif types in ["OVA", "OAD"]:
            typecode = "03"
        else:
            typecode = "XBD"

        return poster, jp_name, cn_name, types, typecode, release, episodes, score

    except Exception as e:
        log(e)
        return


# Bangumi 前传
def api_bangumiInit(init_id, init_name):
    headers = {"accept": "application/json", "User-Agent": "nuthx/bangumi-renamer"}
    url = "https://api.bgm.tv/v0/subjects/" + str(init_id) + "/subjects"

    try:
        result = requests.get(url, headers=headers).json()

        # 如果有前传，返回前传 prev_id 和 prev_name
        # 如果没有前传，返回原始 init_id 和 not_now_bro
        for data in result:
            if data["relation"] in ["前传", "主线故事", "全集"]:
                prev_id = str(data["id"])
                prev_name = data["name_cn"] if data["name_cn"] else data["name"]
                return prev_id, prev_name
        else:
            return init_id, init_name

    except Exception as e:
        log(e)
        return


# Bangumi 搜索
def api_bgmRelated(jp_name):
    jp_name = jp_name.replace("!", " ").replace("-", " ").replace("/", " ").strip()  # 搜索时移除特殊符号避免报错

    headers = {"accept": "application/json", "User-Agent": "nuthx/bangumi-renamer"}
    url = "https://api.bgm.tv/search/subject/" + jp_name + "?type=2&responseGroup=large&max_results=25"

    try:
        result = requests.post(url, headers=headers).json()

        # 搜索无结果，则返回空内容
        if "code" in result and result["code"] == 404:
            return

        result_full = []
        result_len = len(result['list'])

        for i in range(result_len):
            # 跳过无日期的条目
            if not result["list"][i]["air_date"] or result["list"][i]["air_date"] == "0000-00-00":
                continue

            # 跳过无内容的条目
            if result["list"][i]["name_cn"] == "":
                continue

            # 添加字典
            entry = {"bgm_id": result["list"][i]["id"],
                     "cn_name": result["list"][i]["name_cn"],
                     "release": result["list"][i]["air_date"]}
            result_full.append(entry)

        result_full = [item for item in result_full if item]  # 移除空字典
        result_full = sorted(result_full, key=lambda x: x["release"])  # 按放送日期排序

        return result_full

    except Exception as e:
        log(e)
        return


def api_collectionCheck(user_id, anime_id):
    headers = {"accept": "application/json", "User-Agent": "nuthx/bangumi-renamer"}
    url = "https://api.bgm.tv/v0/users/" + str(user_id) + "/collections/" + str(anime_id)

    try:
        result = requests.get(url, headers=headers).json()

        if "type" in result:
            if result["type"] == 1:
                collection = "想看"
            elif result["type"] == 2:
                collection = "看过"
            elif result["type"] == 3:
                collection = "在看"
            elif result["type"] == 4:
                collection = "搁置"
            else:
                collection = "抛弃"
        else:
            collection = ""

        return collection

    except Exception as e:
        log(e)
        return
