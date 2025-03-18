# modules/help.py

from telethon import events
import os
import importlib

# Переменная, определяющая, что данный модуль предоставляет описание
HELPMODULES = "Модуль работает как мама."

async def register_module(userbot):
    """
    Функция для регистрации модуля 'Help', который будет отвечать на команду '.help <module>'.
    """
    @userbot.on(events.NewMessage(pattern=r"\.help (\S+)"))
    async def help_command(event):
        # Получаем название модуля из команды
        module_name = event.pattern_match.group(1)
        
        # Попробуем найти модуль, игнорируя регистр
        try:
            # Загружаем модуль, проверяя его с правильным регистром
            module = importlib.import_module(f"modules.{module_name.lower()}")

            # Проверяем, есть ли в модуле переменная HELPMODULES
            if hasattr(module, "HELPMODULES"):
                help_message = f"Описание модуля '{module_name}': {module.HELPMODULES}"
            else:
                help_message = f"Модуль '{module_name}' не содержит описания."
        except ModuleNotFoundError:
            help_message = f"Модуль '{module_name}' не найден."

        # Отправляем сообщение с описанием модуля
        await event.reply(help_message)
