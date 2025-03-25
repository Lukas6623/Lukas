from telethon import events
import time

# Commands that this module will handle
COMMANDS = [".user"]
HELPMODULES = "Модуль показывает информацию пользователя." 

# Function to register the module (called when the bot starts)
async def register_module(userbot):
    @userbot.on(events.NewMessage(pattern=r"\.user"))
    async def info_command(event):
        user = event.sender
        user_id = user.id
        username = user.username if user.username else "Not Set"
        first_name = user.first_name if user.first_name else "Not Set"
        last_name = user.last_name if user.last_name else "Not Set"
        ping = round((time.time() - event.date.timestamp()) * 1000, 2)  # Ping in milliseconds

        # Prepare the message with user information
        message = f"""
        🆔 **User ID**: {user_id}
        👤 **Name**: {first_name} {last_name}
        📛 **Username**: @{username}
        ⏱ **Ping**: {ping} ms
        """
        
        # Check if the message is the same as the one sent earlier, and update it
        if event.is_reply:
            # Edit the existing message if replying to a previous one
            await event.edit(message)
        else:
            # Send the message back to the user if it's not a reply
            await event.reply(message)
