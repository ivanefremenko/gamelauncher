
import json
import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import webview
import pystray

from PIL import Image, ImageDraw


# ============================================================
# НАСТРОЙКИ
# ============================================================

HOST = "127.0.0.1"
PORT = 8765

import sys
import os

if getattr(sys, "frozen", False):
    BASE_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LAUNCHER_FILE = os.path.join(BASE_DIR, "launcher.html")
LOGIN_FILE = os.path.join(BASE_DIR, "login.html")

COVERS_DIR = os.path.join(BASE_DIR, "covers")
os.makedirs(COVERS_DIR, exist_ok=True)

SELECTED_ACCOUNT = None

window = None
tray = None

server = None


# ============================================================
# ИГРЫ
# ============================================================

games = [

    {
        "id": 730,
        "name": "Counter-Strike 2",
        "short": "Counter-Strike 2",
        "hours": "316,1 ч.",
        "ach": "1 / 1",

        "achievements": [
            {
                "name": "Новая мета",
                "description": "Выиграйте матч.",
                "progress": "100%"
            },
            {
                "name": "Победитель",
                "description": "Добейтесь победы.",
                "progress": "100%"
            },
            {
                "name": "Командная работа",
                "description": "Сыграйте вместе с командой.",
                "progress": "100%"
            }
        ],

        "screenshots": [
            "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRSpxDB4Lq6AaMUC7A3kK5zfB79SMK6GKnEYpYKF_h_R8jnf-Cf4xa4mUcQ&s=10",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/730/ss_2.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/730/ss_3.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/730/ss_4.jpg"
        ],

        "news": [
            "Обновление Counter-Strike 2",
            "Обновление Counter-Strike 2",
            "Обновление Counter-Strike 2"
        ],

        "dates": [
            "25 АВГУСТА",
            "20 АВГУСТА",
            "13 АВГУСТА"
        ]
    },


    {
        "id": 548430,
        "name": "Deep Rock Galactic",
        "short": "Deep Rock Galactic",
        "hours": "184,7 ч.",
        "ach": "69 / 69",

        "achievements": [
            {
                "name": "Rock and Stone!",
                "description": "Добудьте ресурсы вместе.",
                "progress": "100%"
            },
            {
                "name": "Опасная работа",
                "description": "Завершите сложную миссию.",
                "progress": "100%"
            },
            {
                "name": "Глубокая шахта",
                "description": "Спуститесь глубоко под землю.",
                "progress": "100%"
            }
        ],

        "screenshots": [
            "https://shared.steamstatic.com/store_item_assets/steam/apps/548430/ss_1.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/548430/ss_2.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/548430/ss_3.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/548430/ss_4.jpg"
        ],

        "news": [
            "Season 06: The Dreadnought Awakens",
            "Maintenance & Hotfix",
            "Weekly Core Hunt"
        ],

        "dates": [
            "2 СЕНТЯБРЯ",
            "29 АВГУСТА",
            "22 АВГУСТА"
        ]
    },


    {
        "id": 975370,
        "name": "Oxygen Not Included",
        "short": "Oxygen Not Included",
        "hours": "92,4 ч.",
        "ach": "32 / 48",

        "achievements": [
            {
                "name": "Первый день",
                "description": "Переживите первый цикл.",
                "progress": "100%"
            },
            {
                "name": "Колония",
                "description": "Создайте устойчивую базу.",
                "progress": "75%"
            },
            {
                "name": "Инженер",
                "description": "Создайте сложную систему.",
                "progress": "45%"
            }
        ],

        "screenshots": [
            "https://shared.steamstatic.com/store_item_assets/steam/apps/975370/ss_1.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/975370/ss_2.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/975370/ss_3.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/975370/ss_4.jpg"
        ],

        "news": [
            "Quality of Life Update",
            "Hotfix Update",
            "Community Update"
        ],

        "dates": [
            "31 АВГУСТА",
            "25 АВГУСТА",
            "17 АВГУСТА"
        ]
    },


    {
        "id": 739630,
        "name": "Phasmophobia",
        "short": "Phasmophobia",
        "hours": "74,2 ч.",
        "ach": "28 / 60",

        "achievements": [
            {
                "name": "Первое расследование",
                "description": "Найдите доказательства.",
                "progress": "100%"
            },
            {
                "name": "Охотник за призраками",
                "description": "Завершите расследование.",
                "progress": "70%"
            },
            {
                "name": "Профессионал",
                "description": "Пройдите сложное расследование.",
                "progress": "30%"
            }
        ],

        "screenshots": [
            "https://shared.steamstatic.com/store_item_assets/steam/apps/739630/ss_1.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/739630/ss_2.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/739630/ss_3.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/739630/ss_4.jpg"
        ],

        "news": [
            "Chronicle Update",
            "Hotfix",
            "Developer Preview"
        ],

        "dates": [
            "30 АВГУСТА",
            "21 АВГУСТА",
            "10 АВГУСТА"
        ]
    },


    {
        "id": 108600,
        "name": "Project Zomboid",
        "short": "Project Zomboid",
        "hours": "63,8 ч.",
        "ach": "14 / 37",

        "achievements": [
            {
                "name": "Первый день",
                "description": "Переживите первый день.",
                "progress": "100%"
            },
            {
                "name": "Выживший",
                "description": "Продержитесь неделю.",
                "progress": "50%"
            },
            {
                "name": "Строитель",
                "description": "Создайте убежище.",
                "progress": "35%"
            }
        ],

        "screenshots": [
            "https://shared.steamstatic.com/store_item_assets/steam/apps/108600/ss_1.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/108600/ss_2.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/108600/ss_3.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/108600/ss_4.jpg"
        ],

        "news": [
            "Build 42 Update",
            "Stable Branch Update",
            "Community News"
        ],

        "dates": [
            "28 АВГУСТА",
            "16 АВГУСТА",
            "4 АВГУСТА"
        ]
    },


    {
        "id": 1229490,
        "name": "ULTRAKILL",
        "short": "ULTRAKILL",
        "hours": "41,6 ч.",
        "ach": "19 / 50",

        "achievements": [
            {
                "name": "Первый уровень",
                "description": "Завершите первый уровень.",
                "progress": "100%"
            },
            {
                "name": "Без остановки",
                "description": "Продолжайте движение.",
                "progress": "65%"
            },
            {
                "name": "ULTRAKILL",
                "description": "Получите высокий ранг.",
                "progress": "40%"
            }
        ],

        "screenshots": [
            "https://shared.steamstatic.com/store_item_assets/steam/apps/1229490/ss_1.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/1229490/ss_2.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/1229490/ss_3.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/1229490/ss_4.jpg"
        ],

        "news": [
            "Full Arsenal Update",
            "Cyber Grind Update",
            "Patch Notes"
        ],

        "dates": [
            "27 АВГУСТА",
            "15 АВГУСТА",
            "7 АВГУСТА"
        ]
    },


    {
        "id": 892970,
        "name": "Valheim",
        "short": "Valheim",
        "hours": "38,1 ч.",
        "ach": "21 / 57",

        "achievements": [
            {
                "name": "Первое поселение",
                "description": "Постройте дом.",
                "progress": "100%"
            },
            {
                "name": "Исследователь",
                "description": "Исследуйте новый биом.",
                "progress": "55%"
            },
            {
                "name": "Воин",
                "description": "Победите опасного врага.",
                "progress": "40%"
            }
        ],

        "screenshots": [
            "https://shared.steamstatic.com/store_item_assets/steam/apps/892970/ss_1.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/892970/ss_2.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/892970/ss_3.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/892970/ss_4.jpg"
        ],

        "news": [
            "Ashlands Update",
            "Patch 0.221.4",
            "Developer News"
        ],

        "dates": [
            "24 АВГУСТА",
            "11 АВГУСТА",
            "1 АВГУСТА"
        ]
    },


    {
        "id": 240,
        "name": "Counter-Strike 1.6",
        "short": "CS 1.6",
        "hours": "126,3 ч.",
        "ach": "—",

        "achievements": [
            {
                "name": "Ветеран",
                "description": "Сыграйте матч.",
                "progress": "100%"
            },
            {
                "name": "Победа",
                "description": "Выиграйте раунд.",
                "progress": "100%"
            }
        ],

        "screenshots": [
            "https://shared.steamstatic.com/store_item_assets/steam/apps/240/ss_1.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/240/ss_2.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/240/ss_3.jpg",
            "https://shared.steamstatic.com/store_item_assets/steam/apps/240/ss_4.jpg"
        ],

        "news": [
            "Обновление клиента",
            "Новости сообщества",
            "Изменение мастер-сервера"
        ],

        "dates": [
            "18 АВГУСТА",
            "4 АВГУСТА",
            "27 ИЮЛЯ"
        ]
    }

]

