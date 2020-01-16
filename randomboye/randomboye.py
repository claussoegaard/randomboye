from definitions import FUNCTION_CALL_MSG
from randomboye.discogs_collection import DiscogsCollection
from logs.config import logger
from randomboye.helpers import create_framebuffers
logger = logger(__name__)


def front_button_when_pressed_override():
    logger.debug(FUNCTION_CALL_MSG)
    random_record = dc.get_random_record()
    artist_title = [random_record['record']['artist'], random_record['record']['title']]
    record = create_framebuffers(artist_title)
    pi.write_framebuffers(record)
    # os.kill(pi.pid, signal.SIGUSR1)


def start(auth_token, is_test, refresh_collection):
    global dc
    dc = DiscogsCollection(auth_token=auth_token, refresh_collection=refresh_collection)
    if not is_test:
        from randomboye.raspi import RaspberryPi
        global pi
        pi = RaspberryPi()
        pi.start()
        logger.debug("After Raspberry Pi Is Init")
        logger.debug(f"{pi}")
        pi.front_button.when_pressed = front_button_when_pressed_override
    else:
        pass

    pi.join()

    logger.debug("After Raspberry Pi Is Shut Down")
