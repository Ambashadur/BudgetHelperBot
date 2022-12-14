import pandas as pd
from pandas import DataFrame
from matplotlib import pyplot as plt
from bot_api import *
from regex_finders import *
from db_api import *

commands_cash: dict = dict()


@command_handler(command='/income', description='Добавить новую запись о доходах')
def income_command(response: dict) -> None:
    try:
        chat_id: int = response['message']['chat']['id']

        if chat_id in commands_cash:
            send_message(chat_id, commands_cash[chat_id]['on_failed_text'])
            return

        send_message(chat_id, 'Введите пожалуйста источник дохода.\n'
                              'Допускаются только буквы (как латиница, так и кириллица), точка, запятая и пробел.')

        commands_cash[chat_id] = {
            'command': '/income',
            'process_function': process_source,
            'on_failed_text': 'Допускаются только буквы (как латиница, так и кириллица), точка, запятая и пробел.',
            'entity': {
                'chat_id': chat_id,
                'source': None,
                'amount': None,
                'date': None,
                'budget_entity': 'income'
            }
        }

    except Exception as ex:
        logging.error(ex)


@command_handler(command='/expense', description='Добавить новую запись о расходах')
def income_command(response: dict) -> None:
    try:
        chat_id: int = response['message']['chat']['id']

        if chat_id in commands_cash:
            send_message(chat_id, commands_cash[chat_id]['on_failed_text'])
            return

        send_message(chat_id, 'Введите пожалуйста на что были потрачены деньги\n'
                              'Допускаются только буквы (как латиница, так и кириллица), точка, запятая и пробел')

        commands_cash[chat_id] = {
            'command': '/expense',
            'process_function': process_source,
            'on_failed_text': 'Допускаются только буквы (как латиница, так и кириллица), точка, запятая и пробел',
            'entity': {
                'chat_id': chat_id,
                'source': None,
                'amount': None,
                'date': None,
                'budget_entity': 'expense'
            }
        }

    except Exception as ex:
        logging.error(ex)


@command_handler(command='/clear', description='Удалить все записи о доходах и расходах')
def clear(response: dict) -> None:
    try:
        chat_id: int = response['message']['chat']['id']

        if chat_id in commands_cash:
            send_message(chat_id, commands_cash[chat_id]['on_failed_text'])
            return

        clear_budget_table(chat_id)

        send_animation(chat_id, 'GIFs/wink-wink-dwayne-johnson.mp4')
        send_message(chat_id, 'Все записи были успешно удалены')
        logging.info(f'Successfully delete all records in budget table for chat ID: {chat_id}')

    except Exception as ex:
        logging.error(ex)


@command_handler(command='/getbudget', description='Получить сводку об общих доходах и расходах')
def get_budget_list(response: dict) -> None:
    try:
        chat_id: int = response['message']['chat']['id']

        if chat_id in commands_cash:
            send_message(chat_id, commands_cash[chat_id]['on_failed_text'])
            return

        inline_keyboard: dict = {
            'inline_keyboard': [
                [
                    {
                        'text': 'Получить краткую сводку',
                        'callback_data': 'short_info'
                    }
                ],
                [
                    {
                        'text': 'Получить файл со всеми записями',
                        'callback_data': 'get_file_budget'
                    }
                ],
                [
                    {
                        'text': 'Получить график буджета',
                        'callback_data': 'get_plot_budget'
                    }
                ]
            ]
        }

        send_message(chat_id, 'В каком виде вы хотите получить свединия о вашем бюджете?', inline_keyboard)

    except Exception as ex:
        logging.error(ex)


@command_handler(command='/cancel', description='Отменить выполнение текущей команды')
def cancel(response: dict) -> None:
    try:
        chat_id: int = response['message']['chat']['id']

        if chat_id in commands_cash:
            commands_cash.pop(chat_id)
            send_message(chat_id, 'Команда успешно отменена.')
        else:
            send_message(chat_id, 'Нет команды, которую можно отменить.')

    except Exception as ex:
        logging.error(ex)


@callback_query_handler(callback_data='current_date')
def current_date(response: dict) -> None:
    try:
        chat_id: int = response['callback_query']['message']['chat']['id']

        if chat_id in commands_cash:
            date = datetime.now()
            entity = commands_cash[chat_id]['entity']

            insert_budget_entity(chat_id, entity['source'], entity['amount'], date, entity['budget_entity'])

            answer_callback_query(response['callback_query']['id'], 'Готово')

            send_animation(chat_id, 'GIFs/rock-agreed-rock-sus.mp4')
            send_message(chat_id, f'Запись добавлена\n'
                                  f'Источник: {entity["source"]}\n'
                                  f'Сумма: {entity["amount"]}\n'
                                  f'Дата: {str(date)}')

            logging.info(f'Bot command: {commands_cash[chat_id]["command"]} | Chat ID: {chat_id} | Success')
            commands_cash.pop(chat_id)

        else:
            answer_callback_query(response['callback_query']['id'], 'Ошибка')
            send_message(chat_id, 'Не достаточно данных для сохранения записи')

    except Exception as ex:
        logging.error(ex)


@callback_query_handler(callback_data='short_info')
def get_short_budget_info(response: dict) -> None:
    try:
        chat_id: int = response['callback_query']['message']['chat']['id']
        budget_frame = get_budget_frame(chat_id)

        income_sum: float = budget_frame["income_amount"].sum()
        expense_sum: float = budget_frame["expense_amount"].sum()

        answer_callback_query(response['callback_query']['id'], 'Готово')

        send_animation(chat_id, 'GIFs/rock_explaining_meme.mp4')
        send_message(chat_id, f'Общие доходы: {income_sum}\n'
                              f'Общие расходы: {expense_sum}\n'
                              f'Общий буджет на текущий момент: {income_sum - expense_sum}')
        logging.info(f'Successfully delete all records in budget table for chat ID: {chat_id}')

    except Exception as ex:
        logging.error(ex)


