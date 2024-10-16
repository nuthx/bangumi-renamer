import re
import requests


# https://anilist.github.io/ApiV2-GraphQL-Docs
def anilistSearch(romaji_name):
    """
    在anilist搜索动画名
    :param romaji_name: 动画罗马音文件名
    :return: 动画日文名(已清理)
    """
    query = "query ($id: String) {Media (search: $id, type: ANIME) {title {native}}}"
    js = {"query": query, "variables": {"id": romaji_name}}
    headers = {'accept': 'application/json'}
    url = "https://graphql.anilist.co"

    try:
        result = requests.post(url, json=js, headers=headers).json()

        name_jp_anilist = result["data"]["Media"]["title"]["native"]
        name_jp_anilist = re.sub(r'（[^）]*）', '', name_jp_anilist).strip()  # 移除括号内容，例 22/7 （ナナブンノニジュウニ）

        return name_jp_anilist

    except Exception as e:
        print(f"anilistSearch - {romaji_name}: {e}")
        return
