import json
import logging
import re
import requests
from requests import Response
from time import sleep

url = 'https://api.telegram.org/bot'

commands: dict = dict()
commands_descriptions: list = list()


def load_token() -> None:
    with open('appSettings.json') as file:
        global url
        bot_token = json.load(file)['bot_token']
        url += f'{bot_token}/'


def set_bot_commands() -> None:
    response: dict = requests.post(url + 'deleteMyCommands').json()

    if not response['ok']:
        logging.error(f'While deleting bot commands response: {response}')

    response = requests.request('post', url + 'setMyCommands?commands=' + json.dumps(commands_descriptions)).json()

    if not response['ok']:
        logging.error(f'While setting bot commands response: {response}')


def send_message(chat_id: int, message: str) -> dict:
    data = {
        'chat_id': chat_id,
        'text': message
    }

    response: Response = requests.post(url + 'sendMessage', data=data)
    return response.json()


def get_update() -> dict:
    response: Response = requests.get(url + 'getUpdates')
    content: dict = response.json()

    if content['ok']:
        return content['result'][-1]

    return dict()


def processing_get_updates() -> None:
    last_update_id: int = None

    while True:
        response: dict = get_update()

        if len(response) > 0 and response['update_id'] != last_update_id:
            last_update_id = response['update_id']

            response_text: str = response['message']['text']
            search_result = re.search('\/[a-zA-z]*', response_text)

            if search_result is not None and search_result.group() in commands.keys():
                command = search_result.group()
                commands[command](response)

        sleep(1)


def command_handler(command, description):
    def decorator(func):
        commands[command] = func
        commands_descriptions.append({
            'command': command,
            'description': description
        })

    return decorator