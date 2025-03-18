import time
import os
from telethon import events

# Путь к файлу с языком
LANG_FILE = "modules/language.txt"  # Предположим, что файл теперь в папке modules

# Доступные переводы для каждого языка
LANGUAGES = {
    "en": {
        "ping_message": "Pong! The ping is not dependent on your server, but on Telegram's servers 🏓\nTime: {ping_time:.2f} ms",
    },
    "ru": {
        "ping_message": "Понг! Пинг не зависит от вашего сервера, а зависит от серверов Telegram 🏓\nВремя: {ping_time:.2f} мс",
    },
    "ua": {
        "ping_message": "Понг! Пінг не залежить від вашого сервера, а залежить від серверів Telegram 🏓\nЧас: {ping_time:.2f} мс",
    }
}

# Функция для загрузки языка из файла
def load_language():
    if os.path.exists(LANG_FILE):
        with open(LANG_FILE, "r", encoding="utf-8") as file:
            lang_code = file.read().strip().lower()
            print(f"Загружен язык: {lang_code}")  # Для отладки
    else:
        lang_code = "en"  # По умолчанию английский

    # Возвращаем переводы для выбранного языка, если язык не найден, используем английский
    return LANGUAGES.get(lang_code, LANGUAGES["en"])

# Команды модуля
COMMANDS = [".ping"]

# Функция для регистрации модуля
async def register_module(client):
    # Загружаем текущий язык
    lang = load_language()

    @client.on(events.NewMessage(pattern=r"\.ping"))
    async def ping(event):
        """Команда .ping для проверки времени отклика"""
        start_time = time.time()  # Записываем время начала
        # Отправляем сообщение, чтобы получить пинг
        message = await event.reply("Pinging...")
        
        end_time = time.time()  # Записываем время окончания
        # Вычисляем время отклика
        ping_time = (end_time - start_time) * 1000  # Время в миллисекундах
        
        # Обновляем сообщение с результатом, вместо отправки нового
        await message.edit(lang["ping_message"].format(ping_time=ping_time))

