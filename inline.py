import sys
import os
import importlib.util
import aiogram
import json

from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor

# Загрузка конфигурации из файла config.json
def load_config():
    with open('config.json', 'r') as f:
        return json.load(f)

config = load_config()

# Токен и user_id из config.json
API_TOKEN = config.get('token')
AUTHORIZED_USER_ID = config.get('user_id')

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Путь к папке с языковыми модулями
language_file_path = os.path.join('modules', 'language.txt')

# Функция для записи выбранного языка в файл
def update_language_file(language_code):
    os.makedirs('modules', exist_ok=True)  # Создаём папку modules, если её нет
    with open(language_file_path, 'w') as file:
        file.write(language_code)

# Функция для загрузки сообщений на основе выбранного языка
def load_language(language_code):
    language_module_path = os.path.join('modules', 'languages', f'{language_code}.py')

    if not os.path.exists(language_module_path):
        print(f"Ошибка: файл для языка {language_code} не найден.")
        return None

    spec = importlib.util.spec_from_file_location(language_code, language_module_path)
    language_module = importlib.util.module_from_spec(spec)
    sys.modules[language_code] = language_module
    spec.loader.exec_module(language_module)

    return language_module.messages

# Функция для перезапуска бота
def restart_bot():
    python = sys.executable
    os.execl(python, python, *sys.argv)  # Перезапуск текущего скрипта

# Функция для получения языка
def get_language_code():
    try:
        with open(language_file_path, 'r') as f:
            return f.read().strip()
    except FileNotFoundError:
        return 'en'  # по умолчанию английский


# Обработчик inline-запросов
@dp.inline_handler()
async def inline_echo(inline_query: types.InlineQuery):
    # Проверка, что запрос пришел от авторизованного пользователя
    if inline_query.from_user.id != AUTHORIZED_USER_ID:
        return  # Если запрос не от авторизованного пользователя, ничего не показываем

    query = inline_query.query or "empty"

    # Проверка, что запрос "Lukas"
    if query.lower() != "lukas":
        return  # Если запрос не "Lukas", ничего не показываем

    # Загружаем язык по умолчанию (или из файла)
    language_code = get_language_code()
    messages = load_language(language_code)

    # Создаём кнопку с callback_data
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(messages['change_language'], callback_data="show_buttons")  # Кнопка для показа новых кнопок
    )

    results = [
        types.InlineQueryResultArticle(
            id='1',
            title=messages['greeting'],
            input_message_content=types.InputTextMessageContent(query),
            description=messages['greeting'],
            reply_markup=keyboard
        )
    ]
    await bot.answer_inline_query(inline_query.id, results)


# Обработчик нажатия на кнопку "Нажми меня"
@dp.callback_query_handler(lambda c: c.data == 'show_buttons')
async def show_buttons(callback_query: types.CallbackQuery):
    # Проверка, что запрос от авторизованного пользователя
    if callback_query.from_user.id != AUTHORIZED_USER_ID:
        return  # Если не авторизованный пользователь, игнорируем запрос

    # Загружаем язык
    language_code = get_language_code()
    messages = load_language(language_code)

    # Создаём новые inline кнопки: Настройки
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(messages['settings'], callback_data="settings")
    )

    if callback_query.inline_message_id:
        await bot.edit_message_text(
            messages['choose_language'],
            inline_message_id=callback_query.inline_message_id,
            reply_markup=keyboard  # Новые inline кнопки
        )
    else:
        await bot.edit_message_text(
            messages['choose_language'],
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            reply_markup=keyboard  # Новые inline кнопки
        )

# Обработчик нажатия на кнопку "Настройки"
@dp.callback_query_handler(lambda c: c.data == 'settings')
async def settings(callback_query: types.CallbackQuery):
    # Проверка, что запрос от авторизованного пользователя
    if callback_query.from_user.id != AUTHORIZED_USER_ID:
        return  # Если не авторизованный пользователь, игнорируем запрос

    # Загружаем язык
    language_code = get_language_code()
    messages = load_language(language_code)

    # Создаём кнопку "Сменить язык"
    keyboard = InlineKeyboardMarkup().add(
        InlineKeyboardButton(messages['change_language'], callback_data="change_language")
    )

    if callback_query.inline_message_id:
        await bot.edit_message_text(
            messages['choose_language'],
            inline_message_id=callback_query.inline_message_id,
            reply_markup=keyboard  
        )
    else:
        await bot.edit_message_text(
            messages['choose_language'],
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            reply_markup=keyboard 
        )

# Обработчик нажатия на кнопку "Сменить язык"
@dp.callback_query_handler(lambda c: c.data == 'change_language')
async def change_language(callback_query: types.CallbackQuery):
    # Проверка, что запрос от авторизованного пользователя
    if callback_query.from_user.id != AUTHORIZED_USER_ID:
        return  

    # Загружаем язык
    language_code = get_language_code()
    messages = load_language(language_code)

    # Создаём новые кнопки для выбора языка
    keyboard = InlineKeyboardMarkup(row_width=3).add(
        InlineKeyboardButton("English", callback_data="lang_english"),
        InlineKeyboardButton("Русский", callback_data="lang_russian"),
        InlineKeyboardButton("Українська", callback_data="lang_ukrainian")
    )

    if callback_query.inline_message_id:
        await bot.edit_message_text(
            messages['choose_language'],
            inline_message_id=callback_query.inline_message_id,
            reply_markup=keyboard  
        )
    else:
        await bot.edit_message_text(
            messages['choose_language'],
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id,
            reply_markup=keyboard  # Кнопки для выбора языка
        )

# Обработчик выбора языка
@dp.callback_query_handler(lambda c: c.data in ['lang_english', 'lang_russian', 'lang_ukrainian'])
async def set_language(callback_query: types.CallbackQuery):
    # Проверка, что запрос от авторизованного пользователя
    if callback_query.from_user.id != AUTHORIZED_USER_ID:
        return  # Если не авторизованный пользователь, игнорируем запрос

    language_code = ''
    if callback_query.data == 'lang_english':
        language_code = 'en'
    elif callback_query.data == 'lang_russian':
        language_code = 'ru'
    elif callback_query.data == 'lang_ukrainian':
        language_code = 'ua'

    # Обновляем файл language.txt
    update_language_file(language_code)

    # Загружаем сообщение на выбранном языке
    messages = load_language(language_code)

    # Проверка на актуальность запроса
    try:
        await bot.answer_callback_query(callback_query.id, text=messages['lang_changed'].format(language=language_code.upper()))
    except aiogram.utils.exceptions.InvalidQueryID:
        print("Ошибка: Запрос устарел или ID запроса неверен")

    # Обновляем сообщение, чтобы пользователи знали, что они должны ввести команду для применения изменений
    if callback_query.inline_message_id:
        await bot.edit_message_text(
            messages['lang_changed'].format(language=language_code.upper()),
            inline_message_id=callback_query.inline_message_id
        )
    else:
        await bot.edit_message_text(
            messages['lang_changed'].format(language=language_code.upper()),
            chat_id=callback_query.from_user.id,
            message_id=callback_query.message.message_id
        )


if __name__ == '__main__':
    executor.start_polling(dp)
