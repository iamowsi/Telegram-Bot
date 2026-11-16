import os
import re
import shutil
import tempfile
import logging
import telebot
import yt_dlp
from telebot import types
logger = telebot.logger

logger.setLevel(logging.INFO)

API_TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

MAX_SIZE = 50 * 1024 * 1024  # Telegram Bot API upload limit (50 MB)
YT_RE = re.compile(r"(https?://)?(www\.|m\.)?(youtube\.com|youtu\.be)/\S+")

# (chat_id, message_id) -> url
pending = {}


@bot.message_handler(commands=["start", "help"])
def start(message):
    bot.reply_to(
        message,
        "👋 Send me a YouTube link and choose a quality.\n"
        "I can send video (up to 50 MB) or MP3 audio.",
    )


@bot.message_handler(func=lambda m: m.text and YT_RE.search(m.text))
def got_link(message):
    url = YT_RE.search(message.text).group(0)
    if not url.startswith("http"):
        url = "https://" + url

    key = (message.chat.id, message.message_id)
    pending[key] = url
    mid = message.message_id

    kb = types.InlineKeyboardMarkup(row_width=3)
    kb.add(
        types.InlineKeyboardButton("360p", callback_data=f"v360:{mid}"),
        types.InlineKeyboardButton("480p", callback_data=f"v480:{mid}"),
        types.InlineKeyboardButton("720p", callback_data=f"v720:{mid}"),
    )
    kb.add(types.InlineKeyboardButton("🎵 MP3 audio", callback_data=f"a:{mid}"))
    bot.reply_to(message, "Choose a format:", reply_markup=kb)


@bot.callback_query_handler(func=lambda c: True)
def download(call):
    choice, mid = call.data.split(":")
    chat_id = call.message.chat.id
    url = pending.pop((chat_id, int(mid)), None)
    if not url:
        bot.answer_callback_query(call.id, "Request expired, send the link again.")
        return

    bot.answer_callback_query(call.id)
    bot.edit_message_text("⏳ Downloading...", chat_id, call.message.message_id)

    tmp = tempfile.mkdtemp()
    opts = {
        "outtmpl": os.path.join(tmp, "%(title).60s.%(ext)s"),
        "noplaylist": True,
        "quiet": True,
        "max_filesize": MAX_SIZE,
    }

    if choice == "a":
        opts.update(
            format="bestaudio/best",
            postprocessors=[
                {
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "128",
                }
            ],
        )
    else:
        h = choice[1:]
        opts.update(
            format=f"bv*[height<={h}][ext=mp4]+ba[ext=m4a]/b[height<={h}][ext=mp4]/b[height<={h}]",
            merge_output_format="mp4",
        )

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
        title = info.get("title", "")

        files = os.listdir(tmp)
        if not files:
            bot.edit_message_text(
                "❌ File is larger than 50 MB. Try a lower quality or audio.",
                chat_id,
                call.message.message_id,
            )
            return

        path = os.path.join(tmp, files[0])
        if os.path.getsize(path) > MAX_SIZE:
            bot.edit_message_text(
                "❌ File is larger than 50 MB. Try a lower quality or audio.",
                chat_id,
                call.message.message_id,
            )
            return

        bot.edit_message_text("📤 Uploading...", chat_id, call.message.message_id)
        with open(path, "rb") as f:
            if choice == "a":
                bot.send_audio(chat_id, f, title=title, timeout=300)
            else:
                bot.send_video(
                    chat_id, f, caption=title, supports_streaming=True, timeout=300
                )
        bot.delete_message(chat_id, call.message.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Error: {str(e)[:200]}", chat_id, call.message.message_id)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


print("Bot running...")
bot.infinity_polling()
