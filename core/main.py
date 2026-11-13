import telebot
import os  
from telebot import apihelper
# import json
import logging

logger = telebot.logger

logger.setLevel(logging.INFO)

API_TOKEN = os.environ.get("API_TOKEN")
bot = telebot.TeleBot(API_TOKEN)


# @bot.message_handler(commands=['start', 'help'])
# def send_welcome(message):
# 	bot.reply_to(message, "Hiiiiiiii, چیکار میتونم برات کنم?")
#     # bot.send_message(message.chat.id,json.dumps(message.chat.__dict__,indent = 4,ensure_ascii = False))

@bot.message_handler(commands=['help','start'])
def sendwelcome(message):
    logger.info("triggred welcom")
    bot.reply_to(message,"""hi this is a test """)

@bot.message_handler(commands=['setname'])
def setup_name(message):
    bot.send_message(message.chat.id,"what is your first name?")
    bot.register_next_step_handler(message,assign_first_name)

def assign_first_name(message,*args,**kwargs):
    first_name = message.text
    bot.send_message(message.chat.id,"what is your last name?")
    bot.register_next_step_handler(message,assign_last_name,first_name)

def assign_last_name(message,first_name):
    last_name=message.text
    bot.send_message(message.chat.id,f"welcome {first_name} {last_name } to my bot")


bot.infinity_polling()