from scan_steam_users import get_steam_users

# ============================================================
# STEAM USERS
# ============================================================

steam_users = get_steam_users()

print()
print("=" * 60)
print("STEAM USERS")
print("=" * 60)

for steam_id, username in steam_users:
    print(f"{username} ({steam_id})")

print("=" * 60)

# ============================================================
# SCAN + ADD TO STEAM
# ============================================================

GAMES_FILE = os.path.join(BASE_DIR, "scaned_games.json")

from scan_games import scan_games_folders
from add_games_to_steam import add_games_to_steam_shortcuts
from scan_steam_shortcuts import scan_steam_shortcuts


# 1. Сканируем игры на компьютере
scan_games_folders(
    output_file=GAMES_FILE
)


# 2. Добавляем найденные игры в Steam
add_games_to_steam_shortcuts(
    games_file=GAMES_FILE
)


# 3. Сканируем Steam shortcuts.vdf
scan_steam_shortcuts()

# ============================================================
# RESTART STEAM
# ============================================================


import os
import time
import psutil


def restart_steam():
    # Закрываем Steam
    for proc in psutil.process_iter(["name"]):
        try:
            if proc.info["name"] and proc.info["name"].lower() == "steam.exe":
                proc.terminate()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass

    # Ждём завершения
    time.sleep(2)

    # Запускаем Steam
    os.startfile("steam://open/main")

