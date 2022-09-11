import logging
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
