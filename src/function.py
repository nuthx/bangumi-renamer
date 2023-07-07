import os
import re
import requests
from qfluentwidgets import InfoBar, InfoBarPosition

from src.module import api


def initAnimeList(list_id, anime_list, raw_path_list):
    for raw_path in raw_path_list:
        # 转换为文件路径
        file_path = raw_path.toLocalFile()

        # 解决 macOS 下路径无法识别
        if file_path.endswith('/'):
            file_path = file_path[:-1]

        # 过滤非文件夹
        if not os.path.isdir(file_path):
            continue

        # 去重已存在的文件夹
        path_exist = any(item['file_path'] == file_path for item in anime_list)
        if path_exist:
            continue

        this_anime_dict = dict()
        this_anime_dict['list_id'] = list_id
        this_anime_dict['file_name'] = os.path.basename(file_path)
        this_anime_dict['file_path'] = file_path
        this_anime_dict['file_dir'] = os.path.dirname(file_path)
        anime_list.append(this_anime_dict)
        list_id += 1

    return list_id, anime_list


def analysisAnimeList(anime_list, name_type):
    # 路径列表是否为空

    if not anime_list:
        InfoBar.warning(title="", content="列表中还没有内容哦", orient=Qt.Horizontal, isClosable=True,
                        position=InfoBarPosition.TOP, duration=1600, parent=self)
        return


# # 开始分析
#     @QtCore.Slot()
#     def start_analysis(self):
#         name_type = self.type_input.text()
#         # 路径列表是否为空
#         if not self.file_path_exist:
#             self.state.setText("请先拖入文件夹")
#             return
#
#         # 分析过程
#         self.anime_list = []  # 重置动画列表
#         list_id = 1
#         for file_path in self.file_path_exist:
#             # 在单独的线程中运行get_anime_info函数
#             thread = threading.Thread(target=self.start_analysis_thread, args=(list_id, file_path, name_type))
#             thread.start()
#             # self.state.setText(f"准备识别{list_id}个动画项目")
#             list_id += 1
#
#     # 开始分析线程
#     def start_analysis_thread(self, list_id, file_path, name_type):
#         # 获取本线程的动画信息，写入 anime_list
#         this_anime_dict = function.get_anime_info(list_id, file_path, name_type)
#         self.anime_list.append(this_anime_dict)
#
#         # 重新排序 anime_list 列表，避免串行
#         self.anime_list = sorted(self.anime_list, key=lambda x: x['list_id'])
#
#         # 展示在列表中
#         # 如果没有 b_initial_id 说明没分析完成
#         if "b_initial_id" in this_anime_dict:
#             list_id = this_anime_dict["list_id"]
#             list_order = list_id - 1
#             file_name = this_anime_dict["file_name"]
#             b_cn_name = this_anime_dict["b_cn_name"]
#             b_initial_name = this_anime_dict["b_initial_name"]
#             final_name = this_anime_dict["final_name"]
#
#             self.tree.topLevelItem(list_order).setText(0, str(list_id))
#             self.tree.topLevelItem(list_order).setText(1, file_name)
#             self.tree.topLevelItem(list_order).setText(2, b_cn_name)
#             self.tree.topLevelItem(list_order).setText(3, b_initial_name)
#             self.tree.topLevelItem(list_order).setText(4, final_name)
#         else:
#             print("该动画未获取到内容，已跳过")






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
    img_dir = "cover"
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
