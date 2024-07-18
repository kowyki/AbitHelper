from telebot import TeleBot
from telebot.types import Message

from ..utils.data_handlers import *
from ..utils.main_data import *

global groups_main_data, groups_data, abits_data, main_list, summary_data, last_time

def commands_handler(message: Message, bot: TeleBot):
    if 'last_time' not in globals():
        msg = bot.send_message(message.from_user.id, 'Парсинг данных с сайта...')
        reload_data(message, bot, msg.message_id)
        bot.send_message(message.from_user.id, 'Парсинг завершён', reply_markup=main_markup)

    else:
        bot.send_message(message.from_user.id, f'Последнее обновление данных:\n```\n{data["last_time"]}```', parse_mode='MarkdownV2', reply_markup=main_markup)

def buttons_handler(message: Message, bot: TeleBot):
    match message.text:
        case '📊 Информация':
            if message.from_user.id not in scores:
                bot.register_next_step_handler(message, score_add, bot, data['groups_main_data'], data['summary_data'])
                bot.send_message(message.from_user.id, 'Введите ваш балл (ЕГЭ+ИД)')
                return
            
            table = info_output(data['groups_main_data'], data['summary_data'], scores[message.from_user.id])
            bot.send_message(message.from_user.id, f'```\n{table}```', parse_mode='MarkdownV2')
                
        case '📑 Списки':
            groups = {str(i): group_name for i, group_name in enumerate(data['groups_main_data'], start=1)}
            groups_message = '\n'.join([f'{i}. {group_name}' for i, group_name in groups.items()])
            
            bot.send_message(message.from_user.id, groups_message)
            
            bot.register_next_step_handler(message, lists_handler, bot, groups, data['main_list'])
            
            bot.send_message(message.from_user.id, 'Выберите номер конкурсной группы', reply_markup=groups_markup)
        
        case '🔄 Обновить данные':
            msg = bot.send_message(message.from_user.id, 'Парсинг данных с сайта...')
            reload_data(message, bot, msg.message_id)
            bot.send_message(message.from_user.id, 'Парсинг завершён', reply_markup=main_markup)

            
        case '🗓 Последнее обновление':
            bot.send_message(message.from_user.id, f'Последнее обновление данных:\n```\n{data["last_time"]}```', parse_mode='MarkdownV2', reply_markup=main_markup)
