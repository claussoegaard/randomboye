import os
from datetime import datetime
import logging
import shutil
import json
from definitions import ROOT_DIR
from logging.config import dictConfig


full_path_to_logs = f"{ROOT_DIR}/logs/logs"
full_path_to_log_archive = f"{ROOT_DIR}/logs/logs/archive"

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
        'raspi': {
            'level': 'DEBUG',
            'propagate': False,
            'handlers': ['debug_console_handler', 'debug_file_handler', 'info_file_handler', 'error_file_handler'],
        },
        'randomboye': {
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
            'filename': f'{full_path_to_logs}/debug_current.log',
            'mode': 'a',
        },
        'info_file_handler': {
            'level': 'INFO',
            'formatter': 'info',
            'class': 'logging.FileHandler',
            'filename': f'{full_path_to_logs}/info_current.log',
            'mode': 'a',
        },
        'error_file_handler': {
            'level': 'WARNING',
            'formatter': 'error',
            'class': 'logging.FileHandler',
            'filename': f'{full_path_to_logs}/error_current.log',
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


def setup_logging():
    """
    This is a fairly hacky setup that doesn't safeguard much against whether files
    exist or not and atomic-ness etc. But w/e.
    """

    # Creating logs dir if it doesn't already exist
    if not os.path.exists(full_path_to_logs):
        os.makedirs(full_path_to_logs)

    # Creating log archive dir if it doesn't already exist
    if not os.path.exists(full_path_to_log_archive):
        os.makedirs(full_path_to_log_archive)

    # Creating log metadata file if it doesn't exist
    logs_metadata_file = f"{full_path_to_logs}/logs_metadata.txt"
    if not os.path.isfile(logs_metadata_file):
        with open(logs_metadata_file, 'w'):
            pass

    # Creating log metadata archive file if it doesn't exist
    logs_metadata_archive_file = f"{full_path_to_logs}/logs_metadata_archive.txt"
    if not os.path.isfile(logs_metadata_archive_file):
        with open(logs_metadata_archive_file, 'w'):
            pass

    now = datetime.today()
    now_str = now.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    month = datetime(now.year, now.month, 1)
    month_str = month.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    yyyy_mm = now.strftime("%Y-%m")

    new_metadata_entry = {
        'timestamp': now_str,
        'month': month_str,
        'yyyy_mm': yyyy_mm
    }

    # If file is empty, create an entry
    # even if nothing was changed
    if os.stat(logs_metadata_file).st_size == 0:
        new_metadata_entry['extra'] = "First Entry"
        with open(logs_metadata_file, 'a') as f:
            json.dump(new_metadata_entry, f)
            f.write(os.linesep)

    # Read the metadata file
    log_metadata = {}
    with open(logs_metadata_file, "r") as f:
        log_metadata = json.load(f)

    # If date of entry is same month as current month, do nothing
    if yyyy_mm == log_metadata['yyyy_mm']:
        return

    # At this point, yyyy_mm values don't match, so do renaming stuff

    # Copy file_current.log files to archive folder
    for s in ['info', 'debug', 'error']:
        file_name = f"{s}_current.log"
        full_file_name = f"{full_path_to_logs}/{file_name}"
        new_file_name = f"{s}_{log_metadata['yyyy_mm']}.log"
        full_new_file_name = f"{full_path_to_log_archive}/{new_file_name}"
        shutil.copyfile(
            full_file_name,
            full_new_file_name
        )
        # Emptying _current file
        with open(full_file_name, 'w') as f:
            pass

    # Write old metadata to archive
    with open(logs_metadata_archive_file, 'a') as f:
        json.dump(log_metadata, f)
        f.write(os.linesep)

    new_metadata_entry['extra'] = f"Moved {log_metadata['yyyy_mm']} log files to archive."
    # Write new metadata to metadata file
    with open(logs_metadata_file, 'w') as f:
        json.dump(new_metadata_entry, f)


def get_logger(module):
    dictConfig(LOGGING_CONFIG)
    return logging.getLogger(module)
