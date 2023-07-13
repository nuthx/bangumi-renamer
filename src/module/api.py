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

    js = {
        'query': query,
        'variables': {'id': romaji_name},
    }

    headers = {'accept': 'application/json'}
    print(f"正在通过Anilist搜索{romaji_name}")

    retry = 0
    while retry < 3:
        response = requests.post('https://graphql.anilist.co', json=js, headers=headers)
        if response.status_code == 200:
            result = json.loads(response.text.encode().decode('unicode_escape'))  # 特殊转码
            print(f"成功获取到{romaji_name}的Anilist数据")

            jp_name_anilist = result["data"]["Media"]["title"]["native"]

            return jp_name_anilist
        else:
            print("Anilist请求失败，重试" + str(retry + 1))
            time.sleep(0.5)
            retry += 1
    print(f"在Anilist中搜索{romaji_name}失败")


# 向 Bangumi Search 请求数据(search/subject/keywords)
# https://bangumi.github.io/api/
def bangumiSearch(a_jp_name):
    headers = {
        'accept': 'application/json',
        'User-Agent': 'nuthx/bangumi-renamer'
    }

    url = "https://api.bgm.tv/search/subject/" + a_jp_name + "?type=2&responseGroup=small"
    print(f"正在通过Bangumi搜索{a_jp_name}")

    retry = 0
    while retry < 3:
        response = requests.post(url, headers=headers)
        if response.status_code == 200:
            result = json.loads(response.text)
            print(f"成功获取到{a_jp_name}的Bangumi数据")

            bgm_id = result["list"][0]["id"]
            poster = result["list"][0]["images"]["large"]
            jp_name = result["list"][0]["name"]
            cn_name = result["list"][0]["name_cn"]


            return bgm_id, poster, jp_name, cn_name
        else:
            print("Bangumi搜索失败，重试" + str(retry + 1))
            time.sleep(0.5)
            retry += 1
    print(f"在Bangumi中搜索{a_jp_name}失败")


# 向 Bangumi Subject 请求数据(/v0/subjects/subject_id)
# https://bangumi.github.io/api/
def bangumiSubject(b_id):
    headers = {
        'accept': 'application/json',
        'User-Agent': 'nuthx/bangumi-renamer'
    }

    url = "https://api.bgm.tv/v0/subjects/" + str(b_id)
    print(f"正在向Bangumi请求ID {b_id}的详细信息")

    retry = 0
    while retry < 3:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = json.loads(response.text)
            print(f"成功获取到ID {b_id}的详细信息")

            types = result["platform"]
            release = arrow.get(result["date"]).format("YYMMDD")  # 处理时间格式
            episodes = result["eps"]
            score = result["rating"]["score"]

            # 格式化 b_type
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
            print("Bangumi请求更多失败，重试" + str(retry + 1))
            time.sleep(0.5)
            retry += 1
    print(f"向Bangumi请求ID {b_id}的详细信息失败")


# 向 Bangumi Previous 请求数据(v0/subjects/subjects)
# https://bangumi.github.io/api/
def bangumiPrevious(init_id, init_name):
    headers = {
        'accept': 'application/json',
        'User-Agent': 'nuthx/bangumi-renamer'
    }

    url = "https://api.bgm.tv/v0/subjects/" + str(init_id) + "/subjects"

    retry = 0
    while retry < 3:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            result = json.loads(response.text)

            # 检测改动画 ID 是否有前传内容
            # 如果有，返回前传 prev_id 和 prev_name
            # 如果没有，返回原始 init_id 和 not_now_bro
            for data in result:
                if data["relation"] == "前传":
                    prev_id = str(data["id"])
                    prev_name = data["name_cn"]
                    return prev_id, prev_name
            else:
                return init_id, init_name
        else:
            print("Bangumi请求上一季度信息失败，重试" + str(retry + 1))
            time.sleep(0.5)
            retry += 1
