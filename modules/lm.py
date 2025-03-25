import os
from telethon import events

# Загрузка языка из файла
def load_language():
    current_dir = os.path.dirname(os.path.abspath(__file__))  # Получаем текущую директорию
    lang_file_path = os.path.join(current_dir, "language.txt")

    try:
        with open(lang_file_path, "r", encoding="utf-8") as file:
            lang_code = file.read().strip().lower()
    except FileNotFoundError:
        lang_code = "en"  # Если файл не найден, используем английский по умолчанию

    # Переводы для каждого языка
    LANGUAGES = {
        "ru": {
            "reply_to_python_file": "❌ Ответьте на сообщение с Python-файлом!",
            "not_python_file": "❌ Нужно ответить на Python-файл!",
            "file_missing_variables": "❌ Файл не содержит необходимые переменные: `COMMANDS` и `HELPMODULES`.",
            "file_saved": "✅ Файл `{}` сохранён в `{}`",
            "error": "❌ Ошибка: {}"
        },
        "en": {
            "reply_to_python_file": "❌ Reply to a Python file message!",
            "not_python_file": "❌ You need to reply to a Python file!",
            "file_missing_variables": "❌ The file doesn't contain the required variables: `COMMANDS` and `HELPMODULES`.",
            "file_saved": "✅ The file `{}` has been saved to `{}`",
            "error": "❌ Error: {}"
        },
        "ua": {
            "reply_to_python_file": "❌ Відповідьте на повідомлення з Python-файлом!",
            "not_python_file": "❌ Потрібно відповісти на Python-файл!",
            "file_missing_variables": "❌ Файл не містить необхідні змінні: `COMMANDS` та `HELPMODULES`.",
            "file_saved": "✅ Файл `{}` збережено в `{}`",
            "error": "❌ Помилка: {}"
        }
    }

    # Возвращаем словарь перевода для выбранного языка
    return LANGUAGES.get(lang_code, LANGUAGES["en"])

COMMANDS = [".lm"]
HELPMODULES = "Сохраняет отправленный Python-файл в ту же папку, где находится этот модуль."

async def register_module(userbot):
    # Загрузка языка
    LANG = load_language()

    @userbot.on(events.NewMessage(pattern=r"\.lm"))
    async def save_file(event):
        # Проверка, что сообщение — это ответ на другое сообщение
        if not event.reply_to_msg_id:
            await event.reply(LANG["reply_to_python_file"])
            return

        replied_msg = await event.get_reply_message()

        # Проверка, что это действительно файл Python
        if not replied_msg.document or not replied_msg.file or not replied_msg.file.name.endswith(".py"):
            await event.reply(LANG["not_python_file"])
            return

        module_folder = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(module_folder, replied_msg.file.name)

        try:
            # Загрузка содержимого файла
            file_content = await replied_msg.download_media(bytes)
            file_text = file_content.decode("utf-8", errors="ignore")

            # Проверка наличия переменных COMMANDS и HELPMODULES
            if "COMMANDS" not in file_text or "HELPMODULES" not in file_text:
                await event.reply(LANG["file_missing_variables"])
                return

            # Сохранение файла в ту же папку
            with open(file_path, "wb") as f:
                f.write(file_content)

            # Редактирование сообщения с подтверждением
            await event.reply(LANG["file_saved"].format(replied_msg.file.name, module_folder))

        except Exception as e:
            # Если произошла ошибка
            await event.reply(LANG["error"].format(str(e)))
