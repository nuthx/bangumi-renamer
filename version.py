ver = "2.1.0"
ver_windows = ver.replace(".", ", ") + ", 0"


def windowsVersion():
    with open("version.txt", "r") as file:
        lines = file.readlines()

    if lines[6].strip().startswith("filevers"):
        lines[6] = f"    filevers=({ver_windows}),\n"

    if lines[7].strip().startswith("prodvers"):
        lines[7] = f"    prodvers=({ver_windows}),\n"

    if lines[30].strip().startswith("StringStruct(u'FileVersion'"):
        lines[30] = f"        StringStruct(u'FileVersion', u'{ver}'),\n"

    if lines[33].strip().startswith("StringStruct(u'ProductVersion'"):
        lines[33] = f"        StringStruct(u'ProductVersion', u'{ver}')])\n"

    with open("version.txt", "w") as file:
        file.writelines(lines)


def macVersion():
    with open("build-mac.spec", "r") as file:
        lines = file.readlines()

    if lines[53].strip().startswith("version"):
        lines[53] = f"    version='{ver}',\n"

    with open("build-mac.spec", "w") as file:
        file.writelines(lines)


def appVersion():
    with open("src/module/version.py", "r") as file:
        lines = file.readlines()

    if lines[12].strip().startswith("current_version"):
        lines[12] = f'        current_version = "{ver}"\n'

    with open("src/module/version.py", "w") as file:
        file.writelines(lines)


windowsVersion()
macVersion()
appVersion()
print(f"版本已更改至{ver}")
