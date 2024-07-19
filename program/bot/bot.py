import os
from telebot import TeleBot
from dotenv import load_dotenv
from handlers.main_message_handlers import *

# Включение бота
def init_bot():
    TOKEN = os.getenv('API_KEY')
    bot = TeleBot(TOKEN)
    return bot

load_dotenv()
bot = init_bot()

def register_handlers():
    bot.register_message_handler(commands_handler, commands=['start'], pass_bot=True)
    bot.register_message_handler(buttons_handler, content_types=['text'], pass_bot=True)

register_handlers()

if __name__ == '__main__':
    bot.infinity_polling(timeout=5)
    