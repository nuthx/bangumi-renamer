import time
import json
import requests

from src.module.version import Version


# https://bangumi.github.io/api
class Bangumi:
    def __init__(self):
        self.agent = f"nuthx/bangumi-renamer/{Version().current()} (https://github.com/nuthx/bangumi-renamer)"
        self.headers = {"accept": "application/json", "User-Agent": self.agent}

    def searchID(self, name_jp):
        """
        使用name_jp搜索Bangumi ID，容易触发DDOS 503保护，因此重试三次。其他API目前无此问题
        :param name_jp: 动画日文名称
        :return: Bangumi ID
        """
        name_jp = name_jp.replace("!", " ").replace("-", " ").replace("/", " ").strip()  # 搜索时移除特殊符号避免报错
        url = "https://api.bgm.tv/search/subject/" + name_jp + "?type=2&responseGroup=large&max_results=25"

        for attempt in range(3):
            try:
                result = requests.get(url, headers=self.headers).json()
                bangumi_id = result["list"][0]["id"]
                return str(bangumi_id)

            except json.JSONDecodeError:
                if attempt < 2:
                    print(f"bangumiIDSearch - {name_jp}: 503 重试中 ({attempt + 1}/3)")
                    time.sleep(0.2)
                    continue
                else:
                    break

            except Exception as e:
                print(f"bangumiIDSearch - {name_jp}: e")
                break

        return None

    def getDetail(self, bangumi_id):
        """
        使用bangumi id搜索动画详情
        :param bangumi_id: Bangumi ID
        :return: 动画详情字典
        """
        try:
            result = requests.get("https://api.bgm.tv/v0/subjects/" + bangumi_id, headers=self.headers).json()

            # type
            if result["platform"] in ["TV"]:
                typecode = "01"
            elif result["platform"] in ["剧场版"]:
                typecode = "02"
            elif result["platform"] in ["OVA", "OAD"]:
                typecode = "03"
            else:
                typecode = "XBD"

            # release_end_raw 和 release_week
            if result["infobox"]:
                release_end_raw = next((item["value"] for item in result["infobox"] if item["key"] == "播放结束"), "1000-01-01")
                release_end_raw = release_end_raw.replace("年", "-").replace("月", "-").replace("日", "")
                release_week = next((item["value"] for item in result["infobox"] if item["key"] == "放送星期"), "未知星期")
            else:
                release_end_raw = "1000-01-01"
                release_week = "未知星期"

            anime_info = {
                "name_jp": result["name"],
                "name_cn": result["name_cn"] if result["name_cn"] else result["name"],
                "poster": result["images"]["medium"],
                "type": result["platform"],
                "typecode": typecode,
                "release_raw": result["date"] if result["date"] else "1000-01-01",
                "release_end_raw": release_end_raw,
                "release_week": release_week,
                "episodes": result["eps"] if result["eps"] else "0",
                "score": str(format(float(result["rating"]["score"]), ".1f"))
            }

            return anime_info

        except Exception as e:
            print(f"bangumiSubject - {bangumi_id}: e")
            return
