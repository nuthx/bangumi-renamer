import os
import re

from module import api


# 输入的动画文件夹 file_name，通过正则提取动画名 romaji_name
def get_romaji_name(name):
    # 加载文件名忽略列表
    ignored = ["BD-BOX", "BD"]
    print(f"将忽略文件名中的{ignored}")

    # 将指定字符加入忽略列表
    pattern_ignored = '|'.join(ignored)

    # 更新 file_name 为忽略后的名字
    file_name = re.sub(pattern_ignored, '', name)

    # 匹配第一个 ] 开始，到第一个 [ 或 (，若无上述内容，则匹配至末尾
    pattern_romaji = r"\](.*?)(?:\[|\(|$)"

    # 使用正则表达式匹配并提取内容
    result = re.search(pattern_romaji, file_name)

    # 输出提取的内容
    # 如果没匹配到内容就返回 False
    if result:
        # 使用 strip() 去除首尾空格
        romaji_name = result.group(1).strip()
    else:
        # 非标准的动画格式
        romaji_name = False

    return romaji_name


# 输入待分析的文件序号
# 输入动画文件夹 file_name，输出 API 抓取后的所有内容
def get_anime_info(list_id, path):
    this_anime_dict = dict()

    # 写入处理的文件序号
    this_anime_dict["id"] = list_id
    print(f"当前处理的文件ID: {list_id}")

    # 文件路径转为文件名
    this_anime_dict["path"] = path
    file_name = os.path.basename(path)
    this_anime_dict["file_name"] = file_name
    print(f"正在处理{file_name}")

    # 从文件名提取动画罗马名
    romaji_name = get_romaji_name(file_name)
    if romaji_name == False:
        print(f"非标准的动画格式: {romaji_name}")
        return this_anime_dict
    else:
        this_anime_dict["romaji_name"] = romaji_name
        print(f"完成处理：当前动画罗马名为{romaji_name}")

    # 向 Anilist 请求数据
    anilist_result = api.anilist(romaji_name)
    if anilist_result == None:
        print(f"无法在规定时间内请求到{romaji_name}的数据")
        return this_anime_dict
    else:
        this_anime_dict.update(anilist_result)

    # 向 Bangumi Search 请求数据
    a_jp_name = anilist_result["a_jp_name"]
    bangumi_result = api.bangumi_search(a_jp_name)
    if bangumi_result == None:
        print(f"无法在规定时间内请求到{a_jp_name}的数据")
        return this_anime_dict
    else:
        this_anime_dict.update(bangumi_result)

    # 向 Bangumi Previous 请求数据
    b_id = str(bangumi_result["b_id"])
    b_cn_name = bangumi_result["b_cn_name"]

    print(f"查询{b_cn_name}的初始季度...")
    bangumi_prev_result = api.bangumi_previous(b_id, b_cn_name)
    prev_id = bangumi_prev_result[0]
    prev_name = bangumi_prev_result[1]
    print(f"自身或上一季度是{prev_name}")

    # 如果两个 ID 不同，说明之前还有前传，则循环执行
    while b_id != prev_id:
        b_id = prev_id
        b_cn_name = prev_name

        bangumi_prev_result = api.bangumi_previous(b_id, b_cn_name)
        prev_id = bangumi_prev_result[0]
        prev_name = bangumi_prev_result[1]
        print(f"自身或上一季度是{prev_name}")

    print(f"搜索完成，该动画第一季为{prev_name}")
    this_anime_dict["b_originate_name"] = prev_name


    






    # # 如果获得的 b_sid 与 b_id 不同，说明之前还有前传，则继续执行
    # while b_temp_id != b_id:
    #     print("当前轮次似乎有前传，正在获取前传ID")
    #     bangumi_previous_result = api.bangumi_previous(b_temp_id, b_cn_name)
    #     b_sid = str(bangumi_sid_result[0])
    #     print(b_sid)
    # else:
    #     print("ok")

    # print("该动画无前传")








    return this_anime_dict







# file_name = "[Moozzi2] Watashi ni Tenshi ga Maiorita! Precious Friends [ x265-10Bit Ver. ] - Movie + SP"
# list_id = 5
# romaji_name = get_anime_info(list_id, file_name)
# print(romaji_name)