import os
import logging
import telebot
from telebot.types import InlineKeyboardButton,InlineKeyboardMarkup
logger = telebot.logger
logger.setLevel(logging.INFO)

API_TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    markup = InlineKeyboardMarkup()
    cantact_us = InlineKeyboardButton("ارتباط مستقیم با ما",callback_data="cantact_us")
    problem = InlineKeyboardButton("ثبت مشکل",callback_data="problem")
    markup.add(cantact_us)
    markup.add(problem)
    bot.send_message(message.chat.id, "برای دریافت اطلاعات تماس، روی دکمه زیر کلیک کنید:",reply_markup=markup)

@bot.callback_query_handler(func=lambda call:True)
def reply_call(call):
    if call.data=="cantact_us":
        bot.send_contact(chat_id=call.message.chat.id,
                         phone_number="+989397579687",
                         first_name="شرکت",
                         last_name="شما"
                         )
        bot.send_contact(chat_id=call.message.chat.id,
                         phone_number="+989158567953",
                         first_name="شرکت",
                         last_name="شما"
                         )

    if call.data=="problem":
        bot.send_message(call.message.chat.id,"لطفا مشکل خود را وارد نمایید:")
        bot.register_next_step_handler(call.message, receive_problem)
def receive_problem(message):
    if message.text and message.text.startswith('/'):
        bot.send_message(message.chat.id, "عملیات لغو شد. با /start منو را باز کنید.")
        return

    if not message.text or not message.text.strip():
        bot.send_message(message.chat.id, "⚠️ لطفاً مشکل خود را به صورت متن وارد نمایید.")
        bot.register_next_step_handler(message, receive_problem)
        return
    # if len(receive_problem) < 5:
    #     bot.send_message(
    #         message.chat.id,
    #         "⚠️ توضیح مشکل خیلی کوتاه است. لطفاً کمی بیشتر توضیح دهید."
    #     )
    #     bot.register_next_step_handler(message, receive_problem)
    #     return
    # normalized = receive_problem.replace(" ", "").replace("-", "").replace(".", "")
    # if normalized.isdigit():
    #     bot.send_message(
    #         message.chat.id,
    #         "⚠️ لطفاً مشکل خود را به صورت *متنی* توضیح دهید، نه فقط عدد.\n"
    #         "مثال: «برنامه هنگام ورود باز نمی‌شود»",
    #         parse_mode="Markdown"
    #     )
        # bot.register_next_step_handler(message, receive_problem)
        # return
    bot.send_message(
        message.chat.id,
        f"✅ مشکل شما با موفقیت ثبت شد.\n\n"
        f"کارشناسان ما در اسرع وقت با شما تماس خواهند گرفت.\n"
        ,
        logger.info(message.chat.__dict__)
    )      
bot.infinity_polling()