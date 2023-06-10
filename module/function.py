import os
import re
import requests

from module import api


# 检查花括号是否匹配
def check_braces(string):
    stack = []
    for char in string:
        if char == '{':
            stack.append(char)
        elif char == '}':
            if len(stack) == 0 or stack[-1] != '{':
                return False
            else:
                stack.pop()

    if len(stack) == 0:
        return True
    else:
        return False


# 正则提取文件夹的罗马名
def get_romaji_name(file_name):
    # 加载文件名忽略列表
    ignored = ["BD-BOX", "BD"]
    print(f"忽略文件名中的{ignored}")

    # 将指定字符加入忽略列表，并更新 file_name为忽略后的名字
    pattern_ignored = '|'.join(ignored)
    file_name = re.sub(pattern_ignored, '', file_name)

    # 匹配第一个 ] 开始，到第一个 [ 或 (，若无上述内容，则匹配至末尾
    pattern_romaji = r"\](.*?)(?:\[|\(|$)"
    result = re.search(pattern_romaji, file_name)

    # 输出提取的内容，如果没匹配到内容就返回 False
    if result:
        romaji_name = result.group(1).strip()  # strip() 去除首尾空格
        return romaji_name
    else:
        return


# 获取动画信息
def get_anime_info(list_id, file_path, name_type):
    this_anime_dict = dict()

    # 写入 ID
    this_anime_dict["list_id"] = list_id

    # 写入文件路径与文件名
    file_name = os.path.basename(file_path)
    this_anime_dict["file_name"] = file_name
    this_anime_dict["file_path"] = file_path

    # 写入文件罗马名
    romaji_name = get_romaji_name(file_name)
    if romaji_name is None:
        print(f"不兼容的文件夹格式：{file_name}")
        return this_anime_dict
    else:
        this_anime_dict["romaji_name"] = romaji_name

    # 向 Anilist 请求数据
    anilist_result = api.anilist(romaji_name)
    if anilist_result is None:
        print(f"无法获取{romaji_name}的Anilist数据")
        return this_anime_dict
    else:
        this_anime_dict.update(anilist_result)

    # 向 Bangumi Search 请求数据
    a_jp_name = this_anime_dict["a_jp_name"]
    bangumi_result = api.bangumi_search(a_jp_name)
    if bangumi_result is None:
        print(f"无法获取{a_jp_name}的Bangumi数据")
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

    # 写入前传数据
    this_anime_dict["b_initial_id"] = prev_id
    this_anime_dict["b_initial_name"] = prev_cn_name
    print(f"搜索完成，该动画第一季为{prev_id} - {prev_cn_name}")

    # 写入图片文件名到字典
    img_url = this_anime_dict["b_image"]
    img_name = os.path.basename(img_url)
    this_anime_dict["b_image_name"] = img_name

    # 检测图片文件夹是否存在
    img_dir = "img"
    if not os.path.exists(img_dir):
        os.makedirs(img_dir)

    # 下载此图片
    response_img = requests.get(img_url)
    save_path = os.path.join(img_dir, img_name)
    with open(save_path, "wb") as file:
        file.write(response_img.content)

    # 写入命名结果
    final_name = get_final_name(this_anime_dict, name_type)
    this_anime_dict["final_name"] = final_name
    print(f"该动画将重命名为{final_name}")

    return this_anime_dict


# 获取命名结果
def get_final_name(this_anime_dict, name_type):
    b_id = this_anime_dict["b_id"]
    romaji_name = this_anime_dict["romaji_name"]
    b_jp_name = this_anime_dict["b_jp_name"]
    b_cn_name = this_anime_dict["b_cn_name"]
    b_initial_name = this_anime_dict["b_initial_name"]
    b_type = this_anime_dict["b_type"]
    b_typecode = this_anime_dict["b_typecode"]
    b_release_date = this_anime_dict["b_release_date"]
    b_episodes = this_anime_dict["b_episodes"]

    final_name = eval(f'f"{name_type}"')  # 保留 string 输出
    return final_name
