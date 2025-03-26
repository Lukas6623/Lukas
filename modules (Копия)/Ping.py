import time
import os
import json
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

# Функция для загрузки конфигурации из файла config.json
def load_config():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json'), 'r', encoding='utf-8') as file:
        return json.load(file)

# Загружаем настройки из файла config.json
config = load_config()
AUTHORIZED_USER_ID = config.get('user_id')

# Команды модуля
COMMANDS = [".ping"]

# Функция для регистрации модуля
async def register_module(client):
    @client.on(events.NewMessage(pattern=r"\.ping"))
    async def ping(event):
        """Команда .ping для проверки времени отклика"""
        
        # Проверка, что запрос пришел от авторизованного пользователя
        if event.sender_id != AUTHORIZED_USER_ID:
            return  # Если запрос не от авторизованного пользователя, ничего не показываем

        # Загружаем текущий язык при каждом вызове команды
        lang = load_language()

        start_time = time.time()  # Записываем время начала
        # Отправляем первое сообщение с текстом "Pinging..."
        message = await event.reply("Pinging...")  # Отправляем сообщение

        end_time = time.time()  # Записываем время окончания
        # Вычисляем время отклика
        ping_time = (end_time - start_time) * 1000  # Время в миллисекундах
        
        # Обновляем сообщение с результатом, вместо отправки нового
        await message.edit(lang["ping_message"].format(ping_time=ping_time))  # Редактируем существующее сообщение