restart_steam()

# ============================================================
# SELECT GAMES
# ============================================================

   

STEAM_LICENSED_FILE = os.path.join(
    BASE_DIR,
    "steam_licensed_games.json"
)

STEAM_SHORTCUTS_FILE = os.path.join(
    BASE_DIR,
    "steam_shortcuts.json"
)

print("STEAM FILE:", STEAM_LICENSED_FILE)
print("FILE EXISTS:", os.path.isfile(STEAM_LICENSED_FILE))

def load_steam_games():
    result = []

    # ========================================================
    # ЛИЦЕНЗИОННЫЕ ИГРЫ STEAM
    # ========================================================

    try:
        with open(
            STEAM_LICENSED_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            data = json.load(f)

        steam_games = data.get("games", {})

        for appid, game in steam_games.items():

            result.append({
                # Steam App ID
                "id": str(
                    game.get("appid", appid)
                ),

                # Название
                "name": game.get("name", ""),

                # Короткое название
                "short": game.get("name", ""),

                # Часы
                "hours": game.get(
                    "playtime_hours",
                    ""
                ),

                "ach": "100%",
                "achievements": [],
                "screenshots": [""],
                "news": [],
                "dates": [],

                # Это обычная Steam-игра
                "localGame": False
            })

    except Exception as e:
        print(
            "STEAM LICENSED GAMES LOAD ERROR:",
            e
        )


    # ========================================================
    # ЛОКАЛЬНЫЕ ИГРЫ ИЗ STEAM SHORTCUTS
    # ========================================================

    try:
        with open(
            STEAM_SHORTCUTS_FILE,
            "r",
            encoding="utf-8"
        ) as f:
            shortcuts = json.load(f)

        for shortcut in shortcuts:

            result.append({
                # У shortcuts нет обычного AppID,
                # поэтому используем steam_url
                "id": str(
                    shortcut.get("steam_url", "")
                ),

                # Название
                "name": shortcut.get(
                    "name",
                    ""
                ),

                # Короткое название
                "short": shortcut.get(
                    "name",
                    ""
                ),

                # Часов пока нет
                "hours": "",

                "ach": "0%",
                "achievements": [],
                "screenshots": [""],
                "news": [],
                "dates": [],

                # Это локальная игра
                "localGame": True,

                # Можно сохранить саму Steam-ссылку
                "steam_url": shortcut.get(
                    "steam_url",
                    ""
                )
            })

    except Exception as e:
        print(
            "STEAM SHORTCUTS LOAD ERROR:",
            e
        )


    return result


from scan_steam_games import scan_steam_games
from scan_steam_screenshots import scan_screenshots

from scan_steam_games import scan_steam_games
from scan_steam_screenshots import scan_screenshots

from make_icons import main as make_icons

def select_games(steam_id):
    global games

    # Сканируем игры
    scan_steam_games(
        steam_id,
        output_file=STEAM_LICENSED_FILE
    )

    # Загружаем игры
    games = load_steam_games()

    # Сканируем скриншоты
    screenshots_data = scan_screenshots(steam_id)

    # Добавляем URL скриншотов каждой игре
    for game in games:

        appid = str(game["id"])

        screenshot_info = screenshots_data.get(appid)

        if screenshot_info:

            game["screenshots"] = [
                f"/steam-screenshot/{appid}/{filename}"
                for filename in [
                    os.path.basename(path)
                    for path in screenshot_info["screenshots"]
                    if "\\thumbnails\\" not in path.lower()
                ]
            ]

        else:
            game["screenshots"] = []

    print("GAMES WITH SCREENSHOTS:")
    print(json.dumps(
        games,
        ensure_ascii=False,
        indent=2
    ))

    make_icons()
 
# ============================================================
# HTTP SERVER
# ============================================================
from urllib.parse import unquote

class Handler(BaseHTTPRequestHandler):
    def send_image(self, path):

        if not os.path.isfile(path):
            self.send_error(404, "Image not found")
            return

        # Определяем Content-Type
        ext = os.path.splitext(path)[1].lower()

        content_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".webp": "image/webp",
            ".bmp": "image/bmp"
        }

        content_type = content_types.get(
            ext,
            "application/octet-stream"
        )

        try:
            file_size = os.path.getsize(path)

            self.send_response(200)

            self.send_header(
                "Content-Type",
                content_type
            )

            self.send_header(
                "Content-Length",
                str(file_size)
            )

            self.send_header(
                "Cache-Control",
                "public, max-age=3600"
            )

            self.end_headers()

            with open(path, "rb") as f:

                while True:

                    chunk = f.read(1024 * 1024)

                    if not chunk:
                        break

                    self.wfile.write(chunk)

        except Exception as e:

            print("IMAGE SEND ERROR:", e)

    def log_message(self, format, *args):
        pass

    def send_json(self, data, status=200):

        body = json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )

        self.end_headers()

        self.wfile.write(body)

    def send_file(self, path):

        if not os.path.isfile(path):
            self.send_error(404, "File not found")
            return

        with open(path, "rb") as f:
            body = f.read()

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(body))
        )

        self.end_headers()

        self.wfile.write(body)

    def do_POST(self):
        global SELECTED_ACCOUNT
        # ------------------------------------------------------------
        # ЗАГРУЗКА БАННЕРА ЛОКАЛЬНОЙ ИГРЫ
        # ------------------------------------------------------------

        if self.path == "/upload_local_banner":

            try:
                content_type = self.headers.get("Content-Type", "")

                if "multipart/form-data" not in content_type:
                    self.send_json({
                        "success": False,
                        "error": "Ожидался multipart/form-data"
                    }, 400)
                    return

                # Получаем boundary
                boundary = None

                for part in content_type.split(";"):
                    part = part.strip()

                    if part.startswith("boundary="):
                        boundary = part.split("=", 1)[1]

                        if boundary.startswith('"') and boundary.endswith('"'):
                            boundary = boundary[1:-1]

                        break

                if not boundary:
                    self.send_json({
                        "success": False,
                        "error": "Boundary не найден"
                    }, 400)
                    return

                content_length = int(
                    self.headers.get("Content-Length", 0)
                )

                body = self.rfile.read(content_length)

                boundary_bytes = (
                    b"--" + boundary.encode("utf-8")
                )

                parts = body.split(boundary_bytes)

                file_data = None
                file_name = None
                game_name = None

                for part in parts:

                    if b"Content-Disposition:" not in part:
                        continue

                    header_end = part.find(b"\r\n\r\n")

                    if header_end == -1:
                        continue

                    headers = part[:header_end].decode(
                        "utf-8",
                        errors="ignore"
                    )

                    data = part[header_end + 4:]

                    # Убираем CRLF и "--"
                    data = data.rstrip(b"\r\n-")

                    # ------------------------------------------------
                    # game_name
                    # ------------------------------------------------

                    if 'name="game_name"' in headers:

                        game_name = data.decode(
                            "utf-8",
                            errors="ignore"
                        ).strip()

                    # ------------------------------------------------
                    # file
                    # ------------------------------------------------

                    elif 'name="file"' in headers:

                        file_data = data

                        import re

                        match = re.search(
                            r'filename="([^"]*)"',
                            headers
                        )

                        if match:
                            file_name = match.group(1)

                if not game_name:
                    self.send_json({
                        "success": False,
                        "error": "Название игры не передано"
                    }, 400)
                    return

                if not file_data:
                    self.send_json({
                        "success": False,
                        "error": "Файл не передан"
                    }, 400)
                    return

                # ------------------------------------------------
                # Безопасное имя игры
                # ------------------------------------------------

                game_name = os.path.basename(game_name)

                # ------------------------------------------------
                # Расширение
                # ------------------------------------------------

                # ------------------------------------------------
                # Конвертируем любое изображение в JPG
                # ------------------------------------------------

                try:

                    from io import BytesIO

                    image = Image.open(
                        BytesIO(file_data)
                    )

                    # Переводим в RGB
                    # Это важно для PNG с прозрачностью
                    if image.mode in ("RGBA", "LA", "P"):
                        background = Image.new(
                            "RGB",
                            image.size,
                            (0, 0, 0)
                        )

                        if image.mode == "P":
                            image = image.convert("RGBA")

                        background.paste(
                            image,
                            mask=image.getchannel("A")
                        )

                        image = background

                    else:
                        image = image.convert("RGB")

                    # Всегда .jpg
                    output_path = os.path.join(
                        COVERS_DIR,
                        game_name + ".jpg"
                    )

                    image.save(
                        output_path,
                        "JPEG",
                        quality=95,
                        optimize=True
                    )

                    print()
                    print("=" * 60)
                    print("LOCAL BANNER SAVED")
                    print("Game:", game_name)
                    print("File:", output_path)
                    print("Size:", os.path.getsize(output_path), "bytes")
                    print("=" * 60)

                except Exception as e:

                    print(
                        "IMAGE CONVERT ERROR:",
                        e
                    )

                    self.send_json({
                        "success": False,
                        "error": "Не удалось обработать изображение: " + str(e)
                    }, 400)

                    return

                print()
                print("=" * 60)
                print("LOCAL BANNER SAVED")
                print("Game:", game_name)
                print("File:", output_path)
                print("Size:", len(file_data), "bytes")
                print("=" * 60)

                self.send_json({
                    "success": True,
                    "filename": os.path.basename(output_path)
                })

            except Exception as e:

                print("UPLOAD BANNER ERROR:", e)

                self.send_json({
                    "success": False,
                    "error": str(e)
                }, 500)

            return
        if self.path == "/select-user":
            try:
                content_length = int(
                    self.headers.get("Content-Length", 0)
                )

                body = self.rfile.read(content_length)

                data = json.loads(body)

                steam_id = data.get("id")

                print()
                print("=" * 50)
                print("SELECTED STEAM USER")
                print("Steam ID:", steam_id)
                print("=" * 50)

                SELECTED_ACCOUNT = steam_id

                select_games(steam_id)

                self.send_json({
                    "success": True
                })

            except Exception as e:
                print("SELECT USER ERROR:", e)

                self.send_json({
                    "success": False,
                    "error": str(e)
                })

            return

    def do_GET(self):
        if self.path.startswith("/game_icon/"):

            game_name = self.path[len("/game_icon/"):]
            game_name = unquote(game_name)

            # Убираем query-параметры типа ?t=123
            game_name = game_name.split("?", 1)[0]

            # Защита от выхода из папки icons
            game_name = os.path.basename(game_name)

            icon_path = os.path.join(
                BASE_DIR,
                "icons",
                game_name + ".png"
            )

            print("[GAME ICON]", game_name)

            if os.path.isfile(icon_path):
                self.send_image(icon_path)
            else:
                print("[GAME ICON NOT FOUND]", icon_path)
                self.send_response(404)
                self.end_headers()

            return
        # ------------------------------------------------------------
        # ЛОКАЛЬНЫЙ БАННЕР ИГРЫ
        # ------------------------------------------------------------

        if self.path.startswith("/local_banner/"):

            try:

                from urllib.parse import urlparse

                parsed = urlparse(self.path)

                game_name = parsed.path[len("/local_banner/"):]

                game_name = unquote(game_name)

                print(
                    "[LOCAL BANNER]",
                    game_name
                )

                extensions = [
                    ".jpg",
                    ".jpeg",
                    ".png",
                    ".webp"
                ]

                for ext in extensions:

                    path = os.path.join(
                        COVERS_DIR,
                        game_name + ext
                    )

                    if os.path.isfile(path):

                        print(
                            "[LOCAL BANNER FOUND]",
                            path
                        )

                        self.send_image(path)

                        return

                print(
                    "[LOCAL BANNER NOT FOUND]",
                    game_name
                )

                self.send_error(
                    404,
                    "Local banner not found"
                )

            except Exception as e:

                print(
                    "LOCAL BANNER ERROR:",
                    e
                )

                self.send_error(
                    500,
                    str(e)
                )

            return
        # ------------------------------------------------------------
        # STEAM SCREENSHOT
        # ------------------------------------------------------------

        if self.path.startswith("/steam-screenshot/"):

            try:

                parts = self.path.split("/")

                # /steam-screenshot/108600/filename.jpg
                if len(parts) < 4:
                    self.send_error(400, "Invalid screenshot URL")
                    return

                appid = parts[2]
                filename = parts[3]

                if not appid.isdigit():
                    self.send_error(400, "Invalid AppID")
                    return

                # Защита от ../
                filename = os.path.basename(filename)

                screenshot_path = os.path.join(
                    r"C:\Program Files (x86)\Steam\userdata",
                    str(SELECTED_ACCOUNT),
                    "760",
                    "remote",
                    str(appid),
                    "screenshots",
                    filename
                )

                print(
                    "[SCREENSHOT]",
                    appid,
                    filename
                )

                self.send_image(screenshot_path)

            except Exception as e:

                print("SCREENSHOT ROUTE ERROR:", e)

                self.send_error(
                    500,
                    str(e)
                )

            return

        # Главная страница
        if self.path == "/":
            self.send_file(LAUNCHER_FILE)
            return

        # Главная страница
        if self.path == "/login":
            self.send_file(LOGIN_FILE)
            return

        # Список игр
        if self.path == "/games":
            self.send_json(games)
            return

        # ------------------------------------------------------------
        # /users
        # ------------------------------------------------------------

        if self.path == "/users":

            users = [
                {
                    "id": steam_id,
                    "name": username
                }
                for steam_id, username in steam_users
            ]

            self.send_json(users)

            return

        # 404
        self.send_json(
            {
                "error": "Not found",
                "path": self.path
            },
            404
        )


