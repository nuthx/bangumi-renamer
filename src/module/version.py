import re
import requests


def currentVersion():
    current_version = "1.3"
    return current_version


def latestVersion():
    url = "https://raw.githubusercontent.com/nuthx/bangumi-renamer/main/build.spec"
    response = requests.get(url)
    response_text = response.text.split('\n')

    version_raw = response_text[-3].strip()
    re1 = re.findall(r'\'(.*?)\'', version_raw)
    latest_version = re1[0]

    return latest_version


def newVersion():
    current_version = currentVersion()
    latest_version = latestVersion()

    if current_version != latest_version:
        return True
    else:
        return False
