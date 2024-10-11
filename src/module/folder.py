import platform
import subprocess


def openFolder(path):
    if platform.system() == "Windows":
        subprocess.call(["explorer", path])
    elif platform.system() == "Darwin":
        subprocess.call(["open", path])
    elif platform.system() == "Linux":
        subprocess.call(["xdg-open", path])
