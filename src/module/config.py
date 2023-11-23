import os
import re
import platform
import configparser


# 文件夹存在检查
def newFolder(folder_name):
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)


# 配置文件路径
def configPath():
    if platform.system() == "Windows":
        sys_path = os.environ["APPDATA"]
    elif platform.system() == "Darwin":
        sys_path = os.path.expanduser("~/Library/Application Support")
    elif platform.system() == "Linux":
        sys_path = os.path.expanduser("~/.config")
    else:
        return "N/A"

    config_path = os.path.join(sys_path, "BangumiRenamer")
    newFolder(config_path)

    return config_path


def configFile():
    config_file = os.path.join(configPath(), "config.ini")

    # 是否存在该配置文件
    if not os.path.exists(config_file):
        initConfig(config_file)

    return config_file


def posterFolder():
    poster_folder = os.path.join(configPath(), "poster")
    newFolder(poster_folder)

    return poster_folder


def logFolder():
    log_folder = os.path.join(configPath(), "logs")
    newFolder(log_folder)

    return log_folder


# 初始化配置
def initConfig(config_file):
    config = configparser.ConfigParser()

    config.add_section("Application")
    config.set("Application", "version", "2.0")

    config.add_section("Format")
    config.set("Format", "rename_format", "{init_name}/[{score}] [{typecode}] [{release}] {jp_name}")
    config.set("Format", "date_format", "YYMMDD")

    config.add_section("Bangumi")
    config.set("Bangumi", "user_id", "")

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


# 删除旧版配置文件
def oldConfigCheck():
    config = readConfig()
    current_config_version = config.get("Application", "version")

    # 提取旧版配置计数器
    open_times = config.get("Counter", "open_times")
    analysis_times = config.get("Counter", "analysis_times")
    rename_times = config.get("Counter", "rename_times")

    if current_config_version != "2.0":
        config_file = configFile()
        os.remove(config_file)
        initConfig(config_file)

        # 写入计数器
        config = readConfig()
        config.set("Counter", "open_times", open_times)
        config.set("Counter", "analysis_times", analysis_times)
        config.set("Counter", "rename_times", rename_times)
        with open(config_file, "w", encoding="utf-8") as content:
            config.write(content)


# 读取配置
def readConfig():
    config = configparser.ConfigParser()
    config_file = configFile()

    config.read(config_file)

    return config
