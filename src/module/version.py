import requests


def currentVersion():
    current_version = "1.1"
    return current_version


def latestVersion():
    url = "https://cdn.jsdelivr.net/gh/nuthx/bangumi-renamer/build.spec"
    response = requests.get(url)
    response_text = response.text.split('\n')

    version_raw = response_text[-3].strip()
    latest_version = version_raw[9: -1]

    return latest_version


def newVersion():
    current_version = currentVersion()
    latest_version = latestVersion()

    if current_version < latest_version:
        return current_version, latest_version, True
    else:
        return current_version, latest_version, False
