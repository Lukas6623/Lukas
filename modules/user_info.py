from telethon import events

def register_module(client):
    print("Registering module user_info...")

    if client is None:
        print("❌ Ошибка: client is None!")
        return

    @client.on(events.NewMessage(pattern=r"^\.info$"))
    async def user_info(event):
        try:
            if not event:
                print("❌ Ошибка: event is None!")
                return

            # Проверяем, доступен ли sender_id
            if not event.sender_id:
                print("❌ Ошибка: sender_id отсутствует!")
                await event.reply("⚠️ Ошибка: Не удалось получить информацию о пользователе.")
                return

            # Получаем пользователя
            user = await event.get_sender() if event.sender_id else None
            
            if user is None:
                print("❌ Ошибка: event.get_sender() вернул None!")
                await event.reply("⚠️ Ошибка: Не удалось получить информацию о пользователе.")
                return

            # Формируем сообщение
            text = "📌 *Информация о пользователе:*\n"
            text += f"👤 *Имя:* {user.first_name or 'Нет имени'}\n"
            if user.username:
                text += f"📛 *Юзернейм:* @{user.username}\n"
            text += f"🆔 *ID пользователя:* `{user.id}`"

            # Временно изменяем сообщение, чтобы показать, что идет обработка
            await event.edit("🔍 Получение информации...")

            # Обновляем сообщение с реальными данными
            await event.edit(text)

        except Exception as e:
            print(f"❌ Ошибка в user_info: {e}")
            await event.reply("⚠️ Произошла ошибка при получении информации.")

    print("✅ Модуль user_info успешно зарегистрирован!")
