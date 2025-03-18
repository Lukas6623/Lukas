import asyncio
from telethon import TelegramClient, events

# Путь к файлу конфигурации
CONFIG_FILE = "config.json"

def load_config():
    """ Загружает конфигурацию из файла. Если файла нет, возвращает None. """
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    return None

async def bot():
    # Загружаем конфигурацию
    config = load_config()

    if config:
        API_ID = config["api_id"]
        API_HASH = config["api_hash"]
    else:
        print("Введите ваш API ID:")
        API_ID = input()
        print("Введите ваш API HASH:")
        API_HASH = input()

    bot_client = TelegramClient("bot", API_ID, API_HASH)
    await bot_client.start()

    @bot_client.on(events.NewMessage(pattern='/start'))
    async def start(event):
        await event.reply("Привет, я обычный бот!")

    # Добавим другие команды
    @bot_client.on(events.NewMessage(pattern='/help'))
    async def help(event):
        await event.reply("Вот помощь! Здесь будут все команды.")

    # Ожидание команд
    await bot_client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(bot())
