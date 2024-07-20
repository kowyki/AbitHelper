import sqlite3 as sql
from sqlite3 import Error
from ..methods.itmo import *

def create_connection(path):
    connection = None
    try: connection = sql.connect(path)
    except Error: print(Error)
    
    return connection

def db_init(university_name):
    connection = create_connection(f'program/database/{university_name}.db')
    cur = connection.cursor()
    cur.execute('''
        CREATE TABLE categories(
            category_id INTEGER PRIMARY KEY,
            category_name TEXT
        )        
                ''')
    cur.execute('''
        CREATE TABLE groups_main_data (
            group_id INTEGER PRIMARY KEY,
            group_name TEXT NOT NULL,
            budget INTEGER,
            target_quota INTEGER,
            invalid_quota INTEGER,
            special_quota INTEGER
        )
                ''')
    cur.execute('''
        CREATE TABLE abits_data(
            abit_id TEXT PRIMARY KEY,
            priority_right INTEGER,
            diploma INTEGER,
            IA INTEGER,
            exam TEXT,
            score INTEGER
        )
                ''')
    cur.execute('''
        CREATE TABLE applications(
            id INTEGER PRIMARY KEY,
            abit_id TEXT,
            group_id INTEGER,
            priority INTEGER,
            category_id INTEGER
        )        
                ''')
    connection.commit()
    connection.close()


# university_name = 'itmo'
# connection = create_connection(f'program/database/{university_name}.db')

# db_init(university_name)
# groups_main_data_creation(connection)
