import json
import string
from pathlib import Path

import pylnk3


def scan_games_folders(output_file="games.json"):
    """
    Быстро сканирует диски Windows:

    1. Проверяет ТОЛЬКО папки первого уровня в корне диска.
       Например:
           D:\\Games
           E:\\Games

    2. Если папка Games найдена, ищет внутри неё .lnk ярлыки.

    3. Из каждого .lnk получает:
       - название ярлыка;
       - путь к EXE;
       - рабочую папку;
       - имя EXE.

    Никакие диски целиком рекурсивно не сканируются.
    """

    results = []
    seen = set()

    # ========================================================
    # Ищем только Games в корне каждого диска
    # ========================================================

    games_folders = []

    for letter in string.ascii_uppercase:
        root = Path(f"{letter}:\\/")

        if not root.exists():
            continue

        try:
            # os.scandir через iterdir намного быстрее rglob
            for item in root.iterdir():

                if not item.is_dir():
                    continue

                if item.name.lower() == "games":
                    games_folders.append(item)

        except (PermissionError, OSError):
            pass

    # ========================================================
    # Ищем .lnk внутри найденных Games
    # ========================================================

    for games_folder in games_folders:

        try:
            shortcuts = games_folder.rglob("*.lnk")
        except (PermissionError, OSError):
            continue

        for shortcut_path in shortcuts:

            try:
                if not shortcut_path.is_file():
                    continue
            except (PermissionError, OSError):
                continue

            shortcut_key = str(shortcut_path).lower()

            if shortcut_key in seen:
                continue

            seen.add(shortcut_key)

            # =================================================
            # Читаем Windows .lnk
            # =================================================

            try:
                shortcut = pylnk3.parse(str(shortcut_path))
            except Exception:
                continue

            # pylnk3 может возвращать путь через path или target
            exe_path = getattr(shortcut, "path", None)

            if not exe_path:
                exe_path = getattr(shortcut, "target", None)

            if not exe_path:
                continue

            exe_path = Path(str(exe_path))

            # Нас интересуют именно ярлыки на EXE
            if exe_path.suffix.lower() != ".exe":
                continue

            # Если путь относительный — пробуем сделать абсолютным
            if not exe_path.is_absolute():
                exe_path = (
                    shortcut_path.parent / exe_path
                ).resolve()

            # =================================================
            # Данные
            # =================================================

            name = shortcut_path.stem
            start_dir = exe_path.parent

            results.append({
                "name": name,
                "exe": str(exe_path),
                "start_dir": str(start_dir),
                "filename": exe_path.name,
                "shortcut": str(shortcut_path)
            })

    # ========================================================
    # Сортировка
    # ========================================================

    results.sort(
        key=lambda item: item["name"].lower()
    )

    # ========================================================
    # JSON
    # ========================================================

    with open(
        output_file,
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            results,
            f,
            ensure_ascii=False,
            indent=4
        )

    return results


if __name__ == "__main__":
    programs = scan_games_folders()

    print("=" * 80)
    print("СКАНИРОВАНИЕ GAMES ЗАВЕРШЕНО")
    print("=" * 80)
    print(f"Найдено ярлыков на EXE: {len(programs)}")
    print()

    for index, program in enumerate(programs):
        print(f"[{index}] {program['name']}")
        print(f"    EXE:      {program['exe']}")
        print(f"    Ярлык:    {program['shortcut']}")
        print()

    print("Результат сохранён в games.json")
