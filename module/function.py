import os
import re
import requests

from module import api


# 正则提取文件夹的罗马名
def get_romaji_name(name):
    # 加载文件名忽略列表
    ignored = ["BD-BOX", "BD"]
    print(f"忽略文件名中的{ignored}")

    # 将指定字符加入忽略列表，并更新 file_name为忽略后的名字
    pattern_ignored = '|'.join(ignored)
    file_name = re.sub(pattern_ignored, '', name)

    # 匹配第一个 ] 开始，到第一个 [ 或 (，若无上述内容，则匹配至末尾
    pattern_romaji = r"\](.*?)(?:\[|\(|$)"
    result = re.search(pattern_romaji, file_name)

    # 输出提取的内容，如果没匹配到内容就返回 False
    if result:
        # 使用 strip() 去除首尾空格
        romaji_name = result.group(1).strip()
    else:
        # 非标准的动画格式
        romaji_name = False

    return romaji_name


# 根据路径获取动画信息
# 输入序号避免串行
def get_anime_info(list_id, file_path):
    this_anime_dict = dict()

    # 写入处理的文件序号
    this_anime_dict["list_id"] = list_id

    # 文件路径转为文件名
    file_name = os.path.basename(file_path)
    this_anime_dict["file_name"] = file_name
    this_anime_dict["file_path"] = file_path
    print(f"开始识别 {list_id} - {file_name}")

    # 从文件名提取动画罗马名
    romaji_name = get_romaji_name(file_name)
    if not romaji_name:
        print(f"{file_name}不是标准的动画格式")
        return this_anime_dict
    else:
        this_anime_dict["romaji_name"] = romaji_name
        print(f"当前动画罗马名为{romaji_name}")

    # 向 Anilist 请求数据
    anilist_result = api.anilist(romaji_name)
    if anilist_result is None:
        print(f"无法请求到{romaji_name}的Anilist数据")
        return this_anime_dict
    else:
        this_anime_dict.update(anilist_result)

    # 向 Bangumi Search 请求数据
    a_jp_name = this_anime_dict["a_jp_name"]
    bangumi_result = api.bangumi_search(a_jp_name)
    if bangumi_result is None:
        print(f"无法请求到{a_jp_name}的Bangumi数据")
        return this_anime_dict
    else:
        this_anime_dict.update(bangumi_result)

    # 向 bangumi Subject 请求数据
    b_id = str(bangumi_result["b_id"])
    bangumi_info_result = api.bangumi_subject(b_id)
    if bangumi_info_result is None:
        print(f"无法请求到{a_jp_name}的Bangumi数据")
        return this_anime_dict
    else:
        this_anime_dict.update(bangumi_info_result)

    # 向 Bangumi Previous 请求数据
    b_id = str(bangumi_result["b_id"])
    b_cn_name = bangumi_result["b_cn_name"]

    print(f"查询{b_cn_name}的初始季度...")
    bangumi_prev_result = api.bangumi_previous(b_id, b_cn_name)
    prev_id = bangumi_prev_result[0]
    prev_cn_name = bangumi_prev_result[1]
    print(f"自身或上一季度是{prev_cn_name}")

    # 如果两个 ID 不同，说明之前还有前传，则循环执行
    while b_id != prev_id:
        b_id = prev_id
        b_cn_name = prev_cn_name

        bangumi_prev_result = api.bangumi_previous(b_id, b_cn_name)
        prev_id = bangumi_prev_result[0]
        prev_cn_name = bangumi_prev_result[1]
        print(f"自身或上一季度是{prev_cn_name}")

    this_anime_dict["b_initial_id"] = prev_id
    this_anime_dict["b_initial_name"] = prev_cn_name
    print(f"搜索完成，该动画第一季为{prev_id} - {prev_cn_name}")

    # 下载下来图片并写入字典
    # 如果路径不存在则创建路径
    img_dir = "img"
    print(f"下载本季封面图到{img_dir}")

    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    img_url = this_anime_dict["b_image"]
    response_img = requests.get(img_url)
    img_name = os.path.basename(img_url)

    save_path = os.path.join(img_dir, img_name)
    with open(save_path, "wb") as file:
        file.write(response_img.content)

    print(f"图片已经保存至{img_dir}/{img_name}")
    this_anime_dict["b_image_name"] = img_name

    return this_anime_dict

#
#
# file_name = "[Moozzi2] Watashi ni Tenshi ga Maiorita! Precious Friends [ x265-10Bit Ver. ] - Movie + SP"
# list_id = 5
# romaji_name = get_anime_info(list_id, file_name)
# print(romaji_name)
