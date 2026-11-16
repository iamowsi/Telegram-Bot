import os
import logging
import telebot
import edge_tts
import asyncio
import threading
import time
from telebot.types import ReplyParameters

logger = telebot.logger
logger.setLevel(logging.INFO)

API_TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

PERSIAN_VOICE = "fa-IR-DilaraNeural"


def keep_typing(chat_id, action="record_voice", stop_event=None):
    """وضعیت 'در حال ضبط' را هر ۴ ثانیه تمدید می‌کند."""
    while not stop_event.is_set():
        try:
            bot.send_chat_action(chat_id, action)
        except Exception as e:
            logger.warning(f"chat_action error: {e}")
        # هر ۴ ثانیه یک‌بار تکرار (چون بعد از ۵ ثانیه منقضی می‌شود)
        stop_event.wait(4)


@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.send_message(message.chat.id, "متنت رو بفرست تا برات بخونم (با صدای فارسی)")


@bot.message_handler(func=lambda message: message.text is not None)
def text_to_speech(message):
    text = message.text
    file_name = f'voices/{message.chat.id}_{message.id}.mp3'
    os.makedirs('voices', exist_ok=True)

    # تردی که وضعیت 'در حال ضبط صدا' را نگه می‌دارد
    stop_event = threading.Event()
    typing_thread = threading.Thread(
        target=keep_typing,
        args=(message.chat.id, "record_voice", stop_event),
        daemon=True,
    )
    typing_thread.start()

    async def generate_audio():
        communicate = edge_tts.Communicate(text, PERSIAN_VOICE)
        await communicate.save(file_name)

    try:
        asyncio.run(generate_audio())

        # الان آماده ارسال است → وضعیت را به 'در حال آپلود' تغییر بده
        stop_event.set()  # ترد قبلی را متوقف کن
        typing_thread.join(timeout=1)

        stop_event_upload = threading.Event()
        upload_thread = threading.Thread(
            target=keep_typing,
            args=(message.chat.id, "upload_voice", stop_event_upload),
            daemon=True,
        )
        upload_thread.start()

        with open(file_name, "rb") as voice_file:
            bot.send_voice(
                chat_id=message.chat.id,
                voice=voice_file,
                reply_parameters=ReplyParameters(message_id=message.id),
            )

        stop_event_upload.set()
        upload_thread.join(timeout=1)

    except Exception as e:
        logger.error(f"TTS error: {e}")
        stop_event.set()
        bot.reply_to(message, "متأسفانه نتونستم صدا رو بسازم. دوباره امتحان کن.")
    finally:
        if os.path.exists(file_name):
            os.remove(file_name)


bot.infinity_polling()