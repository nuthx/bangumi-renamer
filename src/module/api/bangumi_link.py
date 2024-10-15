import requests


# https://github.com/ekibot/bangumi-link
def bangumiLinkRelate(bangumi_id):
    """
    搜索动画的关联信息
    :param bangumi_id: Bangumi ID
    :return: 关联信息(仅node部分)
    """
    try:
        bangumi_ids = str(int(bangumi_id) // 1000)
        map_id = requests.get(f"https://cdn.jsdelivr.net/gh/ekibot/bangumi-link/node/{bangumi_ids}/{bangumi_id}").text

        map_ids = str(int(map_id) // 1000)
        result = requests.get(f"https://cdn.jsdelivr.net/gh/ekibot/bangumi-link/map/{map_ids}/{map_id}.json").json()

        return result["node"]

    except Exception as e:
        print(e)
        return
