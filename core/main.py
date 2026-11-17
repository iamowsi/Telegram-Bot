import os
import io
import logging
import telebot
from PIL import Image, ImageOps
from telebot.types import Message

logger = telebot.logger
logger.setLevel(logging.INFO)

API_TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

SUPPORTED_EXT = {".jpg", ".jpeg", ".png"}
MAX_DIMENSION = 1920      
JPEG_QUALITY = 70        


def compress_image(data: bytes, ext: str):
    """
    ورودی: بایت‌های عکس و پسوند
    خروجی: (BytesIO, حجم جدید به بایت)
    """
    img = Image.open(io.BytesIO(data))
    img = ImageOps.exif_transpose(img)  

 
    if max(img.size) > MAX_DIMENSION:
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.LANCZOS)

    out = io.BytesIO()
    ext = ext.lower()

    if ext in (".jpg", ".jpeg"):
  
        if img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")
        img.save(out, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        out.name = "compressed.jpg"
    else:  
        img.save(out, format="PNG", optimize=True)
        out.name = "compressed.png"

    new_size = out.tell()
    out.seek(0)
    return out, new_size


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message: Message):
    bot.send_message(
        message.chat.id,
        "👋 سلام!\n\n"
        "عکس خود را با فرمت *jpg*، *jpeg* یا *png* بفرستید تا فشرده‌اش کنم و برگردانم.\n\n"
        "💡 *نکته:* برای بهترین نتیجه، عکس را به‌صورت «File» (بدون فشرده‌سازی تلگرام) بفرستید.",
        parse_mode="Markdown"
    )


@bot.message_handler(content_types=['photo'])
def handle_photo(message: Message):
   
    file_info = bot.get_file(message.photo[-1].file_id)
    data = bot.download_file(file_info.file_path)

    try:
        compressed, new_size = compress_image(data, ".jpg")
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در پردازش عکس: {e}")
        return

    bot.send_document(
        message.chat.id,
        compressed,
        caption=(
            f"✅ فشرده شد\n"
            f"📦 حجم اصلی: {len(data)/1024:.1f} KB\n"
            f"📦 حجم جدید: {new_size/1024:.1f} KB"
        )
    )

@bot.message_handler(content_types=['document'])
def handle_document(message: Message):
    doc = message.document
    filename = doc.file_name or ""
    ext = os.path.splitext(filename)[1].lower()

  
    if ext not in SUPPORTED_EXT:
        bot.reply_to(message, "⚠️ فقط فرمت‌های jpg، jpeg و png پذیرفته می‌شود.")
        return

    if doc.file_size and doc.file_size > 20 * 1024 * 1024:
        bot.reply_to(message, "⚠️ حجم فایل بیش از ۲۰ مگابایت است و قابل پردازش نیست.")
        return

    file_info = bot.get_file(doc.file_id)
    data = bot.download_file(file_info.file_path)

    try:
        compressed, new_size = compress_image(data, ext)
    except Exception as e:
        bot.reply_to(message, f"❌ خطا در پردازش عکس: {e}")
        return

    saving = 100 - (new_size / len(data) * 100) if data else 0
    bot.send_document(
        message.chat.id,
        compressed,
        caption=(
            f"✅ فشرده شد\n"
            f"📦 حجم اصلی: {len(data)/1024:.1f} KB\n"
            f"📦 حجم جدید: {new_size/1024:.1f} KB\n"
            f"📉 کاهش: {saving:.1f}%"
        )
    )

bot.infinity_polling()