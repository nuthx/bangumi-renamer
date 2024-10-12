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
            "anime_id": anime_id, 
            "file_name": os.path.basename(file_path),
            "file_path": file_path
        }

        anime_list.append(this_anime_dict)
        anime_id += 1

    return anime_id, anime_list
