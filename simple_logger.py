from enum import Enum


class LogLevel(Enum):
    INFORMATION = 1,
    WARNING = 2,
    ERROR = 3


def log(log_level: LogLevel, message: str):
    match log_level:
        case LogLevel.INFORMATION:
            print(message)
