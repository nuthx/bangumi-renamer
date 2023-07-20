import requests


def currentVersion():
    current_version = "1.0"
    return current_version


def latestVersion():
    url = "https://raw.githubusercontent.com/nuthx/bangumi-renamer/dev_1.1_update/build.spec"
    response = requests.get(url)
    response_text = response.text.split('\n')

    version_raw = response_text[-3].strip()
    latest_version = version_raw[9: -1]

    return latest_version
