import json
import requests
from time import sleep
from requests import Response
from simple_logger import log, LogLevel
from regex_finders import *
from work_with_db import *

url: str = None
commands: list = [
    {
        'command': '/expense',
        'description': 'Add expense'
    },
    {
        'command': '/income',
        'description': 'Add income'
    }
]


def load_token() -> None:
    with open('appSettings.json') as file:
        global url
        bot_token = json.load(file)['bot_token']
        url = f'https://api.telegram.org/bot{bot_token}/'


def set_bot_commands() -> None:
    response: Response = requests.post(url + 'deleteMyCommands')
    log(LogLevel.INFORMATION, f'deleteMyCommands - Status Code: {response.status_code} Content: {response.content}')

    response = requests.request('post', url + 'setMyCommands?commands=' + json.dumps(commands))
    log(LogLevel.INFORMATION, f'setMyCommands Status Code: {response.status_code} Content: {response.content}')


def get_update() -> dict:
    response: Response = requests.get(url + 'getUpdates')
    content: dict = response.json()

    if content['ok']:
        return content['result'][-1]

    return dict()


def send_message(chat_id: int, message: str) -> dict:
    data = {
        'chat_id': chat_id,
        'text': message
    }

    response: Response = requests.post(url + 'sendMessage', data=data)
    log(LogLevel.INFORMATION, f'sendMessage Status Code: {response.status_code}')

    return response.json()


def process_user_command(chat_id: int, user_text: str) -> None:
    result = re.search('/expense|/income', user_text)

    if result is None:
        send_message(chat_id, 'Unprocessable command')
        return

    match result.group():
        case '/expense':
            source: str = find_source(user_text.replace(result.group(), ''))

            if len(source) == 0:
                send_message(chat_id, 'Incorrect source')
                log(LogLevel.INFORMATION, f'Chat id: {chat_id} Incorrect source')
                return

            amount: float = find_amount(user_text)

            if amount is None:
                send_message(chat_id, 'Incorrect amount')
                log(LogLevel.INFORMATION, f'Chat id: {chat_id} Incorrect amount')
                return

            date: datetime = find_datetime(user_text)

            log(LogLevel.INFORMATION, f'command: /expense amount: {amount} datetime: {date}')

            insert_income_entity(chat_id, source, amount, date)
            send_message(chat_id, f'Add expense Source: {source}\nAmount: {amount}\nDate: {date}')
        case '/income':
            send_message(chat_id, 'Add income')
        case _:
            return


def main() -> None:
    last_update_id: int = None

    while True:
        response: dict = get_update()

        if len(response) > 0 and response['update_id'] != last_update_id:
            last_update_id = response['update_id']
            chat_id: int = response['message']['chat']['id']
            response_text: str = response['message']['text']

            log(LogLevel.INFORMATION, f'Process for chat - ID: {chat_id}')

            process_user_command(chat_id, response_text)

        sleep(1)


if __name__ == '__main__':
    ensure_db_created()
    load_token()
    set_bot_commands()
    main()
