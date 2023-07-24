import requests


def currentVersion():
    current_version = "1.1"
    return current_version


def latestVersion():
    url = "https://raw.githubusercontent.com/nuthx/bangumi-renamer/main/build.spec"
    response = requests.get(url)
    response_text = response.text.split('\n')

    version_raw = response_text[-3].strip()
    latest_version = version_raw[9: -1]

    return latest_version
