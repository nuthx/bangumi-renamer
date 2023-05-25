import requests
import json
import re
import time
import sys
import os
import shutil
import logging
from datetime import datetime
# import aniparse


# 配置日志记录
current_date = datetime.now().strftime("%Y%m%d")
logging.basicConfig(
    format='[%(levelname)s] %(asctime)s %(message)s',
    filename=f'{current_date}.log', 
    level=logging.DEBUG,
    datefmt='%H:%M:%S'
)

# 日志输出到控制台
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(message)s', datefmt='%H:%M:%S')
console_handler.setFormatter(console_formatter)

logger = logging.getLogger()
logger.addHandler(console_handler)


# 初始化日志内容
logging.debug("==============")


# 拖入文件夹来获得文件名
# 如果不正确则提示重新输入
# 临时删除macOS下会出现的反斜杠，处理转义的文件夹路径
while True:
    print("请选择文件夹")
    if len(sys.argv) < 2:
        # inputpath = input().strip().replace("\\", "")
        inputpath = input().strip().replace("\"", "")
        logging.debug("输入路径：" + inputpath)
    else:
        # inputpath = sys.argv[1].replace("\\", "")
        inputpath = sys.argv[1].replace("\"", "")
        logging.debug("输入路径：" + inputpath)

    # 确保文件夹路径存在
    if not os.path.exists(inputpath):
        logging.error("文件夹路径无效，等待重新输入")
        continue
    break

# 提取文件夹名
inputdir, inputname = os.path.split(inputpath)
logging.info("动画文件名：" + inputname)


# 使用正则将输入文件名 inputname 转换为罗马音作品名 animename
pattern = r"\] (.*?)\[|$"
match = re.search(pattern, str(inputname))
if match:
    animename = match.group(1)
    pattern_cleantrash = r"BD-BOX|BD-BOXXX"
    animename = re.sub(pattern_cleantrash, "", animename, flags=re.IGNORECASE)
    logging.info("格式化文件名：" + animename)
else:
    logging.error("非标准的动画文件夹")
    sys.exit(1)


# 使用aniparse将输入文件名 inputname 转换为罗马音作品名 animename
# animeparse = aniparse.parse(str(inputname))
# animename = animeparse["anime_title"]
# logging.info("格式化文件名：" + animename)


# anilist 查询
# https://anilist.github.io/ApiV2-GraphQL-Docs/
headers = {
    'accept': 'application/json',
    'User-Agent': 'akko/bgm-renamer'
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

anilist_json = {
    'query': query,
    'variables': {'id': animename},
}

logging.debug("向Anilist请求数据")
anilistresponse = requests.post('https://graphql.anilist.co', json=anilist_json, headers=headers)
anilistresult = json.loads(anilistresponse.text.encode().decode('unicode_escape'))
logging.debug("Anilist数据请求成功")
logging.debug(anilistresult)

# 提取信息: 日文原名、动画形式
anilistname = anilistresult["data"]["Media"]["title"]["native"]
anilistformat = anilistresult["data"]["Media"]["format"].lower()
logging.info("Anilist动画名：" + anilistname)
logging.info("Anilist动画类型：" + anilistformat)

# 格式化anilistformat内容
if anilistformat in ["tv", "tv_short"]:
    anilistformatcount = "1.TV"
    logging.debug("Anilist动画类型格式化：" + anilistformatcount)
elif anilistformat in ["movie"]:
    anilistformatcount = "2.MOVIE"
    logging.debug("Anilist动画类型格式化：" + anilistformatcount)
elif anilistformat in ["special", "ova", "ona"]:
    anilistformatcount = "3.SP"
    logging.debug("Anilist动画类型格式化：" + anilistformatcount)
else:
    anilistformatcount = "XBD"
    logging.warning("不支持的动画类型，注意检查")


# 将日文名 anilistname 放入 bgm 查询
logging.debug("向Bangumi请求数据")
def bgmpost(url):
    bgm_json = {
        'keyword': anilistname,
        'filter': {
            'type': [2]
        }
    }

    retry = 0
    while retry < 3:
        bgmresponse = requests.post(url, json=bgm_json, headers=headers)
        if bgmresponse.status_code == 200:
            result = json.loads(bgmresponse.text)
            logging.debug("Bangumi数据请求成功")
            return result
        else: 
            logging.warning("Bangumi数据请求失败，重试次数 " + str(retry + 1))
            time.sleep(0.5)
            retry += 1
    logging.error("Bangumi数据请求失败")

# 提取信息: 日文原名、上映日期、平台
bgmresult = bgmpost('https://api.bgm.tv/v0/search/subjects')
bgmname = bgmresult["data"][0]["name"]
bgmcnname = bgmresult["data"][0]["name_cn"]
bgmdate = bgmresult["data"][0]["date"].replace("-", "")
bgmdate = bgmdate[2:]
logging.info("Bangumi动画名：" + bgmname)
logging.info("Bangumi中文译名：" + bgmcnname)
logging.info("Bangumi上映日期：" + bgmdate)


# 确认内容
# user_input = input("是否继续执行？(Y/N): ")
# if user_input.lower() != "y":
#     logging.warning("用户取消执行")
#     exit()
print("是否继续执行？(按下回车键继续)")
input()


# 更改文件夹名称
finalname = "[" + anilistformatcount + "] [" + bgmdate + "] " + bgmname
newpath = os.path.join(inputdir, finalname)
os.rename(inputpath, newpath)
logging.debug("文件夹更名为：" + finalname)

# 创建父文件夹
cnpath = os.path.join(inputdir, bgmcnname)
if not os.path.exists(cnpath):
    os.makedirs(cnpath)
    logging.debug("创建父文件夹：" + bgmcnname)
else:
    logging.debug("父文件夹" + bgmcnname + "已存在，跳过创建步骤")

# 移动至父文件夹
destination_path = os.path.join(cnpath, finalname)
shutil.move(newpath, destination_path)
logging.info("文件已移动至" + bgmcnname + "/" + finalname)