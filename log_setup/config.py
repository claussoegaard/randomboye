import os
import pathlib
current_folder = str(pathlib.Path(__file__).parent.absolute())
full_path_to_logs = current_folder + "/logs"
# LOGGING_FOLDER = "logs"

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
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'debug_file_handler': {
            'level': 'DEBUG',
            'formatter': 'debug',
            'class': 'logging.FileHandler',
            'filename': f'{current_folder}/debug.log',
            'mode': 'a',
        },
        'info_file_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.FileHandler',
            'filename': f'{current_folder}/info.log',
            'mode': 'a',
        },
        'error_file_handler': {
            'level': 'WARNING',
            'formatter': 'error',
            'class': 'logging.FileHandler',
            'filename': f'{current_folder}/error.log',
            'mode': 'a',
        },
    },
    'formatters': {
        # 'debug': {
        #     'format': '%(asctime)s :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)s :: %(message)s'
        # },
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
