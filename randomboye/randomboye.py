from definitions import FUNCTION_CALL_MSG
from randomboye.discogs_collection import DiscogsCollection
from logs.config import logger
from multiprocessing import Process
import time
logger = logger(__name__)


class RandomBoye(object):
    """docstring for Randomboye"""

    def __init__(self, auth_token, is_test, refresh_collection, shutdown_system):
        super().__init__()
        logger.debug(f"{FUNCTION_CALL_MSG}, {__class__}")
        self.auth_token = auth_token
        self.is_test = is_test
        self.refresh_collection = refresh_collection
        self.shutdown_system = shutdown_system
        self.dc = DiscogsCollection(auth_token=self.auth_token, refresh_collection=self.refresh_collection)
        self.pi = None
        # self.pi.startup_method = self.pi_startup_method_override
        self.print_processes = []
        self.current_print_process = None
        self.state = 'STARTUP'  # Valids: STARTUP, INSTRUCTIONS, RECORD
        # self.Pi = None
        # Conditional imports
        global Pi
        if not is_test:
            from randomboye.raspi import RaspberryPi as Pi

    def start(self):
        self.pi = self.get_pi(self.is_test)
        self.pi.front_button.latest_event = None
        self.pi.back_button.latest_event = None
        self.pi.front_button.when_pressed = self.front_button_press_override
        self.pi.front_button.when_held = self.front_button_hold_override
        self.pi.front_button.when_released = self.front_button_release_override
        self.pi.back_button.when_held = self.back_button_hold_override
        self.pi.back_button.when_pressed = self.back_button_press_override
        self.pi.back_button.when_released = self.back_button_release_override
        self.pi.start()

    def get_pi(self, is_test):
        logger.debug(FUNCTION_CALL_MSG)
        if not is_test:
            # from randomboye.raspi import RaspberryPi
            pi = Pi(shutdown_system=self.shutdown_system)
            return pi
        else:
            raise NotImplementedError

    def pi_startup_method_override(self):
        self.pi.default_startup_text()
        self.get_discogs_collection()
        time.sleep(1)
        self.full_cleanup()

    def get_discogs_collection(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.terminate_current_print_process()
        if self.refresh_collection:
            starting_lines = [
                'Getting Records',
                'From Discogs...'
            ]
        else:
            starting_lines = [
                'Getting Records',
                'From File...'
            ]
        self.start_print_process(starting_lines)
        self.dc = DiscogsCollection(auth_token=self.auth_token, refresh_collection=self.refresh_collection)
        record_count = self.dc.collection['record_count']
        ending_lines = [
            'Got Collection',
            f'Records: {record_count}'
        ]
        self.terminate_current_print_process()
        self.start_print_process(ending_lines)

    def random_record_lines(self):
        logger.debug(FUNCTION_CALL_MSG)
        random_record = self.dc.get_random_record()
        return [random_record['record']['artist'], random_record['record']['title']]

    def instructions_lines(self):
        logger.debug(FUNCTION_CALL_MSG)
        return [
            'Press For Random',
            'Record  d[-_-]b'
        ]

    def start_print_process(self, lines):
        logger.debug(FUNCTION_CALL_MSG)
        self.current_print_process = Process(
            target=self.pi.stream_lines,
            kwargs={'lines': lines}
        )
        self.current_print_process.start()
        self.print_processes.append(self.current_print_process)

    def terminate_current_print_process(self):
        logger.debug(FUNCTION_CALL_MSG)
        if self.current_print_process is not None:
            self.current_print_process.terminate()
            logger.debug("Blocking until current print process dead")
            self.current_print_process.join()

    def print_processes_cleanup(self):
        logger.debug(FUNCTION_CALL_MSG)
        logger.debug(f"{len(self.print_processes)} threads to clean up")
        while len(self.print_processes) > 0:
            self.print_processes[0].terminate()
            logger.debug("Blocking for each cleanup step")
            self.print_processes[0].join()
            self.print_processes.pop(0)

    def full_cleanup(self):
        self.terminate_current_print_process()
        self.print_processes_cleanup()
        self.pi.lcd_cleanup()
        self.pi.terminate()
        self.pi.join()
        self.start()

    def back_button_press_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.pi.back_button.latest_event = 'press'

    def back_button_hold_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        pressed_time = 0
        try:
            if self.pi.back_button.latest_event:
                if self.pi.back_button.latest_event == 'hold':
                    pressed_time = self.pi.back_button.pressed_time
                    logger.debug(f"Hold After Hold (Back, {pressed_time} seconds) - No Action")
                    if self.pi.back_button.is_long_hold_time():
                        self.pi.back_button.hold_repeat = False
                        self.full_cleanup()
                        self.start_print_process(["Release To", "Shut Down"])
                        # self.pi.shutdown_message()
                        # self.pi.back_button.latest_event = 'long_hold'
                        # self.pi.shutdown()

                if self.pi.back_button.latest_event == 'release':
                    logger.debug("Hold After Release (Back) - No Action")

                if self.pi.back_button.latest_event == 'press':
                    logger.debug("Hold After Press (Back) - Cleanup Processes")
                    # self.full_cleanup()
                    # self.pi.stream_lines(['Shutting Down', 'Byeee!'])
        finally:
            self.pi.back_button.latest_event = 'hold'
            self.pi.back_button.latest_hold_time = pressed_time

    def back_button_release_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        try:
            if self.pi.back_button.latest_event:
                if self.pi.back_button.latest_event == 'hold':
                    latest_hold_time = self.pi.back_button.latest_hold_time
                    logger.debug(f"Release After Hold (Back, {latest_hold_time} seconds) - No Action")
                    if self.pi.back_button.was_latest_hold_long():
                        self.pi.shutdown()

                if self.pi.back_button.latest_event == 'release':
                    logger.debug("Release After Release (Back) - No Action")

                if self.pi.back_button.latest_event == 'press':
                    logger.debug("Release After Press (Back) - No Action")
        finally:
            self.pi.back_button.latest_event = 'release'

    def front_button_press_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.pi.front_button.latest_event = 'press'

    def front_button_hold_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        try:
            if self.pi.front_button.latest_event:
                if self.pi.front_button.latest_event == 'hold':
                    logger.debug("Hold After Hold (Front) - No Action")

                if self.pi.front_button.latest_event == 'release':
                    logger.debug("Hold After Release (Front) - No Action")

                if self.pi.front_button.latest_event == 'press':
                    logger.debug("Hold After Press (Front) - Cleanup Processes")
                    self.full_cleanup()
                    self.start_print_process(self.instructions_lines())
                    self.state = 'INSTRUCTIONS'
        finally:
            self.pi.front_button.latest_event = 'hold'

    def front_button_release_override(self):
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
                        self.start_print_process(self.random_record_lines())
                        self.state = 'RECORD'
                    elif self.state in ['STARTUP', 'RECORD']:
                        logger.debug("Release After Press - Print Instructions")
                        self.start_print_process(self.instructions_lines())
                        self.state = 'INSTRUCTIONS'

        finally:
            self.pi.front_button.latest_event = 'release'
