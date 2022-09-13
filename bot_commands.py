import pandas as pd
from bot_api import *
from regex_finders import *
from db_api import *


commands_cash: dict = dict()


@command_handler(command='/income', description='Добавить новую запись о доходах')
def income_command(response: dict) -> None:
    chat_id = response['message']['chat']['id']

    if chat_id in commands_cash.keys():
        send_message(chat_id, commands_cash[chat_id]['on_failed_text'])
        return

    send_message(chat_id, 'Введите пожалуйста источник дохода.\n'
                          'Допускаются только буквы (как латиница, так и кириллица), точка, запятая и пробел.')

    commands_cash[chat_id] = {
        'command': '/income',
        'process_function': process_source,
        'on_failed_text': 'Введите пожалуйста источник дохода.\n'
                          'Допускаются только буквы (как латиница, так и кириллица), точка, запятая и пробел.',
        'entity': {
            'chat_id': chat_id,
            'source': None,
            'amount': None,
            'date': None,
            'budget_entity': 'income'
        }
    }


@command_handler(command='/expense', description='Добавить новую запись о расходах')
def income_command(response: dict) -> None:
    chat_id = response['message']['chat']['id']

    if chat_id in commands_cash.keys():
        send_message(chat_id, commands_cash[chat_id]['on_failed_text'])
        return

    send_message(chat_id, 'Введите пожалуйста на что были потрачены дегьги\n'
                          'Допускаются только буквы (как латиница, так и кириллица), точка, запятая и пробел')

    commands_cash[chat_id] = {
        'command': '/expense',
        'process_function': process_source,
        'on_failed_text': 'Введите пожалуйста на что были потрачены дегьги\n'
                          'Допускаются только буквы (как латиница, так и кириллица), точка, запятая и пробел',
        'entity': {
            'chat_id': chat_id,
            'source': None,
            'amount': None,
            'date': None,
            'budget_entity': 'income'
        }
    }


@command_handler(command='/clear', description='Удалить все записи о доходах и расходах')
def clear(response: dict) -> None:
    try:
        chat_id = response['message']['chat']['id']

        if chat_id in commands_cash.keys():
            send_message(chat_id, commands_cash[chat_id]['on_failed_text'])
            return

        clear_budget_table(chat_id)

        send_animation(chat_id, 'GIFs/wink-wink-dwayne-johnson.mp4')
        send_message(chat_id, 'Все записи были успешно удалены')
        logging.info(f'Successfully delete all records in budget table for chat ID: {chat_id}')

    except Exception as ex:
        logging.error(ex)


@command_handler(command='/getbudget', description='Получить сводку об общих доходах и расходах')
def get_budget_list(response: dict):
    try:
        chat_id = response['message']['chat']['id']

        if chat_id in commands_cash.keys():
            send_message(chat_id, commands_cash[chat_id]['on_failed_text'])
            return

        total_income: float = 0
        total_expense: float = 0

        all_incomes: list = get_all_entity(chat_id, 'income')

        if len(all_incomes) != 0:
            income_frame = pd.DataFrame(all_incomes)
            income_frame.set_index('creation_date', drop=True, inplace=True)
            total_income = income_frame['amount'].sum()

        all_expenses: list = get_all_entity(chat_id, 'expense')

        if len(all_expenses) != 0:
            expense_frame = pd.DataFrame(all_expenses)
            expense_frame.set_index('creation_date', drop=True, inplace=True)
            total_expense = expense_frame['amount'].sum()

        send_animation(chat_id, 'GIFs/rock_explaining_meme.mp4')
        send_message(chat_id, f'Общие доходы: {total_income}\n'
                              f'Общие расходы: {total_expense}\n'
                              f'Общий буджет на текущий момент: {total_income - total_expense}')
        logging.info(f'Successfully delete all records in budget table for chat ID: {chat_id}')

    except Exception as ex:
        logging.error(ex)


@command_handler(command='/cancel', description='Отменить выполнение текущей команды')
def cancel(response: dict):
    chat_id = response['message']['chat']['id']

    if chat_id in commands_cash.keys():
        commands_cash.pop(chat_id)
        send_message(chat_id, 'Команда успешно отменена')


def process_source(response:  dict):
    chat_id = response['message']['chat']['id']
    source = find_source(response['message']['text'])

    if source is not None:
        commands_cash[chat_id]['entity']['source'] = source
        commands_cash[chat_id]['process_function'] = process_amount
        commands_cash[chat_id]['on_failed_text'] = 'Введите пожалуйста сумму денег.\n' \
            'Допускаются только суммы не свыше 999999 рублей.\n' \
            'Допускаются только 2 цифры после запятой.'
        send_message(chat_id, 'Введите пожалуйста сумму денег.\n'
                              'Допускаются только суммы не свыше 999999 рублей.\n'
                              'Допускаются только 2 цифры после запятой.')
    else:
        send_message(chat_id, commands_cash[chat_id]['on_failed_text'])


def process_amount(response: dict):
    chat_id = response['message']['chat']['id']
    amount = find_amount(response['message']['text'])

    if amount is not None:
        commands_cash[chat_id]['entity']['amount'] = amount
        commands_cash[chat_id]['process_function'] = process_date
        commands_cash[chat_id]['on_failed_text'] = 'Введите пожалуйста дату.\n' \
            'Допускабтся даты в формате {dd.mm.yyyy} или {dd.mm.yyyy HH:MM} (24 часовое представление времени).\n' \
            'Дата должна быть не позднее текущей.'

        inline_keyboard = [
            [
                {
                    'text': 'Указать текущую дату',
                    'callback_data': 'current_date'
                }
            ]
        ]

        send_message(chat_id,
                     'Введите пожалуйста дату.\n'
                     'Допускабтся даты в формате {dd.mm.yyyy} или {dd.mm.yyyy HH:MM} '
                     '(24 часовое представление времени).\n'
                     'Дата должна быть не позднее текущей.'
                     'Или если хотите указать текущую дату, то можете нажть на кнопку.',
                     json.dumps({'inline_keyboard': inline_keyboard}))
    else:
        send_message(chat_id, commands_cash[chat_id]['on_failed_text'])


def process_date(response: dict):
    chat_id = response['message']['chat']['id']
    date = find_datetime(response['message']['text'])

    if date is not None and date <= datetime.now():
        entity = commands_cash[chat_id]['entity']

        insert_budget_entity(chat_id, entity['source'], entity['amount'], date, entity['budget_entity'])

        send_animation(chat_id, 'GIFs/rock-agreed-rock-sus.mp4')
        send_message(chat_id, f'Запись добавлена\n'
                              f'Источник: {entity["source"]}\n'
                              f'Сумма: {entity["amount"]}\n'
                              f'Дата: {str(date)}')

        logging.info(f'Bot command: {commands_cash[chat_id]["command"]} | Chat ID: {chat_id} | Success')
        commands_cash.pop(chat_id)
    else:
        send_message(chat_id, commands_cash[chat_id]['on_failed_text'])


@default_command_handler
def default(response: dict):
    chat_id = response['message']['chat']['id']

    if chat_id in commands_cash.keys():
        commands_cash[chat_id]['process_function'](response)
