"""
scan_steam_games.py
Сканирует установленные игры Steam для указанного аккаунта и сохраняет в JSON
"""

import os
import re
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

try:
    import vdf
except ImportError:
    print("❌ Библиотека 'vdf' не установлена.")
    print("Установите: pip install vdf")
    exit(1)

def scan_steam_games(steam_id: str, output_file: str = "steam_licensed_games.json") -> Dict[str, Dict]:
    """
    Сканирует все установленные игры Steam для указанного аккаунта.
    
    Args:
        steam_id (str): Steam ID пользователя (числовая строка из папки userdata)
        output_file (str): Имя выходного JSON файла (по умолчанию: steam_license_games.json)
    
    Returns:
        Dict[str, Dict]: Словарь с информацией об играх, где ключ - AppID
    """
    
    print(f"🔍 Сканирование игр для аккаунта: {steam_id}")
    print("=" * 60)
    
    def find_steam_folders() -> List[Path]:
        """Ищет все папки Steam на всех дисках."""
        steam_folders = set()
        
        for drive in range(ord('C'), ord('Z') + 1):
            drive_letter = chr(drive) + ":"
            if not os.path.exists(drive_letter):
                continue
                
            possible_paths = [
                Path(f"{drive_letter}\\Program Files (x86)\\Steam"),
                Path(f"{drive_letter}\\Program Files\\Steam"),
                Path(f"{drive_letter}\\Steam"),
            ]
            
            for path in possible_paths:
                if path.exists() and (path / "steam.exe").exists():
                    steam_folders.add(path)
        
        return list(steam_folders)

    def get_library_folders(steam_path: Path) -> List[Path]:
        """Читает libraryfolders.vdf и возвращает все папки библиотек."""
        library_folders = [steam_path / "steamapps"]
        
        library_file = steam_path / "steamapps" / "libraryfolders.vdf"
        if not library_file.exists():
            return library_folders
        
        try:
            with open(library_file, 'r', encoding='utf-8') as f:
                data = vdf.load(f)
            
            if "libraryfolders" in data:
                for key, value in data["libraryfolders"].items():
                    if "path" in value:
                        path = Path(value["path"])
                        if path.exists():
                            library_folders.append(path / "steamapps")
                            
        except Exception as e:
            print(f"⚠️  Ошибка чтения libraryfolders.vdf: {e}")
        
        return library_folders

    def parse_manifest(file_path: Path) -> Optional[Tuple[str, str]]:
        """Парсит appmanifest_*.acf файл и возвращает (appid, name)."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            appid_pattern = r'"appid"\s+"(\d+)"'
            name_pattern = r'"name"\s+"([^"]+)"'
            
            appid_match = re.search(appid_pattern, content)
            name_match = re.search(name_pattern, content)
            
            if appid_match and name_match:
                return (appid_match.group(1), name_match.group(1))
                
        except Exception as e:
            print(f"⚠️  Ошибка чтения {file_path.name}: {e}")
        
        return None

    def find_game_path(library_path: Path, appid: str, game_name: str) -> Optional[str]:
        """Находит путь к игре по AppID и названию в библиотеке."""
        common_path = library_path / "common"
        if not common_path.exists():
            return None
        
        # Ищем папку с названием игры
        for item in common_path.iterdir():
            if item.is_dir():
                # Точное совпадение (регистронезависимо)
                if item.name.lower() == game_name.lower():
                    return str(item)
                # Частичное совпадение
                if game_name.lower() in item.name.lower():
                    return str(item)
        
        return None

    def get_playtime_from_steam(steam_id: str, appid: str) -> int:
        """Получает время игры из localconfig.vdf для указанного аккаунта."""
        try:
            userdata_path = Path(f"C:\\Program Files (x86)\\Steam\\userdata\\{steam_id}\\config\\localconfig.vdf")
            
            if not userdata_path.exists():
                return 0
            
            with open(userdata_path, 'r', encoding='utf-8') as f:
                data = vdf.load(f)
            
            try:
                playtime = data.get("UserLocalConfigStore", {}).get("Software", {}).get("Valve", {}).get("Steam", {}).get("apps", {}).get(appid, {}).get("Playtime", 0)
                return int(playtime)
            except:
                return 0
                
        except Exception as e:
            print(f"⚠️  Ошибка получения времени для {appid}: {e}")
            return 0

    def get_account_name(steam_id: str) -> str:
        """Пытается получить имя аккаунта по Steam ID."""
        try:
            login_file = Path("C:\\Program Files (x86)\\Steam\\config\\loginusers.vdf")
            if not login_file.exists():
                return steam_id
            
            with open(login_file, 'r', encoding='utf-8') as f:
                data = vdf.load(f)
            
            if "users" in data:
                for key, value in data["users"].items():
                    if value.get("AccountID") == steam_id:
                        return value.get("PersonaName", steam_id)
        except:
            pass
        
        return steam_id

    # ===== ОСНОВНАЯ ЛОГИКА =====
    
    games = {}
    
    # Получаем имя аккаунта
    account_name = get_account_name(steam_id)
    print(f"👤 Аккаунт: {account_name} (ID: {steam_id})")
    
    # Находим папки Steam
    print("🔍 Поиск папок Steam...")
    steam_folders = find_steam_folders()
    
    if not steam_folders:
        print("❌ Steam не найден на этом компьютере.")
        return games
    
    print(f"✅ Найдено папок Steam: {len(steam_folders)}")
    
    # Собираем все библиотеки
    all_library_folders = []
    for steam_path in steam_folders:
        print(f"📁 Проверка: {steam_path}")
        library_folders = get_library_folders(steam_path)
        all_library_folders.extend(library_folders)
    
    print(f"📂 Найдено папок библиотек: {len(all_library_folders)}")
    
    # Обрабатываем каждую библиотеку
    processed_appids = set()
    game_count = 0
    
    for library_path in all_library_folders:
        if not library_path.exists():
            continue
        
        print(f"\n📂 Библиотека: {library_path}")
        
        # Ищем файлы манифестов
        manifest_files = list(library_path.glob("appmanifest_*.acf"))
        print(f"   Найдено манифестов: {len(manifest_files)}")
        
        for manifest_file in manifest_files:
            result = parse_manifest(manifest_file)
            if not result:
                continue
            
            appid, name = result
            
            # Пропускаем уже обработанные игры
            if appid in processed_appids:
                continue
            processed_appids.add(appid)
            
            # Пропускаем инструменты и системные приложения
            skip_keywords = ["steamworks", "tool", "sdk", "dedicated server", "source sdk"]
            if any(keyword in name.lower() for keyword in skip_keywords):
                continue
            
            # Ищем путь к игре
            game_path = find_game_path(library_path, appid, name)
            
            # Получаем время игры для указанного аккаунта
            playtime_minutes = get_playtime_from_steam(steam_id, appid)
            
            # Собираем информацию
            game_info = {
                "name": name,
                "appid": appid,
                "path": game_path,
                "library_path": str(library_path),
                "playtime_minutes": playtime_minutes,
                "playtime_hours": round(playtime_minutes / 60, 2),
                "manifest_path": str(manifest_file),
                "is_installed": game_path is not None,
                "steam_id": steam_id,
                "account_name": account_name
            }
            
            games[appid] = game_info
            game_count += 1
            
            # Выводим информацию
            status = "✅" if game_path else "❌"
            print(f"   {status} {name} (AppID: {appid})")
            if game_path:
                print(f"      📁 Путь: {game_path}")
            if playtime_minutes > 0:
                hours = playtime_minutes // 60
                minutes = playtime_minutes % 60
                print(f"      ⏱️  Время: {hours} ч {minutes} мин")
    
    print(f"\n✅ Всего найдено игр: {game_count}")

    from datetime import datetime

    # Сохраняем в JSON
    output_data = {
        "steam_id": steam_id,
        "account_name": account_name,
        "total_games": game_count,
        "scan_date": datetime.now().isoformat(),
        "games": games
    }
    
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n💾 Данные сохранены в: {output_file}")
        print(f"   Размер файла: {Path(output_file).stat().st_size / 1024:.2f} КБ")
    except Exception as e:
        print(f"❌ Ошибка сохранения файла: {e}")
    
    return games


# ============================================================
# САМОСТОЯТЕЛЬНЫЙ ЗАПУСК
# ============================================================

if __name__ == "__main__":
    print("=" * 60)
    print(" SCAN STEAM GAMES v1.0")
    print("=" * 60)
    print()
    
    # Функция для поиска всех аккаунтов
    def find_all_accounts():
        accounts = []
        try:
            userdata_path = Path("C:\\Program Files (x86)\\Steam\\userdata")
            if not userdata_path.exists():
                return accounts
            
            # Пытаемся прочитать имена аккаунтов
            login_file = Path("C:\\Program Files (x86)\\Steam\\config\\loginusers.vdf")
            account_names = {}
            
            if login_file.exists():
                try:
                    with open(login_file, 'r', encoding='utf-8') as f:
                        data = vdf.load(f)
                    if "users" in data:
                        for key, value in data["users"].items():
                            account_id = value.get("AccountID")
                            if account_id:
                                account_names[account_id] = value.get("PersonaName", account_id)
                except:
                    pass
            
            for item in userdata_path.iterdir():
                if item.is_dir() and item.name.isdigit():
                    steam_id = item.name
                    name = account_names.get(steam_id, steam_id)
                    accounts.append((steam_id, name))
        except:
            pass
        return accounts
    
    # Ищем аккаунты
    accounts = find_all_accounts()
    
    if not accounts:
        print("❌ Аккаунты Steam не найдены.")
        print("Убедитесь, что Steam установлен и вы входили в аккаунт.")
        exit(1)
    
    print("👤 Найдены аккаунты Steam:")
    for i, (steam_id, name) in enumerate(accounts, 1):
        print(f"   {i}. {name} (ID: {steam_id})")
    
    # Выбираем аккаунт
    if len(accounts) == 1:
        steam_id, name = accounts[0]
        print(f"\n✅ Используется единственный аккаунт: {name}")
    else:
        print("\n💡 Выберите аккаунт (введите номер):")
        while True:
            try:
                choice = input("> ").strip()
                if not choice:
                    steam_id, name = accounts[0]
                    print(f"\n✅ Выбран первый аккаунт: {name}")
                    break
                
                idx = int(choice) - 1
                if 0 <= idx < len(accounts):
                    steam_id, name = accounts[idx]
                    print(f"\n✅ Выбран аккаунт: {name}")
                    break
                else:
                    print("❌ Неверный номер. Попробуйте снова.")
            except ValueError:
                print("❌ Введите число.")
    
    print()
    
    # Запускаем сканирование
    output_file = "steam_license_games.json"
    games = scan_steam_games(steam_id, output_file)
    
    if games:
        print("\n📊 ИТОГО:")
        print(f"   Аккаунт: {games[next(iter(games))]['account_name']}")
        print(f"   Steam ID: {steam_id}")
        print(f"   Найдено игр: {len(games)}")
        
        # Статистика по времени
        total_minutes = sum(g['playtime_minutes'] for g in games.values())
        total_hours = total_minutes // 60
        print(f"   Общее время: {total_hours} ч")
        
        # Топ игр
        if total_minutes > 0:
            print("\n🏆 Топ игр по наигранному времени:")
            sorted_games = sorted(games.values(), key=lambda x: x['playtime_minutes'], reverse=True)[:5]
            for i, game in enumerate(sorted_games, 1):
                if game['playtime_minutes'] > 0:
                    hours = game['playtime_minutes'] // 60
                    minutes = game['playtime_minutes'] % 60
                    print(f"   {i}. {game['name']} - {hours} ч {minutes} мин")
    else:
        print("❌ Игры не найдены.")