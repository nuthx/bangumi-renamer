import requests
import json
import time  # 延迟操作
import arrow  # 处理时间格式


# 向 Anilist 请求数据
# https://anilist.github.io/ApiV2-GraphQL-Docs/
def anilist(name):
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
        'variables': {'id': name},
    }

    print(f"正在向Anilist请求{name}的数据")

    # 3次重试机会，避免网络原因导致请求失败
    retry = 0
    while retry < 3:
        response = requests.post('https://graphql.anilist.co', json=js, headers=headers)

        if response.status_code == 200:
            result = json.loads(response.text.encode().decode('unicode_escape'))
            print(f"成功获取到{name}的Anilist数据")

            a_jp_name = result["data"]["Media"]["title"]["native"]
            a_type = result["data"]["Media"]["format"].lower()

            # 格式化动画类型 a_type
            if a_type in ["tv", "tv_short"]:
                a_type = "1.TV"
            elif a_type in ["movie"]:
                a_type = "2.MOVIE"
            elif a_type in ["special", "ova", "ona"]:
                a_type = "3.SP"
            else:
                a_type = "XBD"
                print("未知的动画类型，注意检查")

            # 将上述元素放入字典
            a_dict = dict()
            a_dict["a_jp_name"] = a_jp_name
            a_dict["a_type"] = a_type

            return a_dict

        # 若请求失败，等待0.5秒重试
        else:
            print("Anilist请求失败，重试" + str(retry + 1))
            time.sleep(0.5)
            retry += 1

    print(f"在Anilist中请求{name}数据失败")


# # 向 Bangumi 请求数据(v0/search/subjects)
# # https://bangumi.github.io/api/
# def bangumi(name):
#     headers = {
#         'accept': 'application/json',
#         'User-Agent': 'akko/bgm-renamer'
#     }

#     js = {
#         'keyword': name,
#         'filter': {
#             'type': [2]
#         }
#     }

#     print(f"正在向Bangumi请求{name}的数据")

#     # 3次重试机会，避免网络原因导致请求失败
#     retry = 0
#     while retry < 3:
#         response = requests.post('https://api.bgm.tv/v0/search/subjects', json=js, headers=headers)

#         if response.status_code == 200:
#             result = json.loads(response.text)
#             print(f"成功获取到{name}的Bangumi数据")

#             # 定义全局变量
#             global b_jp_name
#             global b_cn_name
#             global b_date
#             global b_image
#             global b_id

#             b_jp_name = result["data"][0]["name"]
#             b_cn_name = result["data"][0]["name_cn"]
#             b_date = result["data"][0]["date"]
#             b_image = result["data"][0]["image"]
#             b_id = result["data"][0]["id"]

#             # 使用 arrow 库将时间处理成指定格式
#             b_date = arrow.get(b_date).format("YYMMDD")

#             return result

#         # 若请求失败，等待0.5秒重试
#         else:
#             print("Bangumi请求失败，重试" + str(retry + 1))
#             time.sleep(0.5)
#             retry += 1

#     print(f"在Bangumi中请求{name}数据失败")


# 向 Bangumi 请求数据(search/subject/keywords)
# https://bangumi.github.io/api/
def bangumi(name):
    headers = {
        'accept': 'application/json',
        'User-Agent': 'akko/bgm-renamer'
    }

    url = "https://api.bgm.tv/search/subject/" + name + "?type=2&responseGroup=small"

    print(f"正在向Bangumi请求{name}的数据")
    
    # 3次重试机会，避免网络原因导致请求失败
    retry = 0
    while retry < 3:
        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            result = json.loads(response.text)
            print(f"成功获取到{name}的Bangumi数据")

            b_jp_name = result["list"][0]["name"]
            b_cn_name = result["list"][0]["name_cn"]
            b_image = result["list"][0]["images"]["large"]
            b_id = result["list"][0]["id"]

            # 将上述元素放入字典
            b_dict = dict()
            b_dict["b_jp_name"] = b_jp_name
            b_dict["b_cn_name"] = b_cn_name
            b_dict["b_image"] = b_image
            b_dict["b_id"] = b_id

            return b_dict

        # 若请求失败，等待0.5秒重试
        else:
            print("Bangumi请求失败，重试" + str(retry + 1))
            time.sleep(0.5)
            retry += 1

    print(f"在Bangumi中请求{name}数据失败")







# name = "atashi ni Tenshi ga Maiorita! Precious Friends"

# a_result = anilist(name)
# print(a_result)

# b_result = bangumi(a_result["a_jp_name"])
# print(b_result)

# result = {**a_result, **b_result}
# print(result)




