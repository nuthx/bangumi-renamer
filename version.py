import re

ver = "2.0"
ver_sp = [num for num in str(ver).split(".")]

if len(ver) == 3:
    ver_alt = f"{ver_sp[0]}, {ver_sp[1]}, 0, 0"
elif len(ver) == 5:
    ver_alt = f"{ver_sp[0]}, {ver_sp[1]}, {ver_sp[2]}, 0"


def windowsVersion():
    with open("version.txt", "r") as file:
        lines = file.readlines()

    re1 = re.findall(r'\((.*?)\)', lines[6])
    lines[6] = lines[6].replace(re1[0], ver_alt)
    lines[7] = lines[7].replace(re1[0], ver_alt)

    re2 = re.findall(r'\'(.*?)\'', lines[30])
    lines[30] = lines[30].replace(re2[1], ver)
    lines[33] = lines[33].replace(re2[1], ver)

    with open("version.txt", "w") as file:
        file.writelines(lines)


def macVersion():
    with open("build.spec", "r") as file:
        lines = file.readlines()

    re1 = re.findall(r'\'(.*?)\'', lines[51])
    lines[51] = lines[51].replace(re1[0], ver)

    with open("build.spec", "w") as file:
        file.writelines(lines)


def appVersion():
    with open("src/module/version.py", "r") as file:
        lines = file.readlines()

    re1 = re.findall(r'\"(.*?)\"', lines[5])
    lines[5] = lines[5].replace(re1[0], ver)

    with open("src/module/version.py", "w") as file:
        file.writelines(lines)


windowsVersion()
macVersion()
appVersion()
print(f"版本已更改至{ver}")
