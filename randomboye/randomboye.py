from definitions import FUNCTION_CALL_MSG
from randomboye.discogs_collection import DiscogsCollection
from logs.config import logger
from randomboye.helpers import create_framebuffers
logger = logger(__name__)


class RandomBoye(object):
    """docstring for Randomboye"""

    def __init__(self, auth_token, is_test, refresh_collection):
        super().__init__()
        logger.debug(f"{FUNCTION_CALL_MSG}, {__class__}")
        self.dc = DiscogsCollection(auth_token=auth_token, refresh_collection=refresh_collection)
        self.pi = self.set_pi(is_test)
        self.pi.front_button.when_pressed = self.front_button_press_override

    def set_pi(self, is_test):
        logger.debug(FUNCTION_CALL_MSG)
        if not is_test:
            from randomboye.raspi import RaspberryPi
            self.pi = RaspberryPi()
            self.pi.start()
            # logger.debug("After Raspberry Pi Is Init")
            # logger.debug(f"{pi}")
            # pi.front_button.when_pressed = front_button_when_pressed_override
        else:
            raise NotImplementedError

    def front_button_press_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        random_record = self.dc.get_random_record()
        artist_title = [random_record['record']['artist'], random_record['record']['title']]
        record = create_framebuffers(artist_title)
        self.pi.write_framebuffers(record)


# def start(auth_token, is_test, refresh_collection):
#     global dc
#     dc = DiscogsCollection(auth_token=auth_token, refresh_collection=refresh_collection)
#     if not is_test:
#         from randomboye.raspi import RaspberryPi
#         global pi
#         pi = RaspberryPi()
#         pi.start()
#         logger.debug("After Raspberry Pi Is Init")
#         logger.debug(f"{pi}")
#         pi.front_button.when_pressed = front_button_when_pressed_override
#     else:
#         pass

#     pi.join()

#     logger.debug("After Raspberry Pi Is Shut Down")
