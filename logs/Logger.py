from datetime import datetime
import os

ACCESS_LOG = os.path.join(os.path.dirname(__file__), 'access.log')
ERROR_LOG = os.path.join(os.path.dirname(__file__), 'error.log')


def log_access(message):
    with open(ACCESS_LOG, 'a') as f:
        f.write(f'[{datetime.now()}]: {message}\n')
        f.close()


def log_error(message):
    with open(ERROR_LOG, 'a') as f:
        f.write(f'[{datetime.now()}]: {message}\n')
        f.close()


def get_access_log():
    with open(ACCESS_LOG, 'r') as f:
        log = f.read()
        f.close()
    return log


def get_error_log():
    with open(ERROR_LOG, 'r') as f:
        log = f.read()
        f.close()
    return log


def clear_access_log():
    with open(ACCESS_LOG, 'w') as f:
        f.write('')
        f.close()


def clear_error_log():
    with open(ERROR_LOG, 'w') as f:
        f.write('')
        f.close()