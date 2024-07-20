import requests, json, re
from bs4 import BeautifulSoup as BS
from ..classes import progress_bar

def groups_main_data_creation(connection):
    response = requests.get('https://abitlk.itmo.ru/api/v1/rating/directions', params={'degree': 'bachelor'})
    response = json.loads(response.text)

    cur = connection.cursor()
    
    for i in response['result']['items']:
        raw_title = i['direction_title']
        title = raw_title[raw_title.index('«')+1:raw_title.index('»')]
        cur.execute(f'''
            INSERT INTO groups_main_data
            VALUES (?, ?, ?, ?, ?, ?)
                    ''', (i["competitive_group_id"], title, i["budget_min"], i["target_reception"], i["invalid"], i["special_quota"]))
        
    connection.commit()
    connection.close()

def abit_data(connection):
    cur = connection.cursor()
    
    cur.execute('SELECT COUNT(*) FROM groups_main_data')
    ln = cur.fetchone()[0]
    bar = progress_bar(ln)
    
    for group_id in cur.execute('SELECT group_id FROM groups_main_data'):
        bar.next()
        yield bar.message
        
        response = requests.get(f'https://abit.itmo.ru/rating/bachelor/budget/{group_id}')
        soup = BS(response.text, 'lxml')

        # Список с имеющимися в данной КГ категориями (БВИ, ЦК, ...)
        categories_names = [x.text for x in soup.find_all('h5', class_=re.compile('RatingPage_title__'))]
        # "Суп" с отдельными div'ами категорий
        categories_block = soup.find_all('div', class_=re.compile('^RatingPage_table__[a-zA-Z]{5}$'))
        
        # Перебор категорий
        for i, category in enumerate(categories_block):
            # groups_info_data.add_empty_category(group_name, categories_names[i])
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
                abit_data = [name, info['Преимущественное право'], info['Оригиналы документов'], info['ИД'], None, None]
                if 'Вид испытания' in info: abit_data[-2] = info['Вид испытания']
                elif 'Олимпиада' in info: abit_data[-2] = info['Олимпиада']
                if 'Балл ВИ+ИД' in info: abit_data[-1] = info['Балл ВИ+ИД']
                cur.execute('''
                    INSERT INTO abits_data
                    VALUES (?, ?, ?, ?, ?, ?)
                            ''', abit_data)

                app_data = [id, name, group_id, info['Приоритет'], categories_names[i]]
                cur.execute('''
                    INSERT INTO applications
                    VALUES (?, ?, ?, ?, ?)  
                            ''', app_data)
    
def group_data_handler(groups_main_data, groups_info_data):
    
    
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