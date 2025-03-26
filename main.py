import asyncio
import importlib
import os
import sys
import subprocess
import json
import logging
from telethon import TelegramClient, events
import psutil  

logging.basicConfig(filename='bot_errors.log', level=logging.ERROR)

CONFIG_FILE = "config.json"
MODULE_FOLDER = "modules"
USER_MODULE_FOLDER = "modules/users_modules"
LANG_FILE = "modules/language.txt"

def load_language():
    """ Загружает язык из файла или использует 'en' по умолчанию """
    if os.path.exists(LANG_FILE):
        with open(LANG_FILE, "r", encoding="utf-8") as file:
            lang_code = file.read().strip().lower()
    else:
        lang_code = "en"

    try:
        lang_module = importlib.import_module(f"languages.{lang_code}")
        return lang_module.LANG, lang_code
    except ModuleNotFoundError:
        print(f"⚠️ Язык '{lang_code}' не найден, используется английский")
        lang_module = importlib.import_module("languages.en")
        return lang_module.LANG, "en"

def load_config():
    """ Загружает конфиг или запрашивает у пользователя """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return None

def save_config(api_id, api_hash, user_id, token=None):
    """ Сохраняет настройки в config.json """
    config = {"api_id": api_id, "api_hash": api_hash, "user_id": user_id}
    if token:
        config["token"] = token  
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)

def kill_existing_processes():
    """ Убивает все запущенные копии main.py, кроме текущего """
    current_pid = os.getpid()
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] != current_pid and proc.info['cmdline']:
                if 'python' in proc.info['name'].lower() and 'main.py' in ' '.join(proc.info['cmdline']):
                    print(f"🔴 Завершаем процесс {proc.info['pid']}")
                    proc.terminate()
                    proc.wait(timeout=3)
                    if proc.is_running():
                        proc.kill()
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

async def check_language_change():
    """ Проверяет изменение языка каждые 2 секунды """
    global LANG, current_lang
    while True:
        new_lang, lang_code = load_language()
        if lang_code != current_lang:
            LANG = new_lang
            current_lang = lang_code
            print(f"🔄 Язык изменён на {current_lang}")
        await asyncio.sleep(2)

async def load_modules(userbot, folder):
    """ Загружает модули из указанной папки """
    modules_info = {}
    if not os.path.exists(folder):
        print(f"⚠️ Папка {folder} не найдена!")
        return modules_info

    for filename in os.listdir(folder):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                module_name = filename[:-3]
                full_import_path = f"{folder.replace('/', '.')}.{module_name}"

                module = importlib.import_module(full_import_path)
                commands = getattr(module, 'COMMANDS', [])

                if hasattr(module, 'register_module'):
                    register_function = getattr(module, 'register_module')
                    if asyncio.iscoroutinefunction(register_function):
                        await register_function(userbot)
                    else:
                        register_function(userbot)
                    print(f"✅ Модуль {module_name} загружен!")
                else:
                    print(f"⚠️ {module_name} не содержит register_module")

                modules_info[module_name] = commands
            except Exception as e:
                print(f"❌ Ошибка в модуле {filename}: {e}")

    return modules_info

async def user_bot():
    global LANG, current_lang
    LANG, current_lang = load_language()

    config = load_config()
    if config:
        API_ID = config["api_id"]
        API_HASH = config["api_hash"]
        TOKEN = config.get("token")
    else:
        print("Введите API ID:")
        API_ID = input()
        print("Введите API Hash:")
        API_HASH = input()
        print("Введите Token (если есть):")
        TOKEN = input() or None

    userbot = TelegramClient("userbot", API_ID, API_HASH)
    await userbot.start()

    user = await userbot.get_me()
    USER_ID = user.id
    save_config(API_ID, API_HASH, USER_ID, TOKEN)

    asyncio.create_task(check_language_change())

    await load_modules(userbot, MODULE_FOLDER)  
    await load_modules(userbot, USER_MODULE_FOLDER)  

    @userbot.on(events.NewMessage(pattern=r"\.restart"))
    async def restart_command(event):
        try:
            message = await event.reply(LANG["restart_message"])
            print(LANG["restart_message_terminal"])

            kill_existing_processes()
            await asyncio.sleep(2)

            if os.name == "nt":
                subprocess.call(["exit"])
                os.execv(sys.executable, ['python', 'main.py'])
            else:
                subprocess.call(["exit"])
                os.execv(sys.executable, ['python3', 'main.py'])

        except Exception as e:
            print(f"Ошибка при перезапуске: {e}")

    try:
        inline_process = subprocess.Popen(
            [sys.executable, 'inline.py'],
            stdout=sys.stdout,
            stderr=sys.stderr,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0
        )
        print("✅ inline.py успешно запущен")
    except Exception as e:
        print(f"❌ Ошибка при запуске inline.py: {e}")

    print("✅ Бот запущен!")
    await userbot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(user_bot())
