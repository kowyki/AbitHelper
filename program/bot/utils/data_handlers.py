import datetime, pytz
from telebot.types import Message
from telebot import TeleBot, util
from tabulate import tabulate

from keyboards.reply import *
from handlers.itmo_handlers import *

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

def score_add(message: Message, bot: TeleBot, groups_main_data, summary_data):
    scores[message.from_user.id] = int(message.text)
    
    table = info_output(groups_main_data, summary_data, scores[message.from_user.id])
    bot.send_message(message.from_user.id, f'```\n{table}```', parse_mode='MarkdownV2')


def info_output(groups_main_data, summary_data, score):
    table = {
        'Конкурсная группа': [],
        'Мест': [],
        'ПБ': []
    }
    for group_name in groups_main_data:
        table['Конкурсная группа'].append(group_name)
        table['Мест'].append(groups_main_data[group_name]['КЦП'])
        if summary_data[group_name]["ПБ"] == 'БВИ': summary_data[group_name]["ПБ"] = 400
        table['ПБ'].append(summary_data[group_name]["ПБ"])
        
    mid_table = sorted(zip(*table.values()), key=lambda x: x[2])
    mid_table = [list(x) for x in mid_table]
    
    for i in range(len(mid_table)-1):
        if mid_table[i][2] <= score < mid_table[i+1][2]: ind1 = i+1
        elif mid_table[i][2] <= score+5 < mid_table[i+1][2]: ind2 = i+1
    try:  mid_table.insert(ind1, ('---------------------', '------', '----'))
    except: pass
    try: mid_table.insert(ind2+1, ('---------------------', '------', '----'))
    except: pass
    for item in mid_table:
        if item[2] == 400: item[2] = 'БВИ'
    table['Конкурсная группа'], table['Мест'], table['ПБ'] = zip(*mid_table)        
            
    return tabulate(table, headers='keys', stralign="left", maxcolwidths=[21, 6, 4])                
            
def lists_handler(message: Message, bot: TeleBot, groups, main_list):
    list_message, i = [], 0
    for category_name, category in main_list[groups[message.text]].items():
        if category != []:
            list_message.append(category_name)
            for abit in category:
                i += 1
                for param_name, param in abit.items():
                    match param_name: 
                        case 'Номер':
                            list_message.append(f'  {i}. {param_name}: {param}')

                        case _:
                            list_message.append(' '*(4+len(str(i))) + f'{param_name}: {param}')

    list_message = "\n".join(list_message)
    splitted_message = util.smart_split(list_message, chars_per_string=3700)

    bot.send_message(message.from_user.id, f'Списки зачисленных в рамках конкурсной группы "{groups[message.text]}"', reply_markup=main_markup)
    for excerpt in splitted_message:
        bot.send_message(message.from_user.id, f'```\n{excerpt}```', parse_mode='MarkdownV2')
