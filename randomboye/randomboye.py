from definitions import FUNCTION_CALL_MSG
from randomboye.discogs_collection import DiscogsCollection
from logs.config import logger
from randomboye.helpers import create_framebuffers
from multiprocessing import Process
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
        self.pi.back_button.latest_event = None
        self.pi.front_button.when_pressed = self.front_button_press_override
        self.pi.front_button.when_held = self.front_button_hold_override
        self.pi.front_button.when_released = self.front_button_relase_override
        self.print_processes = []
        self.current_print_process = None
        self.state = 'STARTUP'  # Valids: STARTUP, INSTRUCTIONS, RECORD

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

    def random_record_framebuffers(self):
        logger.debug(FUNCTION_CALL_MSG)
        random_record = self.dc.get_random_record()
        artist_and_title = [random_record['record']['artist'], random_record['record']['title']]
        return create_framebuffers(artist_and_title)

    def instructions_framebuffers(self):
        logger.debug(FUNCTION_CALL_MSG)
        instructions = [
            'Press For Random',
            'Record  d[-_-]b'
        ]
        return create_framebuffers(instructions)

    def start_print_process(self, framebuffers):
        logger.debug(FUNCTION_CALL_MSG)
        self.current_print_process = Process(
            target=self.pi.write_framebuffers,
            kwargs={'framebuffers': framebuffers}
        )
        self.current_print_process.start()
        self.print_processes.append(self.current_print_process)

    def terminate_current_print_process(self):
        logger.debug(FUNCTION_CALL_MSG)
        if self.current_print_process is not None:
            self.current_print_process.terminate()
            self.current_print_process.join()

    def print_processes_cleanup(self):
        logger.debug(FUNCTION_CALL_MSG)
        logger.debug(f"{len(self.print_processes)} threads to clean up")
        while len(self.print_processes) > 0:
            self.print_processes[0].terminate()
            self.print_processes[0].join()
            self.print_processes.pop(0)

    def front_button_press_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.pi.front_button.latest_event = 'press'

    def front_button_hold_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        try:
            if self.pi.front_button.latest_event:
                if self.pi.front_button.latest_event == 'hold':
                    logger.debug("Hold After Hold - No Action")

                if self.pi.front_button.latest_event == 'release':
                    logger.debug("Hold After Release - No Action")

                if self.pi.front_button.latest_event == 'press':
                    logger.debug("Hold After Press - Cleanup Processes")
                    self.terminate_current_print_process()
                    self.print_processes_cleanup()
                    self.pi.lcd_cleanup
        finally:
            self.pi.front_button.latest_event = 'hold'

    def front_button_relase_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        try:
            if self.pi.front_button.latest_event:
                if self.pi.front_button.latest_event == 'hold':
                    logger.debug("Release After Hold - Post Cleanup")

                if self.pi.front_button.latest_event == 'release':
                    logger.debug("Release After Release - No Action")

                if self.pi.front_button.latest_event == 'press':
                    self.terminate_current_print_process()
                    if self.state in ['INSTRUCTIONS']:
                        logger.debug("Release After Press - Random Record")
                        self.start_print_process(self.random_record_framebuffers())
                        self.state = 'RECORD'
                    elif self.state in ['STARTUP', 'RECORD']:
                        logger.debug("Release After Press - Print Instructions")
                        self.start_print_process(self.instructions_framebuffers())
                        self.state = 'INSTRUCTIONS'

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
