import requests

version = ["1.1"]


def getVersion():
    app_version = version[0]
    return app_version


def checkUpdate():
    current_version = getVersion()

    url = "http://your-update-server.com/check_update"
    response = requests.get(url)







