import telebot
import os  
import json

API_TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
	# bot.reply_to(message, "Hiiiiiiii, چیکار میتونم برات کنم?")
    bot.send_message(message.chat.id,json.dumps(message.chat.__dict__,indent = 4,ensure_ascii = False))
bot.infinity_polling()