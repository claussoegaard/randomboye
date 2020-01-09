import os
LOGGING_FOLDER = "logs"

# Creating logs dir if it doesn't already exist
if not os.path.exists(LOGGING_FOLDER):
    os.makedirs(LOGGING_FOLDER)

# Good example of configs:
# https://stackoverflow.com/questions/7507825/where-is-a-complete-example-of-logging-config-dictconfig

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'loggers': {
        '': {  # root logger
            'level': 'NOTSET',
            'handlers': ['info_console_handler', 'debug_file_handler', 'info_file_handler', 'error_file_handler'],
        },
        'discogs_collection': {
            'level': 'DEBUG',
            'propagate': False,
            'handlers': ['info_console_handler', 'debug_file_handler', 'info_file_handler', 'error_file_handler'],
        },
        'raspi_io_diagnoser': {
            'level': 'DEBUG',
            'propagate': False,
            'handlers': ['info_console_handler', 'debug_file_handler', 'info_file_handler', 'error_file_handler'],
        },
        # 'looper': {
        #     'level': 'INFO',
        #     'propagate': False,
        #     'handlers': ['looper_info_file_handler', 'looper_error_file_handler']
        # },
    },
    'handlers': {
        'info_console_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'debug_file_handler': {
            'level': 'DEBUG',
            'formatter': 'debug',
            'class': 'logging.FileHandler',
            'filename': f'{LOGGING_FOLDER}/debug.log',
            'mode': 'a',
        },
        'info_file_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.FileHandler',
            'filename': f'{LOGGING_FOLDER}/info.log',
            'mode': 'a',
        },
        # 'looper_info_file_handler': {
        #     'level': 'INFO',
        #     'formatter': 'looper_info',
        #     'class': 'logging.FileHandler',
        #     'filename': 'looper_info.log',
        #     'mode': 'a',
        # },
        'error_file_handler': {
            'level': 'WARNING',
            'formatter': 'error',
            'class': 'logging.FileHandler',
            'filename': f'{LOGGING_FOLDER}/error.log',
            'mode': 'a',
        },
        # 'looper_error_file_handler': {
        #     'level': 'WARNING',
        #     'formatter': 'looper_error',
        #     'class': 'logging.FileHandler',
        #     'filename': 'looper_error.log',
        #     'mode': 'a',
        # },
    },
    'formatters': {
        'debug': {
            'format': '%(asctime)s :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)s :: %(message)s'
        },
        'info': {
            'format': '%(asctime)s :: %(levelname)s :: %(name)s :: %(module)s :: %(funcName)s :: %(lineno)s :: %(message)s'
        },
        # 'looper_info': {
        #     'format': '%(asctime)s :: %(levelname)s :: %(name)s :: %(module)s :: %(threadName)s :: %(thread)d :: %(lineno)s :: %(message)s'
        # },
        'error': {
            'format': '%(asctime)s :: %(levelname)s :: %(name)s :: %(process)d :: %(module)s :: %(funcName)s :: %(lineno)s :: %(message)s'
        },
        # 'looper_error': {
        #     'format': '%(asctime)s :: %(levelname)s :: %(name)s :: %(process)d :: %(module)s :: %(threadName)s :: %(thread)d :: %(lineno)s :: %(message)s'
        # },
    },
}
