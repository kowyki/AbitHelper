from telebot import types

def remove_kb():
    return types.ReplyKeyboardRemove(selective=False)

def main_kb():
    main_markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    main_markup_items = {1: types.KeyboardButton('📊 Информация'), 
                         2: types.KeyboardButton('📑 Списки'),
                         3: types.KeyboardButton('🔄 Обновить данные'),
                         4: types.KeyboardButton('🗓 Последнее обновление')}
    main_markup.add(*main_markup_items.values())
    
    return main_markup
    
def choose_group_kb():
    groups_markup = types.ReplyKeyboardMarkup(row_width=9, resize_keyboard=True)
    groups_markup.add(*[str(x) for x in range(1, 10)])
    groups_markup.add(*[str(x) for x in range(10, 19)])
    groups_markup.add(*[str(x) for x in range(19, 28)])
    
    return groups_markup

main_markup = main_kb()
groups_markup = choose_group_kb()

