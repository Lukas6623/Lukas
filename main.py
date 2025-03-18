import asyncio
import importlib
import os
import sys
import subprocess
import json
from telethon import TelegramClient, events

# Путь к файлу конфигурации
CONFIG_FILE = "config.json"

USER_DATA_FILE = "user_data.txt"  # Путь к файлу с данными пользователей
module_folder = "modules"  # Папка с модулями
LANG_FILE = "modules/language.txt"  # Теперь файл находится в папке modules

def install_libraries(module_name):
    """
    Устанавливает библиотеку, если она отсутствует, без вывода в терминал.
    """
    try:
        importlib.import_module(module_name)
    except ImportError:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", module_name], 
            stdout=subprocess.DEVNULL,  # Скрываем вывод
            stderr=subprocess.DEVNULL,  # Скрываем ошибки
            check=True
        )

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

def save_config(api_id, api_hash):
    """ Сохраняет конфигурацию в файл. """
    config = {
        "api_id": api_id,
        "api_hash": api_hash
    }
    with open(CONFIG_FILE, "w", encoding="utf-8") as file:
        json.dump(config, file)

# Загружаем язык
LANG = load_language()

# Функция для загрузки и регистрации модулей
async def load_modules(userbot):
    """
    Динамически загружает и инициализирует все модули из папки 'modules'.
    Также проверяет и устанавливает необходимые библиотеки.
    """
    modules_info = {}
    for filename in os.listdir(module_folder):
        if filename.endswith(".py") and filename != "__init__.py":
            try:
                module_name = filename[:-3]  # Убираем расширение .py

                # Проверяем зависимости
                module = importlib.import_module(f"modules.{module_name}")

                # Сохраняем информацию о командах модуля
                commands = getattr(module, 'COMMANDS', [])

                # Регистрируем модуль, если есть функция register_module
                if hasattr(module, 'register_module'):
                    register_function = getattr(module, 'register_module')
                    # Проверяем, является ли функция асинхронной
                    if asyncio.iscoroutinefunction(register_function):
                        await register_function(userbot)
                        print(LANG["module_loaded"].format(name=module_name))
                    else:
                        register_function(userbot)  # Если не асинхронная, вызываем без await
                        print(LANG["module_loaded"].format(name=module_name))
                else:
                    print(LANG["missing_register"].format(name=module_name))
                
                modules_info[module_name] = commands  # Сохраняем команды модуля
            except Exception as e:
                print(LANG["module_error"].format(name=filename, error=e))
    
    return modules_info


# Основной код для юзер-бота
async def user_bot():
    # Загружаем конфигурацию
    config = load_config()
    
    if config:
        API_ID = config["api_id"]
        API_HASH = config["api_hash"]
    else:
        print(LANG["enter_api_id"])
        API_ID = input()
        print(LANG["enter_api_hash"])
        API_HASH = input()
        
        # Сохраняем введенные данные для последующего использования
        save_config(API_ID, API_HASH)
    
    userbot = TelegramClient("userbot", API_ID, API_HASH)
    await userbot.start()

    # Загружаем все модули и получаем информацию о командах
    modules_info = await load_modules(userbot)

    # Добавляем обработчик для команды .restart
    @userbot.on(events.NewMessage(pattern=r"\.restart"))
    async def restart_command(event):
        message = await event.reply(LANG["restart_message"])
        print(LANG["restart_message_terminal"])

        # Перезапуск бота
        python = sys.executable
        os.execl(python, python, *sys.argv)  # Завершаем текущий процесс и запускаем новый

        # После перезапуска обновляем сообщение
        await asyncio.sleep(2)  # Даем время на перезапуск
        await message.edit(LANG["restart_completed"])

    # Запуск второго бота (bot.py)
    subprocess.Popen([sys.executable, 'bot.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    
    # Ждем, пока не будет получено новое сообщение
    await asyncio.Event().wait()

# Запуск юзер-бота
if __name__ == "__main__":
    asyncio.run(user_bot())
