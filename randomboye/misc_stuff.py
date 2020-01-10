import logging
from logging.config import dictConfig
from logging_config import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
FUNCTION_CALL_MSG = 'function_call'

import threading
from time import sleep


class PrinterTest(threading.Thread):
    def __init__(self):
        logger.debug(FUNCTION_CALL_MSG)
        super(PrinterTest, self).__init__()

    def run(self):
        logger.debug(FUNCTION_CALL_MSG)
        for i in range(5):
            print(i)
            sleep(1)
            print(threading.Event())

    def join(self):
        logger.debug(FUNCTION_CALL_MSG)

    def kill(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.killed = True


test_obj = PrinterTest()
test_obj.start()
test_obj.join()