def start_server():

    global server

    server = ThreadingHTTPServer(
        (HOST, PORT),
        Handler
    )

    print()
    print("=" * 60)
    print("CHUVAK GAME LAUNCHER")
    print("=" * 60)
    print(f"Launcher: http://{HOST}:{PORT}/")
    print(f"Games:    http://{HOST}:{PORT}/games")
    print("=" * 60)
    print()

    server.serve_forever()

window = None
tray = None
server = None

# ============================================================
# PYWEBVIEW API
# ============================================================
import subprocess

class Api:
    def open_screenshot(self, appid, filename):
        path = os.path.join(
            r"C:\Program Files (x86)\Steam\userdata",
            str(SELECTED_ACCOUNT),
            "760",
            "remote",
            str(appid),
            "screenshots",
            os.path.basename(filename)
        )

        if not os.path.isfile(path):
            return False

        os.startfile(path)
        return True

    def open_url(self, url):
        try:
            if not url:
                return False

            print("[STEAM]", url)

            subprocess.Popen(
                ["cmd", "/c", "start", "", url],
                shell=False
            )

            return True

        except Exception as e:
            print("[STEAM ERROR]", e)
            return False

    def open_steam_url(self, url):
        try:
            if not url:
                return False

            steam_url = f"steam://openurl/{url}"

            print("[STEAM]", steam_url)

            return self.open_url(steam_url)

        except Exception as e:
            print("[STEAM ERROR]", e)
            return False
        
    def login_success(self):
        global window

        print("LOGIN SUCCESS")

        def open_launcher():
            if not window:
                return

            try:
                # Размер окна лаунчера
                window.resize(1200, 800)

                # Переключаем страницу
                window.load_url(
                    f"http://{HOST}:{PORT}/"
                )

                print("Opening launcher...")

            except Exception as e:
                print("LOAD LAUNCHER ERROR:", e)

        # Даём pywebview завершить JS API вызов
        threading.Timer(0.1, open_launcher).start()

        return True

    def minimize(self):

        if window:
            window.hide()

    def maximize(self):
        global window

        if not window:
            return

        try:
            if window.maximized:
                window.restore()
            else:
                window.maximize()

        except Exception as e:
            print("MAXIMIZE ERROR:", e)

    def close(self):

        print("bebee")
        if window:
            window.hide()

    def show(self):

        if window:
            window.show()

            try:
                window.restore()
                window.bring_to_front()
            except Exception:
                pass

    def get_window_position(self):

        if not window:
            return {
                "x": 0,
                "y": 0
            }

        return {
            "x": window.x,
            "y": window.y
        }

    def move_window(self, x, y):

        if window:
            try:
                window.move(
                    int(x),
                    int(y)
                )
            except Exception as e:
                print("MOVE ERROR:", e)

