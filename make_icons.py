import json
import os
import re

import win32gui
import win32ui
import win32con

from PIL import Image


# ============================================================
# НАСТРОЙКИ
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

GAMES_FILE = os.path.join(
    BASE_DIR,
    "scaned_games.json"
)

ICONS_DIR = os.path.join(
    BASE_DIR,
    "icons"
)

os.makedirs(
    ICONS_DIR,
    exist_ok=True
)


# ============================================================
# БЕЗОПАСНОЕ ИМЯ
# ============================================================

def safe_filename(name):

    name = str(name)

    name = re.sub(
        r'[<>:"/\\|?*]',
        "_",
        name
    )

    name = name.rstrip(" .")

    if not name:
        name = "unknown"

    return name


# ============================================================
# ИЗВЛЕЧЕНИЕ ИКОНКИ
# ============================================================

def extract_icon(exe_path, output_path):

    if not exe_path:

        print("[ICON] Нет пути к EXE")

        return False

    if not os.path.isfile(exe_path):

        print("[ICON] EXE не найден:")
        print("       ", exe_path)

        return False

    large_icons = []
    small_icons = []

    try:

        # ====================================================
        # Получаем иконки из EXE
        #
        # 0 = первая иконка
        # ====================================================

        large_icons, small_icons = (
            win32gui.ExtractIconEx(
                exe_path,
                0
            )
        )

        if not large_icons and not small_icons:

            print(
                "[ICON] Иконка не найдена:"
            )

            print(
                "       ",
                exe_path
            )

            return False

        # ====================================================
        # Выбираем большую иконку
        # ====================================================

        if large_icons:

            hicon = large_icons[0]

        elif small_icons:

            hicon = small_icons[0]

        else:

            return False

        # ====================================================
        # Получаем реальный размер системной иконки
        # ====================================================

        icon_info = win32gui.GetIconInfo(
            hicon
        )

        hbm_color = icon_info[4]
        hbm_mask = icon_info[3]

        if not hbm_color:

            print(
                "[ICON] Не удалось получить bitmap:"
            )

            return False

        # ====================================================
        # Bitmap
        # ====================================================

        color_bitmap = win32ui.CreateBitmapFromHandle(
            hbm_color
        )

        bitmap_info = color_bitmap.GetInfo()

        width = bitmap_info["bmWidth"]
        height = bitmap_info["bmHeight"]

        print(
            f"[ICON] Размер исходной иконки: {width}x{height}"
        )

        # ====================================================
        # Получаем пиксели
        # ====================================================

        bitmap_bits = color_bitmap.GetBitmapBits(
            True
        )

        if not bitmap_bits:

            print(
                "[ICON] Bitmap пустой"
            )

            return False

        # ====================================================
        # Создаём изображение
        # ====================================================

        image = Image.frombuffer(
            "RGBA",
            (
                width,
                height
            ),
            bitmap_bits,
            "raw",
            "BGRA",
            0,
            1
        )

        # ====================================================
        # Сохраняем PNG
        # ====================================================

        image.save(
            output_path,
            format="PNG"
        )

        # Проверяем, что файл действительно появился
        if not os.path.isfile(output_path):

            print(
                "[ICON ERROR] PNG не был создан"
            )

            return False

        file_size = os.path.getsize(
            output_path
        )

        if file_size <= 0:

            print(
                "[ICON ERROR] PNG пустой"
            )

            return False

        print(
            "[ICON OK]",
            os.path.basename(output_path),
            f"({width}x{height}, {file_size} bytes)"
        )

        return True

    except Exception as e:

        print()
        print(
            "[ICON ERROR]"
        )

        print(
            "EXE:",
            exe_path
        )

        print(
            "ERROR:",
            repr(e)
        )

        return False

    finally:

        # ====================================================
        # Освобождаем Windows handles
        # ====================================================

        for icon in large_icons:

            try:
                win32gui.DestroyIcon(
                    icon
                )
            except Exception:
                pass

        for icon in small_icons:

            try:
                win32gui.DestroyIcon(
                    icon
                )
            except Exception:
                pass


# ============================================================
# СОЗДАНИЕ ОДНОЙ ИКОНКИ ИЗ GAME
# ============================================================

def create_game_icon(game):

    if not isinstance(game, dict):

        return False

    name = game.get(
        "name",
        ""
    )

    exe = game.get(
        "exe",
        ""
    )

    if not name:

        print(
            "[ICON SKIP] Нет названия"
        )

        return False

    filename = (
        safe_filename(name)
        + ".png"
    )

    output_path = os.path.join(
        ICONS_DIR,
        filename
    )

    # ========================================================
    # НЕ ПЕРЕЗАПИСЫВАЕМ
    # ========================================================

    if os.path.isfile(output_path):

        print(
            "[ICON SKIP]",
            name,
            "- уже существует"
        )

        return True

    print()
    print(
        "[ICON CREATE]",
        name
    )

    print(
        "EXE:",
        exe
    )

    return extract_icon(
        exe,
        output_path
    )


# ============================================================
# СОЗДАТЬ ВСЕ ИКОНКИ
# ============================================================

def main():

    print()
    print("=" * 70)
    print("                    CREATE GAME ICONS")
    print("=" * 70)
    print()

    # ========================================================
    # Проверяем JSON
    # ========================================================

    if not os.path.isfile(GAMES_FILE):

        print(
            "[ERROR] Не найден:"
        )

        print(
            GAMES_FILE
        )

        return

    # ========================================================
    # Загружаем JSON
    # ========================================================

    try:

        with open(
            GAMES_FILE,
            "r",
            encoding="utf-8"
        ) as f:

            games = json.load(f)

    except Exception as e:

        print(
            "[JSON ERROR]",
            repr(e)
        )

        return

    if not isinstance(games, list):

        print(
            "[ERROR] scaned_games.json должен содержать список"
        )

        return

    print(
        "Игр найдено:",
        len(games)
    )

    print(
        "Папка:",
        ICONS_DIR
    )

    print()

    success = 0
    skipped = 0
    failed = 0

    # ========================================================
    # ИГРЫ
    # ========================================================

    for index, game in enumerate(
        games,
        1
    ):

        print(
            "-" * 70
        )

        print(
            f"[{index}/{len(games)}]"
        )

        if not isinstance(game, dict):

            print(
                "[SKIP] Некорректная запись"
            )

            skipped += 1

            continue

        name = game.get(
            "name",
            ""
        )

        if not name:

            print(
                "[SKIP] Нет названия"
            )

            skipped += 1

            continue

        output_path = os.path.join(
            ICONS_DIR,
            safe_filename(name) + ".png"
        )

        # ====================================================
        # Уже существует
        # ====================================================

        if os.path.isfile(output_path):

            print(
                "[SKIP] Уже существует:",
                name
            )

            skipped += 1

            continue

        # ====================================================
        # Создание
        # ====================================================

        if create_game_icon(game):

            success += 1

        else:

            failed += 1

    # ========================================================
    # РЕЗУЛЬТАТ
    # ========================================================

    print()
    print("=" * 70)
    print("                           ГОТОВО")
    print("=" * 70)

    print(
        "Создано:",
        success
    )

    print(
        "Пропущено:",
        skipped
    )

    print(
        "Ошибок:",
        failed
    )

    print(
        "Всего:",
        len(games)
    )

    print()

    print(
        "Иконки:",
        ICONS_DIR
    )

    print("=" * 70)
    print()


# ============================================================
# START
# ============================================================

if __name__ == "__main__":

    main()