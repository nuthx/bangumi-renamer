import re
import anitopy

from src.module.api import *


def getRomajiName(file_name):
    # 加载文件名忽略列表
    ignored = ["BD-BOX", "BD"]

    # 将指定字符加入忽略列表，并更新 file_name为忽略后的名字
    pattern_ignored = '|'.join(ignored)
    file_name = re.sub(pattern_ignored, '', file_name)

    # 使用 anitopy 识别动画名
    aniparse_options = {'allowed_delimiters': ' .-+[]'}
    romaji_name = anitopy.parse(file_name, options=aniparse_options)

    # 如果没识别到动画名返回 None
    if "anime_title" in romaji_name:
        anime_title = romaji_name["anime_title"]
        return anime_title


def getApiInfo(anime):
    romaji_name = anime["romaji_name"]

    # Anilist

    jp_name_anilist = anilistSearch(romaji_name)
    if jp_name_anilist:
        anime["jp_name_anilist"] = jp_name_anilist
    else:
        return

    # Bangumi Search

    bangumi_search = bangumiSearch(jp_name_anilist)
    if bangumi_search:
        anime["bgm_id"] = bangumi_search[0]
        anime["bgm_image"] = bangumi_search[1]
        anime["jp_name"] = bangumi_search[2]
        anime["cn_name"] = bangumi_search[3]
    else:
        return

    # bangumi Subject

    bangumi_subject = bangumiSubject(anime["bgm_id"])
    if bangumi_subject:
        anime["bgm_type"] = bangumi_subject[0]
        anime["bgm_typecode"] = bangumi_subject[1]
        anime["release_date"] = bangumi_subject[2]
        anime["episodes"] = bangumi_subject[3]
    else:
        return

    # Bangumi Previous
    bgm_id = anime["bgm_id"]
    bangumi_previous = bangumiPrevious(bgm_id, anime["cn_name"])
    prev_id = bangumi_previous[0]
    prev_name = bangumi_previous[1]

    while bgm_id != prev_id:  # 如果 ID 不同，说明有前传
        bgm_id = prev_id
        bangumi_previous = bangumiPrevious(bgm_id, prev_name)
        prev_id = bangumi_previous[0]
        prev_name = bangumi_previous[1]

    anime["initial_id"] = prev_id
    anime["initial_name"] = prev_name

    # # 写入图片文件名到字典
    # img_url = this_anime_dict["b_image"]
    # img_name = os.path.basename(img_url)
    # this_anime_dict["b_image_name"] = img_name
    #
    # # 检测图片文件夹是否存在
    # img_dir = "cover"
    # if not os.path.exists(img_dir):
    #     os.makedirs(img_dir)
    #
    # # 下载此图片
    # response_img = requests.get(img_url)
    # save_path = os.path.join(img_dir, img_name)
    # with open(save_path, "wb") as file:
    #     file.write(response_img.content)
    #
    # # 写入命名结果
    # final_name = get_final_name(this_anime_dict, name_type)
    # this_anime_dict["final_name"] = final_name
    # print(f"该动画将重命名为{final_name}")
    #
    # return this_anime_dict



    #
    # # 开始分析线程
    # def start_analysis_thread(self, list_id, file_path, name_type):
    #     # 获取本线程的动画信息，写入 anime_list
    #     this_anime_dict = function.get_anime_info(list_id, file_path, name_type)
    #     self.anime_list.append(this_anime_dict)
    #
    #     # 重新排序 anime_list 列表，避免串行
    #     self.anime_list = sorted(self.anime_list, key=lambda x: x['list_id'])
    #
    #     # 展示在列表中
    #     # 如果没有 b_initial_id 说明没分析完成
    #     if "b_initial_id" in this_anime_dict:
    #         list_id = this_anime_dict["list_id"]
    #         list_order = list_id - 1
    #         file_name = this_anime_dict["file_name"]
    #         b_cn_name = this_anime_dict["b_cn_name"]
    #         b_initial_name = this_anime_dict["b_initial_name"]
    #         final_name = this_anime_dict["final_name"]
    #
    #         self.tree.topLevelItem(list_order).setText(0, str(list_id))
    #         self.tree.topLevelItem(list_order).setText(1, file_name)
    #         self.tree.topLevelItem(list_order).setText(2, b_cn_name)
    #         self.tree.topLevelItem(list_order).setText(3, b_initial_name)
    #         self.tree.topLevelItem(list_order).setText(4, final_name)
    #     else:
    #         print("该动画未获取到内容，已跳过")