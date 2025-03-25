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
OWNER_JSON_FILE = "owner.json"  # Файл с запрещенными модулями

# Глобальная переменная для отслеживания ожидания файла модуля
waiting_for_module_file = False

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

# Функция загрузки запрещенных модулей из файла
def load_forbidden_modules():
    if os.path.exists(OWNER_JSON_FILE):
        with open(OWNER_JSON_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            return data.get("forbidden_modules", [])
    return []

# Функция для проверки, можно ли удалить модуль
def can_delete_module(module_name):
    if os.path.exists(OWNER_JSON_FILE):
        with open(OWNER_JSON_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            forbidden_modules = data.get("forbidden_modules", [])
            if module_name in forbidden_modules:
                return False  # Модуль нельзя удалить
    return True  # Модуль можно удалить

async def main():
    global waiting_for_module_file

    # Загружаем конфигурацию
    config = load_config()

    # Проверяем наличие api_id, api_hash, token и owner_id
    API_ID = config.get("api_id")
    API_HASH = config.get("api_hash")
    API_TOKEN = config.get("token")
    OWNER_ID = config.get("user_id")

    if not API_ID or not API_HASH or not API_TOKEN:
        print("❌ Ошибка: отсутствуют api_id, api_hash или token в config.json")
        return

    if not OWNER_ID:
        print("❌ Ошибка: отсутствует user_id в config.json")
        return

    # Создаем клиента бота
    bot = TelegramClient('bot', api_id=API_ID, api_hash=API_HASH)
    await bot.start(bot_token=API_TOKEN)

    # Обработчик команды /start – реагирует только на сообщения от OWNER_ID
    @bot.on(events.NewMessage(pattern='/start', from_users=OWNER_ID))
    async def start(event):
        current_lang = load_language()
        translations = load_translations(current_lang)
        buttons = [
            [Button.inline(translations.get("settings", "Настройки ⚙️"), b'settings')],
            [Button.inline(translations.get("choose_language", "Выбрать язык 🌍"), b'choose_language')],
        ]
        await event.reply(translations.get("choose_language_message", "🌍 Choose a language:"), buttons=buttons)

    # Обработчик кнопок – срабатывает только для OWNER_ID
    @bot.on(events.CallbackQuery(func=lambda e: e.sender_id == OWNER_ID))
    async def callback(event):
        global waiting_for_module_file
        lang_code = event.data.decode()

        # Подавляем кнопки "Назад" (или "back")
        if lang_code.lower() in ("back", "назад"):
            current_lang = load_language()
            translations = load_translations(current_lang)
            buttons = [
                [Button.inline(translations.get("settings", "Настройки ⚙️"), b'settings')],
                [Button.inline(translations.get("choose_language", "Выбрать язык 🌍"), b'choose_language')],
            ]
            await event.edit(translations.get("choose_language_message", "🌍 Choose a language:"), buttons=buttons)
            return

        if lang_code == "settings":
            current_lang = load_language()
            translations = load_translations(current_lang)
            settings_buttons = [
                [Button.inline(translations.get("all_modules", "Все модули 📦"), b'all_modules')],
                [Button.inline(translations.get("delete_module", "Удалить модуль 🗑️"), b'delete_module')],
                [Button.inline(translations.get("load_module", "Загрузить модуль ⬆️"), b'load_module')],
                [Button.inline(translations.get("back", "Back"), b'back')],
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
                [Button.inline(translations.get("settings", "Назад"), b'settings')],
                [Button.inline(translations.get("back", "Back"), b'back')],
            ]
            await event.edit(translations.get("choose_language_message", "Please choose a language:"), buttons=language_buttons)
            return

        if lang_code == "all_modules":
            modules = get_modules()
            current_lang = load_language()
            translations = load_translations(current_lang)
            module_buttons = [[Button.inline(module, module.encode())] for module in modules]
            module_buttons.append([Button.inline(translations.get("back", "Back"), b'settings')])  # Добавляем кнопку "Назад"
            await event.edit(translations.get("all_modules_message", "📦 Все доступные модули: Будьте внимательны, если вы удалите модуль, который не устанавливали, функции юзер бота могут не работать."), buttons=module_buttons)
            return

        if lang_code == "delete_module":
            modules = get_modules()
            forbidden_modules = load_forbidden_modules()
            modules_to_display = [module for module in modules if module not in forbidden_modules]
            current_lang = load_language()
            translations = load_translations(current_lang)
            if not modules_to_display:
                await event.edit(translations.get("no_modules_to_delete", "❌ Нет доступных модулей для удаления."), buttons=[])
            else:
                module_buttons = [[Button.inline(module, module.encode())] for module in modules_to_display]
                module_buttons.append([Button.inline(translations.get("back", "Back"), b'settings')])  # Добавляем кнопку "Назад"
                await event.edit(translations.get("select_module_to_delete", "Выберите модуль для удаления: Будьте внимательны, если вы удалите модуль, который не устанавливали, функции юзер бота могут не работать."), buttons=module_buttons)
            return

        if lang_code == "load_module":
            waiting_for_module_file = True
            current_lang = load_language()
            translations = load_translations(current_lang)
            await event.edit(translations.get("send_module_file", "Отправьте, пожалуйста, файл с модулем (Python файл с расширением .py)."))
            return

        # Если пришёл код, совпадающий с названием модуля, пытаемся его удалить
        if lang_code in get_modules():
            module_name = lang_code.strip()
            module_file = os.path.join(MODULES_DIR, f"{module_name}.py")
            print(f"Пытаемся удалить модуль: {module_file}")  # Отладочный вывод
            if can_delete_module(module_name):
                if os.path.exists(module_file):
                    try:
                        os.remove(module_file)
                        current_lang = load_language()
                        translations = load_translations(current_lang)
                        await event.edit(translations.get("module_deleted", f"✅ Модуль {module_name} удален!"))
                        print(f"Модуль {module_name} успешно удален.")
                    except Exception as e:
                        current_lang = load_language()
                        translations = load_translations(current_lang)
                        await event.edit(translations.get("module_not_found", f"❌ Ошибка при удалении модуля {module_name}: {str(e)}"))
                        print(f"Ошибка при удалении модуля {module_name}: {str(e)}")
                else:
                    current_lang = load_language()
                    translations = load_translations(current_lang)
                    await event.edit(translations.get("module_not_found", f"❌ Модуль {module_name} не найден на сервере."))
                    print(f"Модуль {module_name} не найден по пути {module_file}.")
            else:
                current_lang = load_language()
                translations = load_translations(current_lang)
                await event.edit(translations.get("module_cannot_delete", f"❌ Модуль {module_name} не может быть удален, так как он запрещен для удаления."))
            return

        # Если пришёл код языка – сохраняем выбранный язык
        save_language(lang_code)
        translations = load_translations(lang_code)
        await event.edit(translations.get("language_changed", "✅ Language changed!"))

    # Обработчик для получения файла с модулем
    @bot.on(events.NewMessage(from_users=OWNER_ID))
    async def handle_module_file(event):
        global waiting_for_module_file
        if waiting_for_module_file:
            if event.document:
                # Сохраняем файл
                file = await event.download_media(MODULES_DIR)
                filename = os.path.basename(file)
                if filename.endswith(".py"):
                    waiting_for_module_file = False
                    current_lang = load_language()
                    translations = load_translations(current_lang)
                    await event.reply(translations.get("module_uploaded", f"✅ Модуль {filename} успешно загружен!"))
                    print(f"Модуль {filename} успешно загружен!")
                else:
                    waiting_for_module_file = False
                    current_lang = load_language()
                    translations = load_translations(current_lang)
                    await event.reply(translations.get("invalid_file", "❌ Неверный файл. Отправьте файл с расширением .py"))
            else:
                current_lang = load_language()
                translations = load_translations(current_lang)
                await event.reply(translations.get("no_file_sent", "❌ Вы не отправили файл."))
                waiting_for_module_file = False

    print("✅ Бот запущен...")
    await bot.run_until_disconnected()

asyncio.run(main())
