import os
from definitions import ROOT_DIR
import logging
from logging.config import dictConfig

full_path_to_logs = f"{ROOT_DIR}/logs/logs"

# Creating logs dir if it doesn't already exist
if not os.path.exists(full_path_to_logs):
    os.makedirs(full_path_to_logs)

# Good example of configs:
# https://stackoverflow.com/questions/7507825/where-is-a-complete-example-of-logging-config-dictconfig


LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        '': {  # root logger
            'level': 'NOTSET',
            'handlers': ['debug_console_handler', 'debug_file_handler', 'info_file_handler', 'error_file_handler'],
        },
        'main': {
            'level': 'DEBUG',
            'propagate': False,
            'handlers': ['debug_console_handler', 'debug_file_handler', 'info_file_handler', 'error_file_handler'],
        },
        'discogs_collection': {
            'level': 'DEBUG',
            'propagate': False,
            'handlers': ['debug_console_handler', 'debug_file_handler', 'info_file_handler', 'error_file_handler'],
        },
        'raspi_io_diagnoser': {
            'level': 'DEBUG',
            'propagate': False,
            'handlers': ['debug_console_handler', 'debug_file_handler', 'info_file_handler', 'error_file_handler'],
        },
    },
    'handlers': {
        'debug_console_handler': {
            'level': 'DEBUG',
            'formatter': 'debug',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'debug_file_handler': {
            'level': 'DEBUG',
            'formatter': 'debug',
            'class': 'logging.FileHandler',
            'filename': f'{full_path_to_logs}/debug.log',
            'mode': 'a',
        },
        'info_file_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.FileHandler',
            'filename': f'{full_path_to_logs}/info.log',
            'mode': 'a',
        },
        'error_file_handler': {
            'level': 'WARNING',
            'formatter': 'error',
            'class': 'logging.FileHandler',
            'filename': f'{full_path_to_logs}/error.log',
            'mode': 'a',
        },
    },
    'formatters': {
        'info': {
            'format': '%(asctime)s :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)s :: %(message)s'
        },
        'error': {
            'format': '%(asctime)s :: %(levelname)s :: %(name)s :: %(process)d :: %(module)s :: %(funcName)s :: %(lineno)s :: %(message)s'
        },
        'debug': {
            'format': '%(asctime)s :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(threadName)s :: %(thread)d :: %(lineno)s :: %(message)s'
        },
    },
}


def logger(module):
    dictConfig(LOGGING_CONFIG)
    return logging.getLogger(module)
