import json
import logging
import re
import requests
import os

url = 'https://api.telegram.org/bot'

default_command = None

callback_queries: dict = dict()

commands: dict = dict()
commands_descriptions: list = list()

update_cash: list = list()

last_update_id: int = 0


def bot_api_start() -> None:
    load_token()
    load_bot_api_backup()


def load_token() -> None:
    with open('appSettings.json', 'r') as file:
        global url
        bot_token = json.load(file)['bot_token']
        url += f'{bot_token}/'


def load_bot_api_backup() -> None:
    if os.path.exists('bot_api_backup.json'):
        with open('bot_api_backup.json', 'r') as file:
            global last_update_id
            last_update_id = json.load(file)['update_id']


def write_bot_api_backup() -> None:
    with open('bot_api_backup.json', 'w') as file:
        global last_update_id
        json.dump({'update_id': last_update_id}, file)


def set_bot_commands() -> None:
    response: dict = requests.post(url + 'deleteMyCommands').json()

    if not response['ok']:
        logging.error(f'While deleting bot commands response: {response}')

    response = requests.request('post', url + 'setMyCommands?commands=' + json.dumps(commands_descriptions)).json()

    if not response['ok']:
        logging.error(f'While setting bot commands response: {response}')


def send_message(chat_id: int, message: str, reply_markup: dict = None) -> None:
    data = {
        'chat_id': chat_id,
        'text': message,
        'reply_markup': None if reply_markup is None else json.dumps(reply_markup)
    }

    requests.post(url + 'sendMessage', data)


def send_animation(chat_id: int, path_to_animation: str) -> None:
    with open(path_to_animation, 'rb') as file:
        requests.post(url + 'sendAnimation',
                      data={'chat_id': chat_id},
                      files={'animation': file})


def send_photo(chat_id: int, path_to_photo: str) -> None:
    with open(path_to_photo, 'rb') as file:
        requests.post(url + 'sendPhoto',
                      data={'chat_id': chat_id},
                      files={'photo': file})


def send_document(chat_id: int, path_to_file: str) -> None:
    with open(path_to_file, 'rb') as file:
        requests.post(url + 'sendDocument',
                      data={'chat_id': chat_id},
                      files={'document': file})


def answer_callback_query(callback_query_id: int, text: str) -> None:
    requests.post(url + 'answerCallbackQuery', data={
        'callback_query_id': callback_query_id,
        'text': text
    })


def get_update() -> dict:
    global last_update_id
    global update_cash

    if len(update_cash) != 0:
        update = update_cash.pop(0)
        last_update_id = update['update_id'] + 1
        write_bot_api_backup()

        return update

    response: dict = requests.get(url + 'getUpdates', data={
        'offset': last_update_id,
        'timeout': 5
    }).json()

    if not response['ok'] or len(response['result']) == 0:
        return None

    update_cash = response['result']
    update = update_cash.pop(0)
    last_update_id = update['update_id'] + 1
    write_bot_api_backup()

    return update


def bot_processing() -> None:
    global last_update_id

    while True:
        response: dict = get_update()

        if response is None:
            continue

        if 'message' in response.keys() and 'text' in response['message'].keys():
            response_text: str = response['message']['text']

            search_result = re.search('\/[a-zA-z]*', response_text)

            if search_result is not None and search_result.group() in commands.keys():
                command = search_result.group()
                commands[command](response)

            elif default_command is not None:
                default_command(response)

        elif 'callback_query' in response.keys():
            data: str = response['callback_query']['data']

            if data in callback_queries.keys():
                callback_queries[data](response)


def command_handler(command: str, description: str):
    def decorator(func):
        commands[command] = func
        commands_descriptions.append({
            'command': command,
            'description': description
        })

    return decorator


def callback_query_handler(callback_data: str):
    def decorator(func):
        callback_queries[callback_data] = func

    return decorator


def default_command_handler(func):
    global default_command
    default_command = func
