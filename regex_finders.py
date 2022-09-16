import re
from datetime import datetime


def find_amount(text: str) -> float:
    if search_result := re.search('(\d{1,6}([.,]\d{1,2}))|(\d{1,6}[.])|(\d{1,6})', text):
        return float(search_result.group())
    else:
        return None


def find_datetime(text: str) -> datetime:
    if search_result := re.search(
            '([1-9]|[1-2][0-9]|3[0-2]|0[1-9]).([1-9]|1[0-2]|0[1-9]).\d{4}(\s?(([0-1][0-9]|2[0-3]):([0-5][0-9]))|)',
            text):
        try:
            date = datetime.strptime(search_result.group(), '%d.%m.%Y %H:%M')
        except:
            date = datetime.strptime(search_result.group(), '%d.%m.%Y')

        return date
    else:
        return None


def find_source(text: str) -> str:
    if search_result := re.search('[a-zA-zа-яА-я.,\s]+', text):
        return search_result.group()
    else:
        return None
