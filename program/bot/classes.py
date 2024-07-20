import json

# Прогресс-бар
class progress_bar:
    def __init__(self, iter:int):
        self.counter = 0
        self.iter = iter
        self.message = '·'*self.iter + f' {self.counter}/{self.iter}'
        
    def next(self):
        self.counter += 1
        self.message = '#'*self.counter + '·'*(self.iter-self.counter) + f' {self.counter}/{self.iter}'

# Класс всех конкурсных групп
class groups_list:
    def __init__(self, groups_main_data=None):
        if groups_main_data is None: 
            groups_main_data = {}
        self.groups_main_data = groups_main_data
    
    def add_group(self, title, ID, budget_num, target_num, invalid_num, spec_num):
        new_group = {
            'ID': ID,
            'КЦП': budget_num,
            'ЦК': target_num,
            'ОсК': invalid_num,
            'ОтК': spec_num
            }
        self.groups_main_data[title] = new_group
    
    def save(self):
        save_to_json(self.groups_main_data, 'c_groups')

# Класс информации о направлениях-абитуриентах
class groups_info:
    def __init__(self, c_groups, groups_data=None, abits_data=None):
        if groups_data is None: 
            groups_data = {group_name: {} for group_name in c_groups}
        if abits_data is None: abits_data = {}
        
        self.c_groups = c_groups
        self.groups_data = groups_data
        self.abits_data = abits_data
    
    def add_empty_category(self, group_name, category_name):
        self.groups_data[group_name][category_name] = {}
    
    def add_group_data(self, group_name, category_name, name, info):
        categories = self.groups_data[group_name]
        categories[category_name][name] = info
        
    def create_abit(self, abit_id, abit):
        self.abits_data[abit_id] = {
            'ИД': abit['ИД'],
            'Ориг. документов': abit['Оригиналы документов'],
            'КГ': {}
        }

    def add_abit_main_info(self, abit_id, abit, group_name, category_name):
        self.abits_data[abit_id]['КГ'][group_name] = {
            'Категория': category_name,
            'Приоритет': abit['Приоритет']
        }

    def add_abit_side_info(self, abit_id, abit, group_name):
        if 'Олимпиада' in abit:
            self.abits_data[abit_id]['КГ'][group_name]['Олимпиада'] = abit['Олимпиада']
        if 'Вид испытания' in abit:
            self.abits_data[abit_id]['Вид испытания'] = abit['Вид испытания']
            self.abits_data[abit_id]['Преим. право'] = abit['Преимущественное право']
            if abit['Вид испытания'] != 'Без прохождения вступительных испытаний':
                self.abits_data[abit_id]['Балл ВИ+ИД'] = abit['Балл ВИ+ИД']
                
    def sort_abit_info(self):
        ...

    def save(self, extra):
        if extra == 'groups_data':
            save_to_json(self.groups_data, 'groups_data')
        elif extra == 'abits_data':
            save_to_json(self.abits_data, 'abits_data')

