import telebot
import os  
from telebot.types import InlineKeyboardButton ,InlineKeyboardMarkup
import logging

logger = telebot.logger

logger.setLevel(logging.INFO)

API_TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['help','start'])
def sendwelcome(message):
    logger.info("triggred welcom")
    markup = InlineKeyboardMarkup()
    codyad=InlineKeyboardButton("codyad",url="https://codyad.com")
    google=InlineKeyboardButton("google",url="https://google.com")
    test=InlineKeyboardButton("test",callback_data="test")
    
    markup.add(google,codyad)
    markup.add(test)
    bot.send_message(message.chat.id,"choose your answer:",reply_markup=markup)

@bot.callback_query_handler(func=lambda call:True)
def send_messages(call):
    if call.data=="test":
        bot.answer_callback_query(call.id,"callback testing",show_alert=True)


bot.infinity_polling()