# ============================================================
# TRAY ICON
# ============================================================

def create_tray_icon():

    # Создаём простую иконку прямо из Python.
    # Позже сюда можно поставить настоящий logo.ico.

    size = 64

    image = Image.new(
        "RGBA",
        (size, size),
        (25, 25, 25, 255)
    )

    draw = ImageDraw.Draw(image)

    draw.rounded_rectangle(
        (4, 4, 60, 60),
        radius=12,
        fill=(40, 40, 40, 255)
    )

    draw.text(
        (18, 18),
        "C",
        fill=(255, 255, 255, 255)
    )

    return image


# ============================================================
# TRAY ACTIONS
# ============================================================

def tray_show(icon=None, item=None):

    if window:

        window.show()

        try:
            window.restore()
        except Exception:
            pass

        try:
            window.bring_to_front()
        except Exception:
            pass


def tray_hide(icon=None, item=None):

    if window:
        window.hide()


def tray_exit(icon=None, item=None):

    print("Exiting launcher...")

    # Останавливаем HTTP сервер
    if server:

        try:
            server.shutdown()
        except Exception:
            pass

    # Закрываем окно
    if window:

        try:
            window.destroy()
        except Exception:
            pass

    # Закрываем tray
    if tray:

        try:
            tray.stop()
        except Exception:
            pass


