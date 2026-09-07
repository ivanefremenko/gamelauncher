"""
scan_steam_users.py
Сканирует всех пользователей Steam на компьютере
Возвращает список с их ID и никнеймами
"""

import os
import re
from pathlib import Path
from typing import List, Tuple, Optional

try:
    import vdf
except ImportError:
    print("⚠️  Библиотека 'vdf' не установлена. Использую ручной парсинг.")
    vdf = None


def get_steam_users() -> List[Tuple[str, str]]:
    """
    Сканирует всех пользователей Steam на компьютере.
    
    Returns:
        List[Tuple[str, str]]: Список кортежей (steam_id, username)
        Пример: [("123456789", "Gamer123"), ("987654321", "Player456")]
    """
    users = []
    
    try:
        # Путь к папке с данными пользователей
        userdata_path = Path("C:\\Program Files (x86)\\Steam\\userdata")
        if not userdata_path.exists():
            print("⚠️  Папка userdata не найдена.")
            return users
        
        # Путь к файлу с именами пользователей
        login_file = Path("C:\\Program Files (x86)\\Steam\\config\\loginusers.vdf")
        
        # Словарь для хранения имен по ID
        account_names = {}
        
        # Пытаемся прочитать имена из loginusers.vdf
        if login_file.exists():
            try:
                with open(login_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Парсим файл вручную (работает без vdf)
                # Ищем блоки пользователей: "AccountID" "123456789" { ... "PersonaName" "Gamer123" ... }
                import re
                
                # Ищем все блоки пользователей
                user_blocks = re.findall(r'"(\d+)"\s*\{([^}]+)\}', content)
                for account_id, block in user_blocks:
                    # Ищем PersonaName (отображаемое имя)
                    persona_match = re.search(r'"PersonaName"\s+"([^"]+)"', block)
                    if persona_match:
                        account_names[account_id] = persona_match.group(1)
                    else:
                        # Если PersonaName нет, ищем AccountName
                        acc_match = re.search(r'"AccountName"\s+"([^"]+)"', block)
                        if acc_match:
                            account_names[account_id] = acc_match.group(1)
                        
            except Exception as e:
                print(f"⚠️  Ошибка чтения loginusers.vdf: {e}")
        
        # Сканируем папки пользователей
        for item in userdata_path.iterdir():
            if item.is_dir() and item.name.isdigit():
                steam_id = item.name
                
                # Получаем имя пользователя
                username = account_names.get(steam_id, "")
                
                # Если имя не найдено, пытаемся прочитать из localconfig.vdf
                if not username:
                    local_config = item / "config" / "localconfig.vdf"
                    if local_config.exists():
                        try:
                            with open(local_config, 'r', encoding='utf-8') as f:
                                content = f.read()
                                name_match = re.search(r'"PersonaName"\s+"([^"]+)"', content)
                                if name_match:
                                    username = name_match.group(1)
                        except:
                            pass
                
                # Если все еще нет имени, используем Steam ID
                if not username:
                    username = steam_id
                
                users.append((steam_id, username))
        
        # Сортируем пользователей по имени
        users.sort(key=lambda x: x[1].lower())
        
    except Exception as e:
        print(f"❌ Ошибка при сканировании пользователей: {e}")
    
    return users


def get_user_by_id(steam_id: str) -> Optional[str]:
    """
    Получает никнейм пользователя по Steam ID.
    
    Args:
        steam_id: Steam ID пользователя
        
    Returns:
        str: Никнейм пользователя или None, если не найден
    """
    users = get_steam_users()
    for sid, username in users:
        if sid == steam_id:
            return username
    return None


def get_user_by_name(username: str) -> Optional[str]:
    """
    Получает Steam ID пользователя по никнейму.
    
    Args:
        username: Никнейм пользователя
        
    Returns:
        str: Steam ID или None, если не найден
    """
    users = get_steam_users()
    for sid, name in users:
        if name.lower() == username.lower():
            return sid
    return None


def print_users(users: List[Tuple[str, str]]):
    """
    Выводит список пользователей в красивом формате.
    
    Args:
        users: Список кортежей (steam_id, username)
    """
    if not users:
        print("❌ Пользователи не найдены.")
        return
    
    print("\n" + "=" * 50)
    print(" 👤 ПОЛЬЗОВАТЕЛИ STEAM")
    print("=" * 50)
    
    for i, (steam_id, username) in enumerate(users, 1):
        print(f" {i}. {username}")
        print(f"    ID: {steam_id}")
    
    print("=" * 50)
    print(f"📊 Всего: {len(users)} пользователей")
    print("=" * 50)


# ============================================================
# ОСНОВНАЯ ФУНКЦИЯ
# ============================================================

def main():
    """
    Главная функция для тестирования.
    Запускает сканирование пользователей и выводит результат.
    """
    print("=" * 50)
    print(" SCAN STEAM USERS v2.0")
    print("=" * 50)
    print("\n🔍 Поиск пользователей Steam...")
    
    # Получаем список пользователей
    users = get_steam_users()
    
    # Выводим результат
    print_users(users)
    
    # Дополнительная информация для использования
    if users:
        print("\n💡 Пример использования в других скриптах:")
        print("   from scan_steam_users import get_steam_users")
        print("   users = get_steam_users()")
        print(f"   # users = {users}")
    
    return users


# ============================================================
# АВТОМАТИЧЕСКИЙ ЗАПУСК ПРИ ИМПОРТЕ ИЛИ ЗАПУСКЕ СКРИПТА
# ============================================================

if __name__ == "__main__":
    # Запускаем основную функцию
    users = main()
    
    # Выводим финальный лог
    print("\n" + "=" * 50)
    print("✅ ГОТОВО")
    print("=" * 50)
    print(f"📊 Найдено пользователей: {len(users)}")
    
    if users:
        print("\n📋 Список пользователей:")
        for steam_id, username in users:
            print(f"   • {username} (ID: {steam_id})")
    
    print("=" * 50)