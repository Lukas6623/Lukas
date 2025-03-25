import platform
import time
import os
import sys
import json
from telethon import events

# Запоминаем время запуска бота
start_time = time.time()

# Функция для загрузки конфигурации из файла
def load_config():
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'config.json'), 'r', encoding='utf-8') as file:
        return json.load(file)

# Загружаем настройки из файла config.json
config = load_config()
AUTHORIZED_USER_ID = config.get('user_id')

def format_uptime(seconds):
    """Форматирует время работы в удобочитаемый вид."""
    days = seconds // 86400
    hours = (seconds % 86400) // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{int(days)}д {int(hours)}ч {int(minutes)}м {int(seconds)}с"

def get_bot_version():
    """Получает версию бота из файла ../version.py"""
    version_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "version.py")
    version = "Неизвестно"
    
    if os.path.exists(version_file):
        try:
            version_namespace = {}
            with open(version_file, "r", encoding="utf-8") as f:
                exec(f.read(), version_namespace)
            version = version_namespace.get("VERSION", "Неизвестно")
        except Exception as e:
            print(f"❌ Ошибка при получении версии: {e}")
    
    return version

def register_module(client):
    print("Registering module user_info...")

    if client is None:
        print("❌ Ошибка: client is None!")
        return

    @client.on(events.NewMessage(pattern=r"^\.info$"))
    async def user_info(event):
        try:
            # Проверка, что запрос пришел от авторизованного пользователя
            if event.sender_id != AUTHORIZED_USER_ID:
                return  # Если запрос не от авторизованного пользователя, ничего не показываем

            if not event:
                print("❌ Ошибка: event is None!")
                return

            if not event.sender_id:
                print("❌ Ошибка: sender_id отсутствует!")
                await event.reply("⚠️ Ошибка: Не удалось получить информацию о пользователе.")
                return

            user = await event.get_sender() if event.sender_id else None
            
            if user is None:
                print("❌ Ошибка: event.get_sender() вернул None!")
                await event.reply("⚠️ Ошибка: Не удалось получить информацию о пользователе.")
                return

            # Определение операционной системы
            os_name = platform.system()
            os_details = platform.release()

            if "Android" in os_name or "linux" in os_name.lower():
                try:
                    with open("/system/bin/sh") as f:
                        os_name = "Termux" if "Android" in platform.uname().version else "Linux"
                except FileNotFoundError:
                    pass

            # Вычисляем аптайм бота
            uptime = format_uptime(time.time() - start_time)

            # Получаем версию бота
            bot_version = get_bot_version()

            # Формируем сообщение
            text = "📌 *Информация о Lukas:*\n\n"
            text += f"👤 *Имя:* {user.first_name or 'Нет имени'}\n"
            if user.username:
                text += f"📛 *Юзернейм:* @{user.username}\n"
            text += f"🆔 *ID пользователя:* `{user.id}`\n\n"
            text += f"💻 *Устройство:* {os_name} {os_details}\n"
            text += f"⏳ *Время работы:* {uptime}\n\n"
            text += f"🔹 *Версия бота:* {bot_version}"

            # Временно изменяем сообщение, чтобы показать, что идет обработка
            await event.edit("🔍 Получение информации...")

            # Обновляем сообщение с реальными данными
            await event.edit(text)

        except Exception as e:
            print(f"❌ Ошибка в user_info: {e}")
            await event.reply("⚠️ Произошла ошибка при получении информации.")

    print("✅ Модуль user_info успешно зарегистрирован!")  

COMMANDS = [".info" ".help"]