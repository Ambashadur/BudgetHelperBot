import sqlite3
import json
from datetime import datetime

budget_entity_types = [
    'income',
    'expense'
]

connection_string: str = None


def ensure_db_created() -> None:
    global connection_string

    with open('appSettings.json') as file:
        connection_string = json.load(file)['db_connection']

    connection = sqlite3.connect(connection_string)

    create_budget_entities_types_table_sql = '''
            create table if not exists budget_entity_type
            (id integer primary key autoincrement not null,
            type text not null);
        '''

    create_budget_table_sql = '''
        create table if not exists budget
        (id integer primary key autoincrement not null,
        chat_id integer not null,
        source text not null,
        amount real not null,
        creation_datetime text not null,
        type_id integer not null,
        foreign key (type_id) references budget_entity_type (id));
    '''

    connection.execute(create_budget_entities_types_table_sql)
    connection.execute(create_budget_table_sql)
    connection.commit()

    cursor = connection.execute('select type from budget_entity_type;')
    # Установка того как получать элементы при вызове fetchall, то есть выбирается первый элемент из полученного tuple
    cursor.row_factory = lambda cur, row: row[0]
    exist_types = cursor.fetchall()

    for budget_type in budget_entity_types:
        if budget_type not in exist_types:
            connection.execute(f'insert into budget_entity_type (type) values ({budget_type})')

    connection.commit()
    connection.close()


def insert_budget_entity(
        chat_id: int,
        source: str,
        amount: float,
        creation_datetime: datetime,
        entity_type: str
) -> None:
    connection = sqlite3.connect(connection_string)

    insert_sql = f'''
            insert into budget (chat_id, source, amount, creation_datetime, type_id)
            select {chat_id}, '{source}', {amount}, '{str(creation_datetime)}', id
            from budget_entity_type
            where type = '{entity_type}';
        '''

    connection.execute(insert_sql)
    connection.commit()
    connection.close()
