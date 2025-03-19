import json
import os
import asyncio
from telethon import TelegramClient, events
from telethon.tl.custom import Button

# Пути к файлам
CONFIG_FILE = "config.json"
LANG_FILE = "modules/language.txt"
LANG_DIR = "languages"  # Директория с языковыми файлами
MODULES_DIR = "modules"  # Директория с модулями

# Функция загрузки конфигурации
def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return {}

# Функция сохранения языка в файл
def save_language(lang_code):
    with open(LANG_FILE, "w", encoding="utf-8") as file:
        file.write(lang_code)

# Функция загрузки текущего языка
def load_language():
    if os.path.exists(LANG_FILE):
        with open(LANG_FILE, "r", encoding="utf-8") as file:
            lang = file.read().strip()
            return lang if os.path.exists(os.path.join(LANG_DIR, f"{lang}.py")) else "en"
    return "en"

# Функция загрузки переводов из файла
def load_translations(lang_code):
    lang_file = os.path.join(LANG_DIR, f"{lang_code}.py")
    if os.path.exists(lang_file):
        lang_module = {}
        with open(lang_file, "r", encoding="utf-8") as file:
            exec(file.read(), lang_module)
        return lang_module.get("LANG", {})
    return {}

# Функция для получения списка всех доступных модулей
def get_modules():
    modules = []
    for filename in os.listdir(MODULES_DIR):
        if filename.endswith(".py") and filename != "__init__.py":
            modules.append(filename[:-3])  # Убираем расширение .py
    return modules

async def main():
    # Загружаем конфигурацию
    config = load_config()

    # Проверяем наличие api_id, api_hash и токена
    API_ID = config.get("api_id")
    API_HASH = config.get("api_hash")
    API_TOKEN = config.get("token")

    if not API_ID or not API_HASH or not API_TOKEN:
        print("❌ Ошибка: отсутствуют api_id, api_hash или token в config.json")
        return

    # Создаем клиента бота
    bot = TelegramClient('bot', api_id=API_ID, api_hash=API_HASH)
    await bot.start(bot_token=API_TOKEN)  # Await the start to ensure proper initialization

    # Обработчик команды /start
    @bot.on(events.NewMessage(pattern='/start'))
    async def start(event):
        current_lang = load_language()
        translations = load_translations(current_lang)

        buttons = [
            [Button.inline(translations.get("settings", "Настройки ⚙️"), b'settings')],
            [Button.inline(translations.get("choose_language", "Выбрать язык 🌍"), b'choose_language')],
        ]
        
        await event.reply(translations.get("choose_language_message", "🌍 Choose a language:"), buttons=buttons)

    # Обработчик кнопок
    @bot.on(events.CallbackQuery)
    async def callback(event):
        lang_code = event.data.decode()

        if lang_code == "settings":
            current_lang = load_language()
            translations = load_translations(current_lang)

            settings_buttons = [
                [Button.inline(translations.get("all_modules", "Все модули 📦"), b'all_modules')],
                [Button.inline(translations.get("delete_module", "Удалить модуль 🗑️"), b'delete_module')],
                [Button.inline(translations.get("load_module", "Загрузить модуль ⬆️"), b'load_module')],
            ]

            await event.edit(translations.get("settings_message", "⚙️ Настройки:"), buttons=settings_buttons)
            return

        if lang_code == "choose_language":
            current_lang = load_language()
            translations = load_translations(current_lang)

            language_buttons = [
                [Button.inline(translations.get("russian", "Русский 🇷🇺"), b'ru')],
                [Button.inline(translations.get("ukrainian", "Українська 🇺🇦"), b'ua')],
                [Button.inline(translations.get("english", "English 🇬🇧"), b'en')],
            ]

            await event.edit(translations.get("choose_language_message", "Please choose a language:"), buttons=language_buttons)
            return

        if lang_code == "all_modules":
            # Получаем список всех доступных модулей
            modules = get_modules()
            current_lang = load_language()
            translations = load_translations(current_lang)

            # Создаем кнопки для каждого модуля
            module_buttons = [[Button.inline(module, module.encode())] for module in modules]
            await event.edit(translations.get("all_modules_message", "📦 Все доступные модули:"), buttons=module_buttons)
            return

        save_language(lang_code)
        translations = load_translations(lang_code)
        
        await event.edit(translations.get("language_changed", "✅ Language changed!"))

    print("✅ Бот запущен!")
    await bot.run_until_disconnected()  # Ensure the bot keeps running

# Запуск основного цикла
if __name__ == "__main__":
    asyncio.run(main()) 
