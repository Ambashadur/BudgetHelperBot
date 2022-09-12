import re
from datetime import datetime


def find_amount(text: str) -> float:
    search_result = re.search('(\d{1,12}([.,]\d{1,2}))|(\d{1,12}[.,])|(\d{1,12})', text)

    if search_result is None:
        return None

    return float(search_result.group())


def find_datetime(text: str) -> datetime:
    search_result = re.search(
        '([1-9]|[1-2][0-9]|3[0-2]).([1-9]|1[0-2]).\d{4}(\s?(([0-1][0-9]|2[0-3]):([0-5][0-9]))|)',
        text)

    if search_result is None:
        return datetime.now()

    try:
        date = datetime.strptime(search_result.group(), '%d.%m.%Y %H:%M')
    except:
        date = datetime.strptime(search_result.group(), '%d.%m.%Y')

    return date


def find_source(text: str) -> str:
    search_result = re.search('[a-zA-zа-яА-я.,\s]+', text)

    if search_result is None:
        return None
    else:
        return search_result.group()