@callback_query_handler(callback_data='get_file_budget')
def get_file_budget(response: dict) -> None:
    try:
        chat_id: int = response['callback_query']['message']['chat']['id']

        budget_frame = get_budget_frame(chat_id)
        budget_frame.rename(columns={
            'income_amount': 'Доход',
            'expense_amount': 'Расход',
            'income_source': 'Источник дохода',
            'expense_source': 'Цель расхода'
        }, inplace=True)

        filename: str = 'Files/' + str(datetime.now()) + '.csv'
        budget_frame.to_csv(filename)

        answer_callback_query(response['callback_query']['id'], 'Готово')
        send_document(chat_id, filename)

        os.remove(filename)

    except Exception as ex:
        logging.error(ex)


@callback_query_handler(callback_data='get_plot_budget')
def get_plot_budget(response: dict) -> None:
    try:
        chat_id: int = response['callback_query']['message']['chat']['id']

        budget_frame = get_budget_frame(chat_id)
        budget_frame.drop(columns=['income_source', 'expense_source'], inplace=True)
        budget_frame.rename(columns={
            'income_amount': 'Доход',
            'expense_amount': 'Расход',
        }, inplace=True)

        plt.clf()
        plt.plot(budget_frame['Доход'], label='Доход')
        plt.plot(budget_frame['Расход'], label='Расход')
        plt.grid()
        plt.legend()
        plt.title('График расходов и доходов')
        plt.xlabel('Дата')
        plt.ylabel('Сумма, руб.')
        plt.xticks(rotation=45)

        filename: str = 'Plots/' + str(datetime.now()) + '.jpg'
        plt.savefig(filename, dpi=150, bbox_inches='tight')

        answer_callback_query(response['callback_query']['id'], 'Готово')
        send_photo(chat_id, filename)

        os.remove(filename)

    except Exception as ex:
        logging.error(ex)


@default_command_handler
def default(response: dict) -> None:
    chat_id: int = response['message']['chat']['id']

    if chat_id in commands_cash:
        commands_cash[chat_id]['process_function'](response)


def process_source(response:  dict) -> None:
    try:
        chat_id: int = response['message']['chat']['id']

        if source := find_source(response['message']['text']):
            commands_cash[chat_id]['entity']['source'] = source
            commands_cash[chat_id]['process_function'] = process_amount
            commands_cash[chat_id]['on_failed_text'] = 'Допускаются только суммы не свыше 999999 рублей.\n' \
                                                       'Допускаются только 2 цифры после запятой.'
            send_message(chat_id, 'Введите пожалуйста сумму денег.\n'
                                  'Допускаются только суммы не свыше 999999 рублей.\n'
                                  'Допускаются только 2 цифры после запятой.')
        else:
            send_message(chat_id, commands_cash[chat_id]['on_failed_text'])

    except Exception as ex:
        logging.error(ex)


def process_amount(response: dict) -> None:
    try:
        chat_id: int = response['message']['chat']['id']

        if amount := find_amount(response['message']['text']):
            commands_cash[chat_id]['entity']['amount'] = amount
            commands_cash[chat_id]['process_function'] = process_date
            commands_cash[chat_id]['on_failed_text'] = \
                'Допускаются даты в формате {dd.mm.yyyy} или {dd.mm.yyyy HH:MM}\n' \
                '(24 часовое представление времени).\n' \
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
                         'Допускаются даты в формате {дд.мм.гггг} или {дд.мм.гггг ЧЧ:ММ}\n'
                         '(24 часовое представление времени).\n'
                         'Дата должна быть не позднее текущей.',
                         {'inline_keyboard': inline_keyboard})
        else:
            send_message(chat_id, commands_cash[chat_id]['on_failed_text'])

    except Exception as ex:
        logging.error(ex)


def process_date(response: dict) -> None:
    try:
        chat_id: int = response['message']['chat']['id']

        if (date := find_datetime(response['message']['text'])) and date <= datetime.now():
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

    except Exception as ex:
        logging.error(ex)


def get_budget_frame(chat_id: int) -> DataFrame:
    all_incomes: list = get_all_entity(chat_id, 'income')

    income_frame = pd.DataFrame(columns=['source', 'amount', 'creation_date'])
    expense_frame = pd.DataFrame(columns=['source', 'amount', 'creation_date'])

    if len(all_incomes) != 0:
        income_frame = pd.DataFrame(all_incomes)

    income_frame.rename(columns={'amount': 'income_amount', 'source': 'income_source'}, inplace=True)
    income_frame.set_index('creation_date', drop=True, inplace=True)
    income_frame.index = pd.to_datetime(income_frame.index)

    all_expenses: list = get_all_entity(chat_id, 'expense')

    if len(all_expenses) != 0:
        expense_frame = pd.DataFrame(all_expenses)

    expense_frame.rename(columns={'amount': 'expense_amount', 'source': 'expense_source'}, inplace=True)
    expense_frame.set_index('creation_date', drop=True, inplace=True)
    expense_frame.index = pd.to_datetime(expense_frame.index)

    budget_frame = income_frame.join(expense_frame, how='outer')
    budget_frame.fillna({
        'expense_amount': 0.0,
        'income_amount': 0.0,
        'expense_source': '-',
        'income_source': '-'
    }, inplace=True)

    return budget_frame
