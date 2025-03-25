import asyncio
import importlib
import os
import sys
import subprocess
import json
import logging
from telethon import TelegramClient, events
import psutil  
from aiogram.utils.exceptions import TerminatedByOtherGetUpdates

logging.basicConfig(filename='bot_errors.log', level=logging.ERROR)

CONFIG_FILE = "config.json"
USER_DATA_FILE = "user_data.txt"  
MODULE_FOLDER = "modules"  
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
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return None

def save_config(api_id, api_hash, user_id, token=None):
    config = {"api_id": api_id, "api_hash": api_hash, "user_id": user_id}
    if token:
        config["token"] = token  
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file, indent=4)

def kill_existing_processes():
    current_pid = os.getpid()  # PID текущего процесса
    for proc in psutil.process_iter(attrs=['pid', 'name', 'cmdline']):
        try:
            if proc.info['pid'] != current_pid and proc.info['cmdline']:
                if 'python' in proc.info['name'].lower() and 'main.py' in ' '.join(proc.info['cmdline']):
                    print(f"🔴 Завершаем процесс {proc.info['pid']}")
                    proc.terminate()
                    proc.wait(timeout=3)  # Ждём завершения 3 секунды
                    if proc.is_running():  # Если всё ещё работает, убиваем принудительно
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

async def load_modules(userbot):
    modules_info = {}
    for filename in os.listdir(MODULE_FOLDER):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                module_name = filename[:-3]
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
        print("Введите Token:")
        TOKEN = input()
    
    userbot = TelegramClient("userbot", API_ID, API_HASH)
    await userbot.start()
    
    user = await userbot.get_me()
    USER_ID = user.id
    save_config(API_ID, API_HASH, USER_ID, TOKEN)
    
    asyncio.create_task(check_language_change())  
    modules_info = await load_modules(userbot)
    
    @userbot.on(events.NewMessage(pattern=r"\.restart"))
    async def restart_command(event):
        try:
            message = await event.reply(LANG["restart_message"])
            print(LANG["restart_message_terminal"])
            
            kill_existing_processes()  # Убиваем старый процесс перед запуском нового
            
            await asyncio.sleep(2)  # Небольшая пауза перед рестартом
            
            # Для Windows (если запускается в командной строке)
            if os.name == "nt":
                subprocess.call(["exit"])  # Закрываем текущий терминал
                os.execv(sys.executable, ['python', 'main.py'])  # Запускаем новый процесс
            else:
                # Для Linux/Mac
                subprocess.call(["exit"])  # Закрываем текущий терминал
                os.execv(sys.executable, ['python3', 'main.py'])  # Запускаем новый процесс
            
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
