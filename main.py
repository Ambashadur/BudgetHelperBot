from bot_commands import *

if __name__ == '__main__':
    log_format = '[%(asctime)s] [%(levelname)s]    %(message)s'
    logging.basicConfig(level=logging.INFO, format=log_format)

    ensure_db_created()
    load_token()
    set_bot_commands()
    processing_get_updates()
