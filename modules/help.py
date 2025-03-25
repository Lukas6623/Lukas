from telethon import events
import os
import importlib

# Переменная, определяющая, что данный модуль предоставляет описание
HELPMODULES = "Отображает список доступных модулей и их команд."

async def register_module(userbot):
    """
    Функция для регистрации модуля 'Help', который будет отвечать на команду '.help <module>'
    или просто '.help' для отображения всех команд.
    """
    @userbot.on(events.NewMessage(pattern=r"\.help(?:\s+(\S+))?"))
    async def help_command(event):
        module_name = event.pattern_match.group(1)
        module_folder = "modules"
        modules_info = {}
        
        # Получаем список всех модулей и их команд
        for filename in os.listdir(module_folder):
            if filename.endswith(".py") and filename != "__init__.py":
                try:
                    module_name_lower = filename[:-3]
                    module = importlib.import_module(f"modules.{module_name_lower}")
                    commands = getattr(module, 'COMMANDS', [])
                    if commands:
                        modules_info[module_name_lower] = sorted(commands)
                except Exception:
                    continue
        
        if module_name:
            # Отображение информации о конкретном модуле
            module_name_lower = module_name.lower()
            if module_name_lower in modules_info:
                commands_list = '\n'.join([f'▫ {cmd}' for cmd in modules_info[module_name_lower]])
                help_message = f"**📌 Модуль:** `{module_name}`\n**📋 Команды:**\n{commands_list}"
            else:
                help_message = f"❌ Модуль `{module_name}` не найден."
        else:
            # Отображение информации о всех доступных модулях
            all_modules_info = "\n\n".join([
                f"**📌 {module.capitalize()}**\n" + '\n'.join([f'▫ {cmd}' for cmd in commands])
                for module, commands in modules_info.items()
            ])
            help_message = f"**📚 Доступные модули и их команды:**\n\n{all_modules_info}"
        
        await event.reply(help_message)
