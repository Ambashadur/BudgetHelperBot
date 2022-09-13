import pandas as pd
from bot_api import *
from regex_finders import *
from db_api import *


commands_cash: dict = dict()


@command_handler(command='/income', description='Add income')
def income_command(response: dict) -> None:
    chat_id = response['message']['chat']['id']
    send_message(chat_id, 'Please enter source of income.'
                          '\nMust contains only letters, comma, dot and space')

    commands_cash[chat_id] = {
        'command': '/income',
        'function': process_source,
        'on_failed_text': 'Please enter source of income.\nMust contains only letters, comma, dot and space',
        'entity': {
            'chat_id': chat_id,
            'source': None,
            'amount': None,
            'date': None,
            'budget_entity': 'income'
        }
    }


@command_handler(command='/expense', description='Add expense')
def income_command(response: dict) -> None:
    chat_id = response['message']['chat']['id']
    send_message(chat_id, 'Please enter source of expense.'
                          '\nMust contains only letters, comma, dot and space')

    commands_cash[chat_id] = {
        'command': '/expense',
        'function': process_source,
        'on_failed_text': 'Please enter source of expense.\nMust contains only letters, comma, dot and space',
        'entity': {
            'chat_id': chat_id,
            'source': None,
            'amount': None,
            'date': None,
            'budget_entity': 'income'
        }
    }


@command_handler(command='/clear', description='Delete all records of budget')
def clear(response: dict) -> None:
    try:
        chat_id = response['message']['chat']['id']
        clear_budget_table(chat_id)

        send_animation(chat_id, 'GIFs/wink-wink-dwayne-johnson.mp4')
        send_message(chat_id, 'Clear all budget records')
        logging.info(f'Successfully delete all records in budget table for chat ID: {chat_id}')

    except Exception as ex:
        logging.error(ex)


@command_handler(command='/getbudget', description='Show all total income and expense')
def get_budget_list(response: dict):
    try:
        chat_id = response['message']['chat']['id']

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
        send_message(chat_id, f'Total income: {total_income}\n'
                              f'Total expense: {total_expense}\n'
                              f'Total budget: {total_income - total_expense}')
        logging.info(f'Successfully delete all records in budget table for chat ID: {chat_id}')

    except Exception as ex:
        logging.error(ex)


@command_handler(command='/cancel', description='Cancel executing command')
def cancel(response: dict):
    chat_id = response['message']['chat']['id']

    if chat_id in commands_cash.keys():
        commands_cash.pop(chat_id)
        send_message(chat_id, 'Command successfully canceled')


def process_source(response:  dict):
    chat_id = response['message']['chat']['id']
    source = find_source(response['message']['text'])

    if source is not None:
        commands_cash[chat_id]['entity']['source'] = source
        commands_cash[chat_id]['function'] = process_amount
        commands_cash[chat_id]['on_failed_text'] = \
            'Please enter amount.\nMust be positive float number in Rubles'
        send_message(chat_id, 'Please enter amount.\nMust be positive float number in Rubles')
    else:
        send_message(chat_id, commands_cash[chat_id]['on_failed_text'])


def process_amount(response: dict):
    chat_id = response['message']['chat']['id']
    amount = find_amount(response['message']['text'])

    if amount is not None:
        commands_cash[chat_id]['entity']['amount'] = amount
        commands_cash[chat_id]['function'] = process_date
        commands_cash[chat_id]['on_failed_text'] = \
            'Please enter date.\nIn format {dd.mm.yyyy} or {dd.mm.yyyy HH:MM} in 24 hours format'
        send_message(chat_id, 'Please enter date.\nIn format {dd.mm.yyyy} or {dd.mm.yyyy HH:MM} in 24 hours format')
    else:
        send_message(chat_id, commands_cash[chat_id]['on_failed_text'])


def process_date(response: dict):
    chat_id = response['message']['chat']['id']
    date = find_datetime(response['message']['text'])

    if date is not None:
        entity = commands_cash[chat_id]['entity']

        insert_budget_entity(chat_id, entity['source'], entity['amount'], date, entity['budget_entity'])

        send_animation(chat_id, 'GIFs/rock-agreed-rock-sus.mp4')
        send_message(chat_id, f'Add income\n'
                              f'Source: {entity["source"]}\n'
                              f'Amount: {entity["amount"]}\n'
                              f'Date: {str(date)}')

        logging.info(f'Bot command: {commands_cash[chat_id]["command"]} | Chat ID: {chat_id} | Success')
        commands_cash.pop(chat_id)
    else:
        send_message(chat_id, commands_cash[chat_id]['on_failed_text'])


@default_command_handler
def default(response: dict):
    chat_id = response['message']['chat']['id']

    if chat_id in commands_cash.keys():
        commands_cash[chat_id]['function'](response)
