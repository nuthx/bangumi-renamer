import os
import re
import platform
import configparser


# 配置文件路径
def configPath():
    if platform.system() == "Windows":
        config_path = os.environ["APPDATA"]
    elif platform.system() == "Darwin":
        config_path = os.path.expanduser("~/Library/Application Support")
    elif platform.system() == "Linux":
        config_path = os.path.expanduser("~/.config")
    else:
        return "N/A"

    config_path = config_path + os.sep + "BangumiRenamer"

    # 是否存在该路径
    if not os.path.exists(config_path):
        os.makedirs(config_path)

    return config_path


def configFile():
    config_path = configPath()
    config_file = config_path + os.sep + "config.ini"

    # 是否存在该配置文件
    if not os.path.exists(config_file):
        initConfig(config_file)

    return config_file


def posterFolder():
    config_path = configPath()
    poster_folder = config_path + os.sep + "Poster"

    # 路径无效时返回无效的海报路径
    if config_path == "N/A":
        return "N/A"

    # 是否存在该路径
    if not os.path.exists(poster_folder):
        os.makedirs(poster_folder)

    return poster_folder


# 初始化配置
def initConfig(config_file):
    config = configparser.ConfigParser()

    config.add_section("Application")
    config.set("Application", "version", "1.0")

    config.add_section("Format")
    config.set("Format", "rename_format", "{init_name}/[{score}] [{typecode}] [{release}] {jp_name}")
    config.set("Format", "date_format", "YYMMDD")

    config.add_section("Counter")
    config.set("Counter", "open_times", "0")
    config.set("Counter", "analysis_times", "0")
    config.set("Counter", "rename_times", "0")

    # 写入配置内容
    with open(config_file, "w", encoding="utf-8") as content:
        config.write(content)


def formatCheck(rename_format):
    # 花括号内容检查
    available = ["jp_name", "cn_name", "init_name", "romaji_name",
                 "types", "typecode", "release", "episodes",
                 "score", "bgm_id"]
    pattern = r"\{(.*?)\}"
    matches = re.findall(pattern, rename_format)
    for match in matches:
        if match not in available:
            return "检查花括号内的变量拼写"

    # 是否有多个斜杠
    if rename_format.count("/") > 1:
        return "仅支持一个单斜杠用于文件夹嵌套"

    return True


# 读取配置
def readConfig():
    config = configparser.ConfigParser()
    config_file = configFile()

    config.read(config_file)

    return config
