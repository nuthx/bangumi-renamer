import requests
import json
import time     # 延迟操作
import arrow    # 处理时间格式


# 向 Anilist 请求数据
# https://anilist.github.io/ApiV2-GraphQL-Docs/
def anilist(romaji_name):
    headers = {
        'accept': 'application/json',
    }

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

    print(f"正在通过Anilist搜索{romaji_name}")

    # 3次重试机会，避免网络原因导致请求失败
    retry = 0
    while retry < 3:
        response = requests.post('https://graphql.anilist.co', json=js, headers=headers)

        if response.status_code == 200:
            result = json.loads(response.text.encode().decode('unicode_escape'))
            print(f"成功获取到{romaji_name}的Anilist数据")

            a_jp_name = result["data"]["Media"]["title"]["native"]
            a_type = result["data"]["Media"]["format"]

            a_dict = dict()
            a_dict["a_jp_name"] = a_jp_name
            a_dict["a_type"] = a_type
            return a_dict

        # 若请求失败，等待0.5秒重试
        else:
            print("Anilist请求失败，重试" + str(retry + 1))
            time.sleep(0.5)
            retry += 1

    print(f"在Anilist中搜索{romaji_name}失败")

# 向 Bangumi Search 请求数据(search/subject/keywords)
# https://bangumi.github.io/api/
def bangumi_search(a_jp_name):
    headers = {
        'accept': 'application/json',
        'User-Agent': 'akko/bgm-renamer'
    }

    url = "https://api.bgm.tv/search/subject/" + a_jp_name + "?type=2&responseGroup=small"
    print(f"正在通过Bangumi搜索{a_jp_name}")
    
    # 3次重试机会，避免网络原因导致请求失败
    retry = 0
    while retry < 3:
        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            result = json.loads(response.text)
            print(f"成功获取到{a_jp_name}的Bangumi数据")

            b_id = result["list"][0]["id"]
            b_jp_name = result["list"][0]["name"]
            b_cn_name = result["list"][0]["name_cn"]
            b_image = result["list"][0]["images"]["large"]

            b_dict = dict()
            b_dict["b_id"] = b_id
            b_dict["b_jp_name"] = b_jp_name
            b_dict["b_cn_name"] = b_cn_name
            b_dict["b_image"] = b_image
            return b_dict

        # 若请求失败，等待0.5秒重试
        else:
            print("Bangumi搜索失败，重试" + str(retry + 1))
            time.sleep(0.5)
            retry += 1

    print(f"在Bangumi中搜索{a_jp_name}失败")

# 向 Bangumi Subject 请求数据(/v0/subjects/subject_id)
# https://bangumi.github.io/api/
def bangumi_subject(b_id):
    headers = {
        'accept': 'application/json',
        'User-Agent': 'akko/bgm-renamer'
    }

    url = "https://api.bgm.tv/v0/subjects/" + b_id
    print(f"正在向Bangumi请求ID {b_id}的详细信息")

    # 3次重试机会，避免网络原因导致请求失败
    retry = 0
    while retry < 3:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result = json.loads(response.text)
            print(f"成功获取到ID {b_id}的详细信息")

            b_type = result["platform"]
            b_release_date = result["date"]
            b_episodes = result["eps"]

            # 使用 arrow 库将时间处理成指定格式
            b_release_date = arrow.get(b_release_date).format("YYMMDD")

            b_dict = dict()
            b_dict["b_type"] = b_type
            b_dict["b_release_date"] = b_release_date
            b_dict["b_episodes"] = b_episodes
            return b_dict

        # 若请求失败，等待0.5秒重试
        else:
            print("Bangumi请求更多失败，重试" + str(retry + 1))
            time.sleep(0.5)
            retry += 1

    print(f"向Bangumi请求ID {b_id}的详细信息失败")


# 向 Bangumi Previous 请求数据(v0/subjects/subjects)
# https://bangumi.github.io/api/
def bangumi_previous(b_id, b_cn_name):
    headers = {
        'accept': 'application/json',
        'User-Agent': 'akko/bgm-renamer'
    }

    url = "https://api.bgm.tv/v0/subjects/" + b_id + "/subjects"
    print(f"正在向Bangumi请求{b_cn_name}的上一季度数据")

    # 3次重试机会，避免网络原因导致请求失败
    retry = 0
    while retry < 3:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            result = json.loads(response.text)
            print(f"成功获取到{b_cn_name}的上一季数据")

            # 检测改动画 ID 是否有前传内容
            # 如果有，返回前传 prev_id 和 prev_cn_name
            # 如果没有，返回原始 b_id 和 b_cn_name
            for data in result:
                if data["relation"] == "前传":
                    prev_id = str(data["id"])
                    prev_cn_name = data["name_cn"]
                    return prev_id, prev_cn_name
            else:
                return b_id, b_cn_name

        # 若请求失败，等待0.5秒重试
        else:
            print("Bangumi请求上一季度信息失败，重试" + str(retry + 1))
            time.sleep(0.5)
            retry += 1

    print(f"在Bangumi中请求{b_cn_name}上一季度信息失败")






# 格式化动画类型 a_type
def set_format(type):
    if type in ["TV", "TV_SHORT"]:
        a_type = "1.TV"
    elif type in ["MOVIE"]:
        a_type = "2.MOVIE"
    elif type in ["SPECIAL", "OVA", "ONA"]:
        a_type = "3.SP"
    else:
        a_type = "XBD"
        print("未知的动画类型，注意检查")
    return a_type





# idd = str(315745)
# result = bangumi_subject(idd)
# print(result)
