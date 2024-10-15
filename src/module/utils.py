import re
import os
import sys
import logging
from datetime import datetime

from src.module.config import logFolder


def getResource(path):
    """
    根据系统环境，输出资源文件的最终路径
    :param path: 相对路径
    :return: 最终路径
    """
    if hasattr(sys, '_MEIPASS'):  # 系统环境中存在_MEIPASS属性说明程序已被打包
        return os.path.join(sys._MEIPASS, path)
    else:
        return os.path.join(os.path.abspath("."), path)


def log(content):
    """
    在控制台打印指定内容，并同步写入日志文件
    :param content: 需要输出的内容
    """
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%Y-%m-%d %H:%M:%S")

    log_folder = logFolder()
    log_file = os.path.join(log_folder, f"{date}.log")

    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(message)s")
    logging.info(f"[{time}] {content}")

    print(f"[{time}] {content}")


def sanitizeName(filename):
    invalid = r'[<>:"/\\|?*]'  # windows 不允许的字符
    return re.sub(invalid, '', filename)
