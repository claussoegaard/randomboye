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
        self.pi = self.get_pi(is_test)
        self.pi.start()
        self.pi.front_button.latest_event = None
        self.pi.back_buton.latest_event = None
        self.pi.front_button.when_pressed = self.front_button_press_override

    def get_pi(self, is_test):
        logger.debug(FUNCTION_CALL_MSG)
        if not is_test:
            from randomboye.raspi import RaspberryPi
            pi = RaspberryPi()
            return pi
            # self.pi = RaspberryPi()
            # self.pi.start()
            # logger.debug("After Raspberry Pi Is Init")
            # logger.debug(f"{pi}")
            # pi.front_button.when_pressed = front_button_when_pressed_override
        else:
            raise NotImplementedError

    def front_button_press_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.pi.front_button.latest_event = 'press'

    def front_button_hold_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.pi.front_button.latest_event = 'hold'

    def front_button_relase_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        try:
            if self.pi.front_button.latest_event:
                if self.pi.front_button.latest_event == 'hold':
                    logger.debug("Release After Hold - No Action")
                if self.pi.front_button.latest_event == 'release':
                    logger.debug("Release After Release - No Action")
                if self.pi.front_button.latest_event == 'press':
                    logger.debug("Release After Press - Random Record Flip")
                    random_record = self.dc.get_random_record()
                    artist_title = [random_record['record']['artist'], random_record['record']['title']]
                    record = create_framebuffers(artist_title)
                    self.pi.write_framebuffers(record)
        finally:
            self.pi.front_button.latest_event = 'release'


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
