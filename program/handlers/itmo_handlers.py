import requests, json, re, sqlite3
from bs4 import BeautifulSoup as BS

from ..classes import *


    
    
    

# Обработчик класса groups
def groups_handler(groups_list_data):
    response = requests.get('https://abitlk.itmo.ru/api/v1/rating/directions', params={'degree': 'bachelor'})
    response = json.loads(response.text)
    
    for i in response['result']['items']:
        raw_title = i['direction_title']
        title = raw_title[raw_title.index('«')+1:raw_title.index('»')]
        groups_list_data.add_group(title, i['competitive_group_id'], i['budget_min'], i['target_reception'], i['invalid'], i['special_quota'])

# Обработчик информации направлений-абитуриентов
def group_data_handler(groups_main_data, groups_info_data):
    bar = progress_bar(len(groups_main_data))
    
    for group_name, group_value in groups_main_data.items():
        bar.next()
        yield bar.message
        
        group_id = group_value['ID']
        response = requests.get(f'https://abit.itmo.ru/rating/bachelor/budget/{group_id}')
        soup = BS(response.text, 'lxml')
        # Список с имеющимися в данной КГ категориями (БВИ, ЦК, ...)
        categories_names = [x.text for x in soup.find_all('h5', class_=re.compile('RatingPage_title__'))]
        # "Суп" с отдельными div'ами категорий
        categories_block = soup.find_all('div', class_=re.compile('^RatingPage_table__[a-zA-Z]{5}$'))
        
        # Перебор категорий
        for i, category in enumerate(categories_block):
            groups_info_data.add_empty_category(group_name, categories_names[i])
            # Перебор информации об абитуриентах
            for abit_block in category.children:
                # Номер СНИЛСа или дела
                name = abit_block.find('p', class_=re.compile('RatingPage_table__position__')).find('span').text
                # Вся инфа о абитуриенте
                all_info = abit_block.find_all('div', class_=re.compile('RatingPage_table__info__'))
                info = {}
                # Парсинг информации
                for divs in all_info:
                    for child in divs.children:
                        for item in child.children:
                            txt = item.text
                            try: info[txt[:txt.index(':')]] = int(item.find_all('span')[-1].text)
                            except: info[txt[:txt.index(':')]] = item.find_all('span')[-1].text
                # Добавление абитуриента с инфой в его категорию
                groups_info_data.add_group_data(group_name, categories_names[i], name, info)

# Обработчик информации об абитуриентах
def abits_data_handler(abits_info_data):
    abits_data = abits_info_data.abits_data
    groups_data = abits_info_data.groups_data
    # Перебор конкурсных групп
    for c_group_name, c_group in groups_data.items():
        # Перебор категорий внутри КГ
        for category_name, category in c_group.items():
            # Перебор абитуриентов внутри категории
            for abit_id, abit in category.items():
                if abit_id not in abits_data:
                    abits_info_data.create_abit(abit_id, abit)
                abits_info_data.add_abit_main_info(abit_id, abit, c_group_name, category_name)
                abits_info_data.add_abit_side_info(abit_id, abit, c_group_name)

# Создание списков
def list_handler(abit_list_data):
    while abit_list_data.old_q != abit_list_data.q:
        abit_list_data.queue_proccessing()
        abit_list_data.creating_queue()

    abit_list_data.deleting_abits()
    abit_list_data.final_clearing()

# Обработка сводки
def summary_handler(summary_main, main_list):
    for group_name, group in main_list.items():
        wet = 0
        for abit in group['ОК']:
            if abit['Балл'] == 'БВИ': wet += 1
            
        summary_main.add_data(wet, group_name, group)
