import os
import logging
from datetime import datetime

from src.module.config import logFolder


def log(content):
    now = datetime.now()
    date = now.strftime("%Y-%m-%d")
    time = now.strftime("%Y-%m-%d %H:%M:%S")

    log_folder = logFolder()
    log_file = os.path.join(log_folder, f"{date}.log")

    logging.basicConfig(filename=log_file, level=logging.INFO, format="%(message)s")
    logging.info(f"[{time}] {content}")

    print(f"[{time}] {content}")
