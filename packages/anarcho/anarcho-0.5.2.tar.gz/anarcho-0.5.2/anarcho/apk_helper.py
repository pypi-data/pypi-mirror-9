import os

from anarcho.models.build import Build
from APKParser.apk import APK


def save_file_from_apk(apk_file, file_name, dest):
    f = apk_file.get_file(file_name)
    out = open(dest, 'wb')
    out.write(f)
    out.close()


def save_icon(apk_file, package, icon_dest):
    icon_hex_id = apk_file.get_element("application", "android:icon")
    icon_id = int(icon_hex_id.replace("@", ""), 16)
    icon_name = apk_file.get_android_resources().get_id(package, icon_id)[1]
    icons = apk_file.get_android_resources().get_drawable(package, icon_name)
    if len(icons) > 0:
        save_file_from_apk(apk_file, icons[-1][1], icon_dest)


def parse_apk(apk_path, app_key):
    apk_file = APK(apk_path)

    package = apk_file.get_package()
    version_code = apk_file.get_androidversion_code()
    version_name = apk_file.get_androidversion_name()

    icon_dest = os.path.join(os.path.dirname(apk_path), "%s_icon.png" % app_key)
    try:
        save_icon(apk_file, package, icon_dest)
    except:
        print icon_dest, 'not saved'
        icon_dest = None
    build = Build(app_key, version_code, version_name)
    return {"build": build, "icon_path": icon_dest, "package": package}