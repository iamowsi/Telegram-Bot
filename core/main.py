import telebot
import os  
from telebot.types import KeyboardButton,ReplyKeyboardMarkup
import logging

logger = telebot.logger

logger.setLevel(logging.INFO)

API_TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)

@bot.message_handler(commands=['help','start'])
def sendwelcome(message):
    logger.info("triggred welcom")
    markup = ReplyKeyboardMarkup(input_field_placeholder="choose your answer",resize_keyboard=True,one_time_keyboard=True)
    markup.add(KeyboardButton("like"),KeyboardButton("dislike"))
    bot.send_message(message.chat.id,"hi mustafa king what should i do for u?",reply_markup=markup)


@bot.message_handler(func=lambda message :message.text == "like")
def send_like(message):
    bot.send_message(message.chat.id,"1856 people likes")
@bot.message_handler(func=lambda message :message.text == "dislike")
def send_like(message):
    bot.send_message(message.chat.id,"8564 people dislikes")
bot.infinity_polling()


