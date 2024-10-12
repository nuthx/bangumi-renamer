import os
import platform


def createAnimeData(anime_id, anime_list, file_list):
    for file in file_list:
        # 转换为文件路径
        file_path = file.toLocalFile()

        # Windows 下调整路径分隔符
        if platform.system() == "Windows":
            file_path = file_path.replace("/", "\\")

        # 解决 macOS 下路径无法识别
        if file_path.endswith("/"):
            file_path = file_path[:-1]

        # 过滤非文件夹
        if not os.path.isdir(file_path):
            continue

        # 去重已存在的文件夹
        path_exist = any(item["file_path"] == file_path for item in anime_list)
        if path_exist:
            continue

        this_anime_dict = {
            "id": anime_id,  # ID
            "file_name": os.path.basename(file_path),  # 原始文件名
            "file_path": file_path,  # 原始文件路径
            "final_name": "",  # 重命名后的文件名
            "final_dir": "",  # 重命名后的文件目录
            "final_path": "",  # 重命名后的文件路径
            "bangumi_id": 0,  # Bangumi ID
            "name_jp": "",  # 日文名称(Bangumi)
            "name_jp_anilist": "",  # 日文名称(AniList)
            "name_romaji": "",  # 罗马音名称
            "name_cn": "",  # 中文名称
            "poster": "",  # 海报图片
            "type": "",  # 放送类型
            "typecode": "",  # 放送类型代码(01: TV版, 02: 剧场版, 03: OVA与OAD, XBD: 其他)
            "release": "",  # 放送开始日期
            "release_end": "",  # 放送结束日期
            "release_week": "",  # 放送星期
            "episodes": 0,  # 章节数量
            "score": "",  # 当前评分
            "collection": "",  # 收藏状态
            "fs_id": "",  # 首季度Bangumi ID
            "fs_name_cn": "",  # 首季度中文名称动画
            "fs_detail": []  # 首季度动画信息
        }

        anime_list.append(this_anime_dict)
        anime_id += 1

    return anime_id, anime_list
