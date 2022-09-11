import pandas as pd
from bot_api import *
from regex_finders import *
from db_api import *


@command_handler(command='/income', description='Add income')
def income_command(response: dict) -> None:
    user_text = response['message']['text']
    chat_id = response['message']['chat']['id']

    source: str = find_source(user_text)

    if len(source) == 0:
        send_message(chat_id, 'Incorrect source')
        logging.error(
            f'Bot command: /income | Chat ID: {chat_id} | Incorrect income source | User message: {user_text}')
        return

    amount: float = find_amount(user_text)

    if amount is None:
        send_message(chat_id, 'Incorrect amount')
        logging.error(f'Bot command: /income | Chat ID: {chat_id} | Incorrect amount | User message: {user_text}')
        return

    date: datetime = find_datetime(user_text)

    if date > datetime.now():
        send_message(chat_id, 'Incorrect date')
        logging.error(f'Bot command: /income | Chat ID: {chat_id} | Incorrect date | User message: {user_text}')
        return

    insert_budget_entity(chat_id, source, amount, date, 'income')
    send_message(chat_id, f'Add income\nSource: {source}\nAmount: {amount}\nDate: {date}')
    logging.info(f'Bot command: /income | Chat ID: {chat_id} | Success')


@command_handler(command='/expense', description='Add expense')
def income_command(response: dict) -> None:
    user_text = response['message']['text']
    chat_id = response['message']['chat']['id']

    source: str = find_source(user_text)

    if len(source) == 0:
        send_message(chat_id, 'Incorrect source')
        logging.error(
            f'Bot command: /expense | Chat ID: {chat_id} | Incorrect expense source | User message: {user_text}')
        return

    amount: float = find_amount(user_text)

    if amount is None:
        send_message(chat_id, 'Incorrect amount')
        logging.error(f'Bot command: /expense | Chat ID: {chat_id} | Incorrect amount | User message: {user_text}')
        return

    date: datetime = find_datetime(user_text)

    if date > datetime.now():
        send_message(chat_id, 'Incorrect date')
        logging.error(f'Bot command: /expense | Chat ID: {chat_id} | Incorrect date | User message: {user_text}')
        return

    insert_budget_entity(chat_id, source, amount, date, 'expense')
    send_message(chat_id, f'Add expense\nSource: {source}\nAmount: {amount}\nDate: {date}')
    logging.info(f'Bot command: /expense | Chat ID: {chat_id} | Success')


@command_handler(command='/clear', description='Delete all records of budget')
def clear(response: dict) -> None:
    try:
        chat_id = response['message']['chat']['id']
        clear_budget_table(chat_id)

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

        send_message(chat_id, f'Total income: {total_income}\n'
                              f'Total expense: {total_expense}\n'
                              f'Total budget: {total_income - total_expense}')
        logging.info(f'Successfully delete all records in budget table for chat ID: {chat_id}')

    except Exception as ex:
        logging.error(ex)
