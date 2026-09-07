import json
import os
from pathlib import Path

import vdf


def scan_steam_shortcuts(output_file="steam_shortcuts.json"):
    """
    Сканирует все shortcuts.vdf в Steam\\userdata\\*\\config
    и сохраняет индекс ярлыка + steam://rungameid/... в JSON.

    Возвращает список найденных ярлыков.
    """

    # --- Поиск Steam ---
    steam_path = None

    try:
        import winreg

        registry_locations = [
            (winreg.HKEY_CURRENT_USER, r"Software\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Valve\Steam"),
            (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Valve\Steam"),
        ]

        for root, key_path in registry_locations:
            try:
                with winreg.OpenKey(root, key_path) as key:
                    value, _ = winreg.QueryValueEx(key, "SteamPath")
                    path = Path(value)

                    if path.exists():
                        steam_path = path
                        break

            except (FileNotFoundError, OSError):
                pass

    except Exception:
        pass

    # --- Если реестр не сработал ---
    if steam_path is None:
        for path in (
            Path(r"C:\Program Files (x86)\Steam"),
            Path(r"C:\Program Files\Steam"),
        ):
            if path.exists():
                steam_path = path
                break

    if steam_path is None:
        raise FileNotFoundError("Steam не найден.")

    # --- Поиск shortcuts.vdf ---
    userdata = steam_path / "userdata"

    if not userdata.exists():
        raise FileNotFoundError(
            f"Папка userdata не найдена: {userdata}"
        )

    result = []

    for user_dir in userdata.iterdir():

        if not user_dir.is_dir():
            continue

        shortcuts_file = user_dir / "config" / "shortcuts.vdf"

        if not shortcuts_file.exists():
            continue

        # --- Читаем бинарный VDF ---
        with open(shortcuts_file, "rb") as f:
            data = vdf.binary_load(f)

        shortcuts = data.get("shortcuts", {})

        # Индекс здесь именно индекс записи в shortcuts.vdf
        for index, shortcut in shortcuts.items():

            try:
                index = int(index)
            except (ValueError, TypeError):
                continue

            try:
                appid = int(shortcut.get("appid", 0)) & 0xFFFFFFFF

                # Формула Steam для Non-Steam Game
                rungameid = (appid << 32) | 0x02000000

                steam_url = f"steam://rungameid/{rungameid}"

            except (ValueError, TypeError):
                continue

            result.append({
                "index": index,
                "name": shortcut.get("AppName", ""),
                "steam_url": steam_url
            })

    # Сортируем для удобства
    result.sort(key=lambda x: x["index"])

    # --- Сохраняем JSON ---
    output_path = Path(output_file)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            result,
            f,
            ensure_ascii=False,
            indent=4
        )

    return result


if __name__ == "__main__":
    shortcuts = scan_steam_shortcuts()

    print(f"Найдено ярлыков: {len(shortcuts)}")

    for shortcut in shortcuts:
        print(
            f'[{shortcut["index"]}] '
            f'{shortcut["name"]} -> '
            f'{shortcut["steam_url"]}'
        )
