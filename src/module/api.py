import requests
import json
import time
import arrow    # 处理时间格式


# 向 Anilist 请求数据
# https://anilist.github.io/ApiV2-GraphQL-Docs/
def anilistSearch(romaji_name):
    query = '''
    query ($id: String) {
        Media (search: $id, type: ANIME) {
            title {
                native
            }
            format
        }
    }'''

    js = {"query": query, "variables": {"id": romaji_name}}
    headers = {'accept': 'application/json'}
    url = "https://graphql.anilist.co"
    print(f"开始搜索{romaji_name}")

    for retry in range(3):
        response = requests.post(url, json=js, headers=headers)
        if response.status_code == 200:
            result = json.loads(response.text.encode().decode('unicode_escape'))  # 特殊转码
            print(f"成功获取{romaji_name}数据")

            jp_name_anilist = result["data"]["Media"]["title"]["native"]

            return jp_name_anilist
        else:
            time.sleep(0.5)
    print(f"搜索{romaji_name}失败")


# 向 Bangumi Search 请求数据(search/subject/keywords)
# https://bangumi.github.io/api/
def bangumiSearch(jp_name):
    headers = {"accept": "application/json", "User-Agent": "nuthx/bangumi-renamer"}
    url = "https://api.bgm.tv/search/subject/" + jp_name + "?type=2&responseGroup=small"
    print(f"开始搜索{jp_name}")

    for retry in range(3):
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            result = json.loads(response.text)
            print(f"成功获取{jp_name}数据")

            bgm_id = result["list"][0]["id"]
            poster = result["list"][0]["images"]["large"]
            jp_name = result["list"][0]["name"]
            cn_name = result["list"][0]["name_cn"]

            return bgm_id, poster, jp_name, cn_name
        else:
            time.sleep(0.5)
    print(f"搜索{jp_name}失败")


# 向 Bangumi Subject 请求数据(/v0/subjects/subject_id)
# https://bangumi.github.io/api/
def bangumiSubject(bgm_id, data_format):
    headers = {"accept": "application/json", "User-Agent": "nuthx/bangumi-renamer"}
    url = "https://api.bgm.tv/v0/subjects/" + str(bgm_id)
    print(f"开始搜索{bgm_id}")

    for retry in range(3):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = json.loads(response.text)
            print(f"成功获取{bgm_id}数据")

            types = result["platform"]
            release = arrow.get(result["date"]).format(data_format)  # 处理时间格式
            episodes = result["eps"]
            score = result["rating"]["score"]

            # 格式化 types
            types = types.lower()
            if types in ["tv"]:
                typecode = "01"
            elif types in ["剧场版"]:
                typecode = "02"
            elif types in ["ova", "oad"]:
                typecode = "03"
            else:
                typecode = "XBD"

            return types, typecode, release, episodes, score
        else:
            time.sleep(0.5)
    print(f"搜索{bgm_id}失败")


# 向 Bangumi Previous 请求数据(v0/subjects/subjects)
# https://bangumi.github.io/api/
def bangumiPrevious(init_id, init_name):
    headers = {"accept": "application/json", "User-Agent": "nuthx/bangumi-renamer"}
    url = "https://api.bgm.tv/v0/subjects/" + str(init_id) + "/subjects"
    print(f"开始搜索{init_name}前传")

    for retry in range(3):
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = json.loads(response.text)
            print(f"成功获取{init_name}前传")

            # 如果有前传，返回前传 prev_id 和 prev_name
            # 如果没有前传，返回原始 init_id 和 not_now_bro
            for data in result:
                if data["relation"] in ["前传", "主线故事"]:
                    prev_id = str(data["id"])
                    prev_name = data["name_cn"]
                    return prev_id, prev_name
            else:
                return init_id, init_name
        else:
            time.sleep(0.5)
    print(f"搜索{init_name}前传失败")