def start_tray():

    global tray

    image = create_tray_icon()

    menu = pystray.Menu(

        pystray.MenuItem(
            "Открыть chuVAK",
            tray_show,
            default=True
        ),

        pystray.MenuItem(
            "Скрыть",
            tray_hide
        ),

        pystray.Menu.SEPARATOR,

        pystray.MenuItem(
            "Выход",
            tray_exit
        )
    )

    tray = pystray.Icon(
        "chuvak_launcher",
        image,
        "chuVAK Game Launcher",
        menu
    )

    tray.run()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    # --------------------------------------------------------
    # HTTP SERVER
    # --------------------------------------------------------

    server_thread = threading.Thread(
        target=start_server,
        daemon=True
    )

    server_thread.start()


    # --------------------------------------------------------
    # PYWEBVIEW API
    # --------------------------------------------------------

    api = Api()


    # --------------------------------------------------------
    # WINDOW
    # --------------------------------------------------------

    window = webview.create_window(

        "chuVAK",

        f"http://{HOST}:{PORT}/login",

        js_api=api,

        width=500,
        height=700,

        min_size=(400, 500),

        resizable=True,

        frameless=True,

        easy_drag=False
    )


    # --------------------------------------------------------
    # TRAY
    # --------------------------------------------------------

    tray_thread = threading.Thread(
        target=start_tray,
        daemon=True
    )

    tray_thread.start()


    # --------------------------------------------------------
    # START WEBVIEW
    # --------------------------------------------------------

    webview.start()