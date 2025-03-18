import subprocess
import sys
import logging
from telethon import events
from deep_translator import GoogleTranslator

# Logger setup
logger = logging.getLogger(__name__)

# List of required libraries
REQUIRED_LIBS = ["deep-translator"]
for lib in REQUIRED_LIBS:
    try:
        __import__(lib.replace("-", "_"))
    except ImportError:
        print(f"📌 Installing module {lib}...")
        subprocess.run([sys.executable, "-m", "pip", "install", lib], check=True)

HELPMODULES = ("Модуль работает как переводчик.")
SUPPORTED_LANGUAGES = {
    "en": "English", "ru": "Russian", "fr": "French", "de": "German",
    "es": "Spanish", "it": "Italian", "uk": "Ukrainian", "zh": "Chinese",
    "ja": "Japanese", "ko": "Korean", "ar": "Arabic", "tr": "Turkish",
    "pl": "Polish", "pt": "Portuguese", "hi": "Hindi", "id": "Indonesian",
    "sv": "Swedish", "no": "Norwegian", "fi": "Finnish", "nl": "Dutch",
    "da": "Danish", "ro": "Romanian", "cs": "Czech", "sk": "Slovak", "th": "Thai"
}

# Translate function
async def translate(event):
    args = event.text.split(" ", 2)  # Split the command into parts
    if len(args) < 2:
        await event.edit("⚠️ Usage: `.tr [source-target] [text]`\nExample: `.tr en-ru hello`")
        return

    lang_pair = args[1]  # Get the language pair (e.g., "en-ru")
    text = args[2] if len(args) > 2 else ""

    if "-" not in lang_pair or len(lang_pair.split("-")) != 2:
        await event.edit("❌ Invalid language format. Use `.tr en-ru text`")
        return

    source_lang, target_lang = lang_pair.split("-")

    if source_lang not in SUPPORTED_LANGUAGES or target_lang not in SUPPORTED_LANGUAGES:
        await event.edit("❌ Unsupported language. Use `.list` to view available languages.")
        return

    if not text:
        reply = await event.get_reply_message()
        if not reply:
            await event.edit("⚠️ Provide text for translation or reply to a message `.tr en-ru`")
            return
        text = reply.raw_text  # Get text from the reply

    try:
        translated_text = GoogleTranslator(source=source_lang, target=target_lang).translate(text)
        await event.edit(f"**Translation ({source_lang} → {target_lang}):**\n{translated_text}")
    except Exception as e:
        logger.exception("Translation error")
        await event.edit(f"❌ Translation error: {str(e)}")

# List languages function
async def list_languages(event):
    lang_list = "\n".join([f"**{code}** - {name}" for code, name in SUPPORTED_LANGUAGES.items()])
    example_text = (
        "**Examples of usage:**\n"
        "✅ `.tr en-ru hello` → (Привет)\n"
        "✅ `.tr fr-de Bonjour` → (Guten Tag)\n"
        "✅ `.tr es-it Hola` → (Ciao)\n"
        "✅ `.tr ru-en Привет` → (Hello)\n"
        "✅ `.tr en-uk` (in response to a message) → (Привет)\n"
    )

    await event.edit(f"🌍 **Available languages:**\n{lang_list}\n\n{example_text}")

# Help function for translator module
async def translator_help(event):
    help_text = (
        "📌 **Translator Module Commands:**\n"
        "✅ `.tr [source-target] [text]` - Translate text from source language to target language.\n"
        "✅ `.tr en-ru hello` - Example usage.\n"
        "✅ `.tr en-uk` (when replying to a message) - Translate the replied message.\n"
        "✅ `.list` - Show supported languages.\n"
    )
    await event.edit(help_text)


async def register_module(bot):
    # Register event handlers
    bot.add_event_handler(translate, events.NewMessage(pattern=r"\.tr\s+[a-z]{2}-[a-z]{2}(\s+.*)?"))
    bot.add_event_handler(list_languages, events.NewMessage(pattern=r"\.list"))
    bot.add_event_handler(translator_help, events.NewMessage(pattern=r"\.help translator")) 
    




   