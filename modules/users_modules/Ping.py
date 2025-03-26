import time
from telethon import events
import json

# Список команд, которые поддерживает модуль
COMMANDS = [".ping"]

async def ping_handler(event):
    """ Обработчик команды .ping для получения пинга бота """
    # Загружаем конфиг и получаем user_id
    with open("config.json", "r", encoding="utf-8") as file:
        config = json.load(file)
        allowed_user_id = config.get("user_id")

    # Проверяем, совпадает ли user_id отправителя с указанным в config.json
    if event.sender_id != allowed_user_id:
        return  # Если не совпадает, игнорируем команду

    start_time = time.time()  # Засекаем время начала
    message = await event.reply("🏓 Проверка пинга...")
    end_time = time.time()  # Засекаем время окончания
    ping = round((end_time - start_time) * 1000)  # Рассчитываем пинг в миллисекундах
    await message.edit(f"🏓 Пинг: {ping} мс")

# Регистрация модуля (регистрируем обработчик команды)
async def register_module(userbot):
    userbot.add_event_handler(ping_handler, events.NewMessage(pattern=r"\.ping"))
