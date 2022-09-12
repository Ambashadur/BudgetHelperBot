import json
import logging
import re
import requests
import os

url = 'https://api.telegram.org/bot'

regex_patterns: dict = dict()
commands: dict = dict()
commands_descriptions: list = list()

update_cash: list = list()
commands_cash: dict = dict()

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


def send_message(chat_id: int, message: str) -> None:
    requests.post(url + 'sendMessage', data={
        'chat_id': chat_id,
        'text': message
    })


def send_animation(chat_id: int, path_to_animation: str):
    with open(path_to_animation, 'rb') as file:
        requests.post(url + 'sendAnimation',
                      data={'chat_id': chat_id},
                      files={'animation': file})


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

        if response is not None:
            response_text: str = response['message']['text']
            chat_id: int = response['message']['chat']['id']

            search_result = re.search('\/[a-zA-z]*', response_text)

            if search_result is not None and search_result.group() in commands.keys():
                command = search_result.group()
                commands[command](response)
            elif chat_id in commands_cash.keys():
                commands_cash[chat_id]['function'](response)


def command_handler(command: str, description: str):
    def decorator(func):
        commands[command] = func
        commands_descriptions.append({
            'command': command,
            'description': description
        })

    return decorator
