from definitions import FUNCTION_CALL_MSG
from randomboye.discogs_collection import DiscogsCollection
import os
import signal
# from multiprocessing import Process
from logs.config import logger
logger = logger(__name__)


def when_held_override():
    logger.debug(FUNCTION_CALL_MSG)
    os.kill(pi, signal.SIGUSR1)


def start(auth_token, is_test, refresh_collection):
    if not is_test:
        from randomboye.raspi import RaspberryPi
        global pi
        pi = RaspberryPi()
        pi.start()
        logger.debug("After Raspberry Pi Is Init")
        logger.debug(f"{pi}")
        pi.back_button.when_held = when_held_override
    else:
        pass

    dc = DiscogsCollection(auth_token=auth_token, refresh_collection=refresh_collection)
    dc.get_random_record()

    pi.join()

    logger.debug("After Raspberry Pi Is Shut Down")
