import json
import os
from telethon import TelegramClient, events
from telethon.tl.custom import Button

# Пути к файлам
CONFIG_FILE = "config.json"
LANG_FILE = "modules/language.txt"
LANG_DIR = "languages"  # Директория с языковыми файлами

# Функция загрузки конфигурации
def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as file:
        return json.load(file)

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

# Загружаем конфигурацию
config = load_config()
API_ID = config["api_id"]
API_HASH = config["api_hash"]
API_TOKEN = config["token"]

# Создаем клиента бота
bot = TelegramClient('bot', api_id=API_ID, api_hash=API_HASH).start(bot_token=API_TOKEN)

# Обработчик команды /start
@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    # Загружаем текущий язык
    current_lang = load_language()
    translations = load_translations(current_lang)

    # Кнопки для выбора языка и настроек
    buttons = [
        [Button.inline(translations.get("settings", "Настройки ⚙️"), b'settings')],
        [Button.inline(translations.get("choose_language", "Выбрать язык 🌍"), b'choose_language')],
    ]
    
    # Отправляем сообщение с кнопками
    await event.reply(translations.get("choose_language_message", "🌍 Choose a language:"), buttons=buttons)

# Обработчик нажатия на кнопки
@bot.on(events.CallbackQuery)
async def callback(event):
    lang_code = event.data.decode()  # Получаем код языка

    # Если нажата кнопка "Настройки"
    if lang_code == "settings":
        # Загружаем текущий язык
        current_lang = load_language()
        translations = load_translations(current_lang)

        # Кнопки для настройки модулей
        settings_buttons = [
            [Button.inline(translations.get("all_modules", "Все модули 📦"), b'all_modules')],
            [Button.inline(translations.get("delete_module", "Удалить модуль 🗑️"), b'delete_module')],
            [Button.inline(translations.get("load_module", "Загрузить модуль ⬆️"), b'load_module')],
        ]

        # Отправляем сообщение с настройками
        await event.edit(translations.get("settings_message", "⚙️ Настройки:"), buttons=settings_buttons)
        return

    # Если нажата кнопка "Выбрать язык"
    if lang_code == "choose_language":
        # Загружаем текущий язык
        current_lang = load_language()
        translations = load_translations(current_lang)

        # Кнопки для выбора языка
        language_buttons = [
            [Button.inline(translations.get("russian", "Русский 🇷🇺"), b'ru')],
            [Button.inline(translations.get("ukrainian", "Українська 🇺🇦"), b'ua')],
            [Button.inline(translations.get("english", "English 🇬🇧"), b'en')],
        ]

        # Отправляем сообщение с кнопками для выбора языка
        await event.edit(translations.get("choose_language_message", "Please choose a language:"), buttons=language_buttons)
        return

    # Если нажата кнопка выбора языка
    save_language(lang_code)  # Сохраняем язык в файл
    
    # Загружаем перевод для нового языка
    translations = load_translations(lang_code)
    
    # Отправляем сообщение с переводом
    await event.edit(translations.get("language_changed", "✅ Language changed!"))

    # Если нажата кнопка "Все модули"
    if lang_code == "all_modules":
        # Логика для вывода всех модулей с их расширением .py
        modules = [f for f in os.listdir('modules') if f.endswith('.py') and f not in ['__init__.py', 'bot.py']]
        
        # Создаем кнопки с именами файлов без расширения .py
        buttons = [[Button.inline(module.replace('.py', ''), module.encode())] for module in modules]
        await event.edit(translations.get('all_modules_list', 'Все модули:') + "\n", buttons=buttons)

# Запускаем бота
print("Бот запущен")
bot.run_until_disconnected()
