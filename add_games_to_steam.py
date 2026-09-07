import json
from pathlib import Path

import vdf


def add_games_to_steam_shortcuts(
    games_file="games.json",
    steam_path=r"C:\Program Files (x86)\Steam"
):
    """
    Добавляет игры из games.json в Steam shortcuts.vdf.

    Правила:
    - существующие shortcuts НЕ удаляются и НЕ перезаписываются;
    - игра считается уже добавленной, если AppName совпадает с name из games.json
      без учёта регистра;
    - новые записи получают AppID = 0, чтобы Steam сам сгенерировал ID
      при следующем чтении/пересохранении shortcuts.vdf;
    - перед изменением создаётся резервная копия shortcuts.vdf.

    Возвращает словарь с added и skipped.
    """

    games_file = Path(games_file)
    steam_path = Path(steam_path)

    if not games_file.exists():
        raise FileNotFoundError(f"Не найден файл: {games_file}")

    if not steam_path.exists():
        raise FileNotFoundError(f"Не найдена папка Steam: {steam_path}")

    # ========================================================
    # Читаем games.json
    # ========================================================

    with open(games_file, "r", encoding="utf-8") as f:
        games = json.load(f)

    if not isinstance(games, list):
        raise ValueError("games.json должен содержать список игр.")

    # ========================================================
    # Ищем shortcuts.vdf
    # ========================================================

    userdata = steam_path / "userdata"
    shortcut_files = []

    if userdata.exists():
        for user_dir in userdata.iterdir():
            if not user_dir.is_dir():
                continue

            shortcuts_file = user_dir / "config" / "shortcuts.vdf"

            if shortcuts_file.exists():
                shortcut_files.append(shortcuts_file)

    if not shortcut_files:
        raise FileNotFoundError(
            "Не найден shortcuts.vdf. "
            "Добавь хотя бы один Non-Steam Shortcut через Steam."
        )

    # Если найдено несколько аккаунтов Steam, обрабатываем все
    total_added = []
    total_skipped = []

    # ========================================================
    # Обрабатываем каждый shortcuts.vdf
    # ========================================================

    for shortcuts_file in shortcut_files:

        with open(shortcuts_file, "rb") as f:
            data = vdf.binary_load(f)

        if "shortcuts" not in data:
            data["shortcuts"] = {}

        shortcuts = data["shortcuts"]

        # ----------------------------------------------------
        # Существующие имена
        # ----------------------------------------------------

        existing_names = set()

        for shortcut in shortcuts.values():
            name = str(shortcut.get("AppName", "")).strip().lower()

            if name:
                existing_names.add(name)

        # ----------------------------------------------------
        # Находим следующий свободный индекс
        # ----------------------------------------------------

        numeric_indexes = []

        for key in shortcuts.keys():
            try:
                numeric_indexes.append(int(key))
            except (ValueError, TypeError):
                pass

        next_index = max(numeric_indexes, default=-1) + 1

        changed = False

        # ----------------------------------------------------
        # Добавляем новые игры
        # ----------------------------------------------------

        for game in games:

            if not isinstance(game, dict):
                continue

            name = str(game.get("name", "")).strip()
            exe = str(game.get("exe", "")).strip()
            start_dir = str(game.get("start_dir", "")).strip()

            if not name or not exe:
                continue

            name_key = name.lower()

            # Уже есть ярлык с таким названием
            if name_key in existing_names:
                total_skipped.append({
                    "name": name,
                    "reason": "already_exists",
                    "shortcuts_file": str(shortcuts_file)
                })
                continue

            # ------------------------------------------------
            # Новая запись
            #
            # AppID намеренно НЕ вычисляем.
            # Ставим 0, чтобы Steam обработал ярлык как новый.
            # ------------------------------------------------

            shortcuts[str(next_index)] = {
                "appid": 0,
                "AppName": name,
                "Exe": exe,
                "StartDir": start_dir,
                "icon": "",
                "ShortcutPath": "",
                "LaunchOptions": "",
                "IsHidden": 0,
                "AllowDesktopConfig": 1,
                "AllowOverlay": 1,
                "OpenVR": 0,
                "Devkit": 0,
                "DevkitGameID": "",
                "DevkitOverrideAppID": 0,
                "LastPlayTime": 0,
                "tags": {}
            }

            existing_names.add(name_key)

            total_added.append({
                "name": name,
                "exe": exe,
                "shortcuts_file": str(shortcuts_file)
            })

            next_index += 1
            changed = True

        # ----------------------------------------------------
        # Если ничего не изменилось — файл не трогаем
        # ----------------------------------------------------

        if not changed:
            continue

        # ----------------------------------------------------
        # Backup
        # ----------------------------------------------------

        backup_file = shortcuts_file.with_suffix(
            ".vdf.backup"
        )

        if not backup_file.exists():
            backup_file.write_bytes(
                shortcuts_file.read_bytes()
            )

        # ----------------------------------------------------
        # Сохраняем обновлённый VDF
        # ----------------------------------------------------

        temp_file = shortcuts_file.with_suffix(
            ".vdf.tmp"
        )

        with open(temp_file, "wb") as f:
            vdf.binary_dump(data, f)

        temp_file.replace(shortcuts_file)

    return {
        "added": total_added,
        "skipped": total_skipped
    }


if __name__ == "__main__":

    result = add_games_to_steam_shortcuts()

    print("=" * 80)
    print("ДОБАВЛЕНИЕ ИГР В STEAM")
    print("=" * 80)

    print()
    print(f"Добавлено: {len(result['added'])}")
    print(f"Пропущено: {len(result['skipped'])}")
    print()

    if result["added"]:
        print("ДОБАВЛЕНЫ:")

        for game in result["added"]:
            print(
                f"- {game['name']}"
            )

            print(
                f"  {game['exe']}"
            )

    if result["skipped"]:
        print()
        print("ПРОПУЩЕНЫ (уже есть в Steam):")

        for game in result["skipped"]:
            print(
                f"- {game['name']}"
            )