# Класс итоговых списков
class abit_list:
    def __init__(self, c_groups, abits_data, main_list=None):
        self.c_groups = c_groups
        if main_list is None:
            main_list = {group_name: {
            'ЦК': [],
            'ОсК': [],
            'ОтК': [],
            'ОК': []} for group_name in self.c_groups}
        self.main_list = main_list
        self.abits_data = abits_data
        # Первоначальное создание очереди и приоритетов
        self.q = list(self.abits_data.keys())
        self.old_q = None    
        self.priorities = {x: 0 for x in self.abits_data.keys()}
        
    # Преобразование названия категории
    def category_definition(self, category_name):
        match category_name:
            case 'Целевая квота': return 'ЦК'
            case 'Особая квота': return 'ОсК'
            case 'Отдельная квота': return 'ОтК'
            case _: return 'ОК'

    # Создание очереди
    def creating_queue(self):
        q, new_list = [], self.main_list.copy()
        # Перебор категорий в заполненном списке
        for group_name, group in self.main_list.items():
            for category_name, category in group.items():
                # place_count - кол-во выделенных мест в данной категории
                if category_name == 'ОК': 
                    # Из общего количества мест вычитается кол-во занятых квотных мест
                    place_count = self.c_groups[group_name]['КЦП'] - (min(len(self.main_list[group_name]['ЦК']), self.c_groups[group_name]['ЦК']) + min(len(self.main_list[group_name]['ОтК']), self.c_groups[group_name]['ОтК']) + min(len(self.main_list[group_name]['ОсК']), self.c_groups[group_name]['ОсК']))
                else: place_count = self.c_groups[group_name][category_name]
                # Проверка на переполненность категории и добавление непрошедших абитуриентов в список
                if len(category) > place_count:
                    for abit in category[place_count:]:
                        q.append(abit['Номер'])
                        new_list[group_name][category_name].remove(abit)
                        
        self.q, self.main_list = q, new_list
        
    # Обработка очереди
    def queue_proccessing(self):
        self.old_q = self.q[:]
        
        while len(self.q) > 0:
            abit_id = self.q[0]
            abit = self.abits_data[abit_id]
            
            # Обновление приоритетов
            self.priorities[abit_id] += 1
            if self.priorities[abit_id] == 5:
                self.q.remove(abit_id)
                continue
            
            # Обработка категорий абитуриентов
            for group_name, group in abit['КГ'].items():
                if group['Приоритет'] == self.priorities[abit_id]:
                    if group['Категория'] == 'Без вступительных испытаний' or abit['Вид испытания'] == 'Без прохождения вступительных испытаний': 
                        score = 400
                    else: 
                        score = abit['Балл ВИ+ИД']
                    if group['Категория'] == 'Без вступительных испытаний' or abit['Преим. право'] == 'нет': 
                        vip = 0
                    else: 
                        vip = 1
                    diploma = 1 if abit["Ориг. документов"] == 'да' else 0
                    c_definition = self.category_definition(group['Категория'])
                    # Добавление абитуриента в КГ, согласно следующему приоритеу
                    self.main_list[group_name][c_definition].append({
                        'Номер': abit_id,
                        'Балл': score,
                        'Преим. право': vip,
                        'Ориг. док.': diploma
                    })
                    # Сортировка группы по баллам и преимуществу
                    self.main_list[group_name][c_definition].sort(key=lambda x: (x['Балл'], x['Преим. право'], x['Ориг. док.']), reverse=True)
                    
            self.q.pop(0)
    
    # Удаление непрошедших абитуриентов
    def deleting_abits(self):
        final_list = self.main_list.copy()
        for group_name, group in self.main_list.items():
            for category_name, category in group.items():
                if category_name != 'ОК':
                    final_list[group_name][category_name] = category[:self.c_groups[group_name][category_name]]
                else:
                    place_count = self.c_groups[group_name]['КЦП'] - (min(len(self.main_list[group_name]['ЦК']), self.c_groups[group_name]['ЦК']) + min(len(self.main_list[group_name]['ОтК']), self.c_groups[group_name]['ОтК']) + min(len(self.main_list[group_name]['ОсК']), self.c_groups[group_name]['ОсК']))
                    final_list[group_name]['ОК'] = category[:place_count]
    
        self.main_list = final_list

    # Финальная чистка
    def final_clearing(self):
        fin_list = self.main_list.copy()
        for group_name, group in self.main_list.items():
            for category_name, category in group.items():
                if category == []: continue
                
                for i, abit in enumerate(category):
                    for param_name, param in abit.items():
                        match param_name:
                            case 'Балл':
                                if param == 400: 
                                    fin_list[group_name][category_name][i][param_name] = 'БВИ'
                            case 'Преим. право' | 'Ориг. док.':
                                if param == 1: fin_list[group_name][category_name][i][param_name] = 'есть'
                                elif param == 0: fin_list[group_name][category_name][i][param_name] = 'нет'
        self.main_list = fin_list

    def save(self):
        save_to_json(self.main_list, 'main_list')

# Класс сводки
class summary:
    def __init__(self, summary_data=None):
        if summary_data is None:
            summary_data = {}
        self.summary_data = summary_data

    def add_data(self, wet, group_name, group):
        self.summary_data[group_name] = {
            'БВИ': wet,
            'ЦК': len(group['ЦК']),
            'ОсК': len(group['ОсК']),
            'ОтК': len(group['ОтК']),
            'ОК': len(group['ОК']),
            'ПБ': group['ОК'][-1]['Балл'] if len(group['ОК']) != 0 else 'БВИ'
        }
        
    def save(self):
        save_to_json(self.summary_data, 'summary')

# Сохранение в JSON
def save_to_json(to_save:dict, title:str):
    tojson = json.dumps(to_save, indent=4, ensure_ascii=False)
    with open(f'output/json/{title}.json', 'w', encoding='utf-8') as f:
        f.write(tojson)
    