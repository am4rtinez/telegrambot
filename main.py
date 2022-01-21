import config
import telebot

API_KEY = config.API_KEY
bot = telebot.TeleBot(API_KEY)


@bot.message_handler(commands=['hello'])
def hello(message):
    bot.send_message(message.chat.id, "Hello!")


bot.polling()
