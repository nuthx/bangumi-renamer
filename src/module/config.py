import os
import platform
import configparser


# 配置文件路径
def configPath():
    # 定位系统配置文件所在位置
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
    config.set("Format", "rename_format", "{initial_name}/[{bgm_typecode}] [{release_date}] {jp_name}")
    config.set("Format", "date_format", "YYMMDD")

    config.add_section("Counter")
    config.set("Counter", "open_times", "0")
    config.set("Counter", "analysis_times", "0")
    config.set("Counter", "rename_times", "0")
    config.set("Counter", "anilist_api", "0")
    config.set("Counter", "bangumi_api", "0")

    # 写入配置内容
    with open(config_file, "w") as content:
        config.write(content)


# 读取配置
def readConfig():
    config = configparser.ConfigParser()
    config_file = configFile()

    config.read(config_file)

    return config
