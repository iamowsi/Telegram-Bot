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
    test=InlineKeyboardButton("step1",callback_data="step1")
    
    markup.add(google,codyad)
    markup.add(test)
    bot.send_message(message.chat.id,"choose your answer:",reply_markup=markup)

@bot.callback_query_handler(func=lambda call:True)
def send_messages(call):
    if call.data=="step1":
        markup = InlineKeyboardMarkup()
        step2 = InlineKeyboardButton("step2",callback_data="step2")
        cancel = InlineKeyboardButton("cancel" , callback_data="cancel")
        markup.add(step2,cancel)
        bot.edit_message_text(chat_id=call.message.chat.id , message_id=call.message.id,text="choose your next?",reply_markup=markup)
    if call.data == "step2":
        bot.edit_message_text(chat_id=call.message.chat.id , message_id=call.message.id,text="your ref is = 1465165")
    if call.data == "cancel":
        bot.answer_callback_query(call.id,show_alert=True ,text="has been canceled",)
        bot.delete_message(chat_id=call.message.chat.id,message_id=call.message.id,timeout=5)


        # bot.answer_callback_query(call.id,"callback testing",show_alert=True)


bot.infinity_polling()
