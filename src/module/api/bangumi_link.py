import requests


# https://github.com/ekibot/bangumi-link
def bangumiLink(anime):
    """
    搜索动画的关联条目，如果未搜索到，则返回动画自身的信息作为唯一的关联项
    :param anime: 动画数据
    :return: 关联信息(仅node部分)
    """
    bangumi_id = anime["bangumi_id"]
    try:
        bangumi_ids = str(int(bangumi_id) // 1000)
        map_id = requests.get(f"https://cdn.jsdelivr.net/gh/ekibot/bangumi-link/node/{bangumi_ids}/{bangumi_id}").text

        map_ids = str(int(map_id) // 1000)
        result = requests.get(f"https://cdn.jsdelivr.net/gh/ekibot/bangumi-link/map/{map_ids}/{map_id}.json").json()

        # 清理无用数据
        result = [item for item in result["node"] if item["type"] == 2]  # 只保留动画，移除小说、游戏等类别
        result = [item for item in result if item["platform"] != "WEB"]  # 移除web类别

        return result

    except ValueError as e:
        node = [{
            "id": anime["bangumi_id"],
            "nameCN": anime["name_cn"],
            "type": 2,
            "platform": anime["type"]
        }]

        return node

    except Exception as e:
        print(e)
        return
