import sqlite3, datetime, pytz
from telebot.types import Message
from telebot import TeleBot

from ...handlers.itmo_handlers import *
from .data_handlers import *

data = {
    'groups_main_data': None, 
    'groups_data': None, 
    'abits_data': None, 
    'main_list': None, 
    'summary_data': None, 
    'last_time': None
}
scores = {}

def reload_data(message: Message, bot: TeleBot, msg_id):
    groups_list_data = groups_list()
    groups_handler(groups_list_data)
    groups_main_data = groups_list_data.groups_main_data
    
    groups_info_data = groups_info(groups_main_data)
    for cur_progress in group_data_handler(groups_main_data, groups_info_data):
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg_id, text=f'Парсинг данных с сайта\n```\n{cur_progress}```', parse_mode='MarkdownV2')
    groups_data = groups_info_data.groups_data
    
    abits_data_handler(groups_info_data)
    abits_data = groups_info_data.abits_data

    abit_list_data = abit_list(groups_main_data, abits_data)
    list_handler(abit_list_data)
    main_list = abit_list_data.main_list
    
    summary_main = summary()
    summary_handler(summary_main, main_list)
    summary_data = summary_main.summary_data
            
    last_time = datetime.datetime.now().astimezone(pytz.timezone('Europe/Moscow')).strftime('%d.%m.%Y %H:%M:%S МСК')
    new_data = (groups_main_data, groups_data, abits_data, main_list, summary_data, last_time)
    
    for name, item in zip(data.keys(), new_data): data[name] = item
    # return data

def score_add(message: Message, bot: TeleBot, groups_main_data, summary_data):
    scores[message.from_user.id] = int(message.text)
    
    table = info_output(groups_main_data, summary_data, scores[message.from_user.id])
    bot.send_message(message.from_user.id, f'```\n{table}```', parse_mode='MarkdownV2')
