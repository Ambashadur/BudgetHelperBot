import re
from datetime import datetime


def find_amount(user_text: str) -> float:
    search_result = re.search('-c \d{1,12}(([.,]\d{1,2})|\s|$)', user_text)

    if search_result is None:
        return None

    return float(search_result.group()[3:])


def find_datetime(user_text: str) -> datetime:
    search_result = re.search('-d \d{1,2}.\d{1,2}.\d{4}(( (([0-1][0-9])|([2][0-3])):([0-5][0-9]))|\s|$)', user_text)

    if search_result is None:
        return datetime.now()

    try:
        date = datetime.strptime(search_result.group()[3:], '%d.%m.%Y %H:%M')
    except:
        date = datetime.strptime(search_result.group()[3:], '%d.%m.%Y')

    return date


def find_source(user_text_without_command: str) -> str:
    search_result = re.search('\s[a-zA-z.,\s]*\s', user_text_without_command)

    if search_result is None:
        return ''
    else:
        return search_result.group()
