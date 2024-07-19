import colorama as clr
from tabulate import tabulate
from .handlers.itmo_handlers import *

def start_program():
    print('Парсинг данных с сайта...')
    
    groups_list_data = groups_list()
    groups_handler(groups_list_data)
    groups_main_data = groups_list_data.groups_main_data
    
    groups_info_data = groups_info(groups_main_data)
    for message in group_data_handler(groups_main_data, groups_info_data):
        print(f'\r{message}', end='   ')
    groups_data = groups_info_data.groups_data
    
    abits_data_handler(groups_info_data)
    abits_data = groups_info_data.abits_data

    abit_list_data = abit_list(groups_main_data, abits_data)
    list_handler(abit_list_data)
    main_list = abit_list_data.main_list
    
    summary_main = summary()
    summary_handler(summary_main, main_list)
    summary_data = summary_main.summary_data
    
    print('\nПарсинг завершён')    

    while True:
        ans = input(clr.Fore.RESET + '\n1. Подробная информация\n2. Краткая информация\n3. Посмотреть списки\n4. Импорт в JSON\n5. Поиск по номеру\n* ')
        match ans:
            case '1':
                if 'score' not in locals(): score = int(input('Введите ваш балл (ЕГЭ+ИД): '))
                detailed_table = {
                    'Конкурсная группа': [],
                    'Мест': [],
                    'БВИ': [],
                    'ЦК': [],
                    'ОсК': [],
                    'ОтК': [],
                    'ОК': [],
                    'ПБ': []
                }
                for group_name in groups_main_data:
                    detailed_table['Конкурсная группа'].append(group_name)
                    detailed_table['Мест'].append(groups_main_data[group_name]['КЦП'])
                    detailed_table['БВИ'].append(summary_data[group_name]['БВИ'])
                    detailed_table['ЦК'].append(f'{summary_data[group_name]["ЦК"]}/{groups_main_data[group_name]["ЦК"]}')
                    detailed_table['ОсК'].append(f'{summary_data[group_name]["ОсК"]}/{groups_main_data[group_name]["ОсК"]}')
                    detailed_table['ОтК'].append(f'{summary_data[group_name]["ОтК"]}/{groups_main_data[group_name]["ОтК"]}')
                    detailed_table['ОК'].append(summary_data[group_name]['ОК'])
                    passing_score = summary_data[group_name]['ПБ']
                    if passing_score == 'БВИ':
                        detailed_table['ПБ'].append(f'{clr.Fore.RED}БВИ{clr.Fore.RESET}')
                    elif passing_score <= score: 
                        detailed_table['ПБ'].append(f'{clr.Fore.GREEN}{summary_data[group_name]["ПБ"]}{clr.Fore.RESET}')
                    elif passing_score <= score+5: 
                        detailed_table['ПБ'].append(f'{clr.Fore.YELLOW}{summary_data[group_name]["ПБ"]}{clr.Fore.RESET}')
                    else:
                        detailed_table['ПБ'].append(f'{clr.Fore.RED}{summary_data[group_name]["ПБ"]}{clr.Fore.RESET}')
                        
                print('\n' + tabulate(detailed_table, headers='keys', numalign="left", stralign="left"))
                
            case '2':
                if 'score' not in locals(): score = int(input('Введите ваш балл (ЕГЭ+ИД): '))
                brief_table = {
                    'Конкурсная группа': [],
                    'Мест': [],
                    'ПБ': []
                }
                for group_name in groups_main_data:
                    brief_table['Конкурсная группа'].append(group_name)
                    brief_table['Мест'].append(groups_main_data[group_name]['КЦП'])
                    passing_score = summary_data[group_name]['ПБ']
                    if passing_score == 'БВИ':
                        brief_table['ПБ'].append(f'{clr.Fore.RED}БВИ{clr.Fore.RESET}')
                    elif passing_score <= score: 
                        brief_table['ПБ'].append(f'{clr.Fore.GREEN}{summary_data[group_name]["ПБ"]}{clr.Fore.RESET}')
                    elif passing_score <= score+5: 
                        brief_table['ПБ'].append(f'{clr.Fore.YELLOW}{summary_data[group_name]["ПБ"]}{clr.Fore.RESET}')
                    else:
                        brief_table['ПБ'].append(f'{clr.Fore.RED}{summary_data[group_name]["ПБ"]}{clr.Fore.RESET}')
                        
                print('\n' + tabulate(brief_table, headers='keys', numalign="left", stralign="left"))
                
            case '3':
                answers_c_group = {str(i): group_name for i, group_name in enumerate(summary_data, start=1)}
                print()
                [print(f'{k}. {v}') for k, v in answers_c_group.items()]
                ans_c_group = input('Введите номер КГ: ')
                i = 0
                for category_name, category in main_list[answers_c_group[ans_c_group]].items():
                    if category != []:
                        match category_name:
                            case 'ЦК': print(clr.Fore.CYAN)
                            case 'ОсК': print(clr.Fore.MAGENTA)
                            case 'ОтК': print(clr.Fore.BLUE)
                            case 'ОК': print(clr.Fore.YELLOW)
                        print(f'\r{category_name}')
                        for abit in category:
                            i += 1
                            for param_name, param in abit.items():
                                match param_name: 
                                    case 'Номер':
                                        print(f'  {i}. {param_name}: {param}')
                                    case _:
                                        print(' '*(4+len(str(i))) + f'{param_name}: {param}')

            case '4':
                saves_names = {
                    1: ('Конкурсные группы', groups_list_data),
                    2: ('Направления и абитуриенты', groups_info_data),
                    3: ('Абитуриенты', groups_info_data),
                    4: ('Списки', abit_list_data),
                    5: ('Сводка', summary_main)
                }
                print()
                [print(f'{name_num}. {name[0]}') for name_num, name in saves_names.items()]
                save_num = int(input('Введите номер: '))
                # try:
                if save_num == 2:
                        saves_names[save_num][1].save('groups_data')
                elif save_num == 3:
                        saves_names[save_num][1].save('abits_data')
                else: 
                        saves_names[save_num][1].save()
                print(f'{clr.Fore.GREEN}Успешно сохранено{clr.Fore.RESET}')
                # except: print(f'{clr.Fore.RED}Произошла ошибка{clr.Fore.RESET}')
            
            case '5':
                number = input('Введите номеро вашего СНИЛСа или личного дела: ')
                if number not in abits_data: print('Неверный номер или вы не подавали документы')
                abit_data = abits_data[number]
                for group_name, group in groups_data.items():
                    i = 1
                    for category_name, category in group.items():
                        for abit_number, abit in category.items():
                            if abit_number == number:
                                abit_data['КГ'][group_name]['Место в списке'] = i
                            i += 1
                            
                for param_name, param in abit_data.items():
                    if param_name != 'КГ': print(f'{param_name}: {param}')
                for group_name, group in abit_data['КГ'].items():
                    print(f'  Информация в рамках конкурсной группы: {group_name}')
                    [print(f'    {param_name}: {param}') for param_name, param in group.items()]       
                            
                list_res = None
                for group_name, group in main_list.items():
                    i = 1
                    for category_name, category in group.items():
                        for abit in category:
                            if abit['Номер'] == number:
                                list_res = {'Конкурсная группа': group_name, 
                                            'Категория': category_name,
                                            'Место в списке': f'{i}/{groups_main_data[group_name]["КЦП"]}'}
                            i += 1
                if list_res is None: print('По результатам составленных списков вы не прошли')
                else: 
                    print(f'\nАбитуриент {number} прошёл конкурс')
                    [print(f'{param_name}: {param}') for param_name, param in list_res.items()]
                
            case _: return
