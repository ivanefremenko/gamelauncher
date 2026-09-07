import os
import json


STEAM_USERDATA_PATH = r"C:\Program Files (x86)\Steam\userdata"

IMAGE_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".webp",
    ".bmp"
}


def scan_screenshots(steam_id, output_file="screenshots.json"):
    """
    Сканирует Steam-скриншоты пользователя.

    steam_id:
        ID папки userdata, например:
        1697939303

    output_file:
        Куда сохранить JSON.

    Возвращает:
        dict с найденными скриншотами.
    """

    userdata = os.path.join(
        STEAM_USERDATA_PATH,
        str(steam_id)
    )

    screenshots_root = os.path.join(
        userdata,
        "760",
        "remote"
    )

    result = {}

    if not os.path.isdir(userdata):
        print(f"[ERROR] Не найдена папка пользователя: {userdata}")
        return result

    if not os.path.isdir(screenshots_root):
        print(f"[INFO] Папка скриншотов не найдена: {screenshots_root}")

        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)

        return result

    print(f"[SCAN] Steam ID: {steam_id}")
    print(f"[SCAN] Путь: {screenshots_root}")
    print()

    # В Steam:
    #
    # userdata/
    #   STEAM_ID/
    #     760/
    #       remote/
    #         APPID/
    #           screenshots/
    #
    # Поэтому 760 пропускаем и получаем настоящий AppID игры.

    for appid in os.listdir(screenshots_root):

        app_folder = os.path.join(
            screenshots_root,
            appid
        )

        if not os.path.isdir(app_folder):
            continue

        # AppID должен быть числом
        if not appid.isdigit():
            continue

        screenshot_folder = os.path.join(
            app_folder,
            "screenshots"
        )

        if not os.path.isdir(screenshot_folder):
            continue

        screenshots = []

        for root, dirs, files in os.walk(screenshot_folder):

            for filename in files:

                extension = os.path.splitext(
                    filename
                )[1].lower()

                if extension not in IMAGE_EXTENSIONS:
                    continue

                full_path = os.path.join(
                    root,
                    filename
                )

                screenshots.append(
                    os.path.abspath(full_path)
                )

        if not screenshots:
            continue

        result[appid] = {
            "appid": int(appid),
            "folder": os.path.abspath(screenshot_folder),
            "screenshots": sorted(screenshots),
            "count": len(screenshots)
        }

        print(
            f"[FOUND] AppID {appid} -> "
            f"{len(screenshots)} скриншотов"
        )

    # Сохраняем JSON
    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=4
        )

    print()
    print(f"[DONE] Найдено игр: {len(result)}")
    print(f"[DONE] JSON: {os.path.abspath(output_file)}")

    return result


# Пример запуска
if __name__ == "__main__":
    scan_screenshots(1697939303)