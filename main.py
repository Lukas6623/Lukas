import asyncio
import importlib
import os
import sys
import subprocess
import json
from telethon import TelegramClient, events

# Путь к файлу конфигурации
CONFIG_FILE = "config.json"
USER_DATA_FILE = "user_data.txt"  # Файл с данными пользователей
MODULE_FOLDER = "modules"  # Папка с модулями
LANG_FILE = "modules/language.txt"  # Файл с языковыми настройками

def install_libraries(module_name):
    """ Устанавливает библиотеку, если она отсутствует. """
    try:
        importlib.import_module(module_name)
    except ImportError:
        subprocess.run([sys.executable, "-m", "pip", "install", module_name], check=True)

def load_language():
    """ Загружает язык из файла или использует 'en' по умолчанию """
    if os.path.exists(LANG_FILE):
        with open(LANG_FILE, "r", encoding="utf-8") as file:
            lang_code = file.read().strip().lower()
    else:
        lang_code = "en"  # По умолчанию английский

    try:
        lang_module = importlib.import_module(f"languages.{lang_code}")
        return lang_module.LANG
    except ModuleNotFoundError:
        print(f"⚠️ Язык '{lang_code}' не найден, используется английский")
        lang_module = importlib.import_module("languages.en")
        return lang_module.LANG

def load_config():
    """ Загружает конфигурацию из файла. Если файла нет, возвращает None. """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return None

def save_config(api_id, api_hash, token=None):
    """ Сохраняет конфигурацию в файл. """
    config = {"api_id": api_id, "api_hash": api_hash}
    if token:
        config["token"] = token  # Добавляем токен, если передан
    
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file)

# Загружаем язык
LANG = load_language()

async def load_modules(userbot):
    """ Загружает модули из папки 'modules'. """
    modules_info = {}
    for filename in os.listdir(MODULE_FOLDER):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                module_name = filename[:-3]  # Убираем расширение .py
                module = importlib.import_module(f"modules.{module_name}")
                
                commands = getattr(module, 'COMMANDS', [])
                if hasattr(module, 'register_module'):
                    register_function = getattr(module, 'register_module')
                    if asyncio.iscoroutinefunction(register_function):
                        await register_function(userbot)
                    else:
                        register_function(userbot)
                    print(LANG["module_loaded"].format(name=module_name))
                else:
                    print(LANG["missing_register"].format(name=module_name))
                
                modules_info[module_name] = commands
            except Exception as e:
                print(LANG["module_error"].format(name=filename, error=e))
    return modules_info

async def user_bot():
    """ Основной код для юзер-бота. """
    config = load_config()
    
    if config:
        API_ID = config["api_id"]
        API_HASH = config["api_hash"]
        TOKEN = config.get("token")  # Чтение токена из конфигурации, если он есть
    else:
        print("Please enter your bot token:")
        TOKEN = input()  # Запрашиваем токен у пользователя
        print("Please enter your API ID:")
        API_ID = input()
        print("Please enter your API Hash:")
        API_HASH = input()
        save_config(API_ID, API_HASH, TOKEN)  # Сохраняем токен, API_ID и API_HASH в конфиг
    
    userbot = TelegramClient("userbot", API_ID, API_HASH)
    await userbot.start()

    modules_info = await load_modules(userbot)

    @userbot.on(events.NewMessage(pattern=r"\.restart"))
    async def restart_command(event):
        message = await event.reply(LANG["restart_message"])
        print(LANG["restart_message_terminal"])
        python = sys.executable
        os.execl(python, python, *sys.argv)
        await asyncio.sleep(2)
        await message.edit(LANG["restart_completed"])

    # Запуск второго бота (bot.py)
    try:
        bot_process = subprocess.Popen(
            [sys.executable, 'bot.py'],
            stdout=sys.stdout,
            stderr=sys.stderr,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )
        print("✅ bot.py успешно запущен")
    except Exception as e:
        print(f"❌ Ошибка при запуске bot.py: {e}")

    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(user_bot())
