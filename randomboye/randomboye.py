from definitions import FUNCTION_CALL_MSG
from randomboye.discogs_collection import DiscogsCollection
from logs.config import get_logger
from multiprocessing import Process
import signal
import time
import os
logger = get_logger(__name__)


class RandomBoye(Process):
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
        self.print_processes = []
        self.current_print_process = None
        self.state = 'STARTUP'  # Valids: STARTUP, INSTRUCTIONS, RECORD
        # self.Pi = None
        # Conditional imports
        global Pi
        if not is_test:
            from randomboye.raspi import RaspberryPi as Pi

    def run(self):
        self.startup()
        signal.pause()

    def startup(self):
        self.pi = self.get_pi(self.is_test)
        self.pi.startup_method = self.pi_startup_method_override
        self.pi.front_button.latest_event = None
        self.pi.back_button.latest_event = None
        logger.debug("Setting button overrides")
        self.pi.front_button.when_pressed = self.front_button_press_override
        self.pi.front_button.when_held = self.front_button_hold_override
        self.pi.front_button.when_released = self.front_button_release_override
        self.pi.back_button.when_held = self.back_button_hold_override
        self.pi.back_button.when_pressed = self.back_button_press_override
        self.pi.back_button.when_released = self.back_button_release_override
        logger.debug("Starting Pi")
        self.pi.start()

    def get_pi(self, is_test):
        logger.debug(FUNCTION_CALL_MSG)
        if not is_test:
            pi = Pi(shutdown_system=self.shutdown_system)
            return pi
        else:
            raise NotImplementedError

    def pi_startup_method_override(self):
        # self.pi.default_startup_text()
        logger.debug("Regular Startup")
        self.pi.set_startup_method()
        logger.debug("Sleep 1")
        time.sleep(1)
        logger.debug("Get Collection")
        self.get_discogs_collection()
        logger.debug("Sleep 2")
        time.sleep(2)

    def get_discogs_collection(self):
        logger.debug(FUNCTION_CALL_MSG)
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
        logger.debug("Starting Lines")
        self.start_print_process(starting_lines)
        # self.pi.lock.acquire()
        self.dc = DiscogsCollection(auth_token=self.auth_token, refresh_collection=self.refresh_collection)
        logger.debug("Sleep at least 2 while discogs collection is being fetched")
        time.sleep(2)
        record_count = self.dc.collection['record_count']
        ending_lines = [
            'Got Collection',
            f'Records: {record_count}'
        ]
        # self.pi.lock.release()
        logger.debug("Ending Lines")
        self.start_print_process(ending_lines)
        time.sleep(2)
        self.start_print_process(self.instructions_lines())
        self.state = 'INSTRUCTIONS'

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
        # Start by terminating any existing print process
        self.terminate_current_print_process()
        self.current_print_process = Process(
            target=self.pi.stream_lines,
            kwargs={'lines': lines}
        )
        self.current_print_process.start()
        self.print_processes.append(self.current_print_process)

    def terminate_current_print_process(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.pi.lock.acquire()
        logger.debug("Lock Acquired In Terminate Current")
        if self.current_print_process is not None:
            self.current_print_process.terminate()
            logger.debug("Blocking until current print process dead")
            self.current_print_process.join()
        self.pi.lock.release()
        logger.debug("Lock Released In Terminate Current")

    def print_processes_cleanup(self):
        logger.debug(FUNCTION_CALL_MSG)
        logger.debug(f"{len(self.print_processes)} threads to clean up")
        self.pi.lock.acquire()
        logger.debug("Lock Acquired In Terminate All Prints")
        while len(self.print_processes) > 0:
            self.print_processes[0].terminate()
            logger.debug("Blocking for each cleanup step")
            self.print_processes[0].join()
            self.print_processes.pop(0)
        self.pi.lock.release()
        logger.debug("Lock Released In Terminate All Prints")

    def cleanup(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.terminate_current_print_process()
        self.print_processes_cleanup()
        self.pi.lcd_cleanup()

    def full_cleanup(self):
        self.terminate_current_print_process()
        self.print_processes_cleanup()
        self.pi.lcd_cleanup()
        logger.debug("Terminating Pi")
        # self.pi.terminate()
        os.killpg(self.pi.pid, signal.SIGUSR1)
        logger.debug("Joining Pi To Main Thread")
        self.pi.join()
        logger.debug("Starting Self again")
        self.startup()

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
                        self.cleanup()
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
                        self.cleanup()
                        self.start_print_process(["Byeeeee...", ""])
                        self.current_print_process.join()
                        self.pi.shutdown2()

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
        pressed_time = 0
        try:
            if self.pi.front_button.latest_event:
                if self.pi.front_button.latest_event == 'hold':
                    pressed_time = self.pi.front_button.pressed_time
                    logger.debug(f"Hold After Hold (Front, {pressed_time} seconds) - No Action")
                    if self.pi.front_button.is_long_hold_time():
                        self.pi.front_button.hold_repeat = False
                        self.cleanup()
                        # self.start_print_process(["Release To", "Shut Down"])

                if self.pi.front_button.latest_event == 'release':
                    logger.debug("Hold After Release (Front) - No Action")

                if self.pi.front_button.latest_event == 'press':
                    logger.debug("Hold After Press (Front) - Cleanup Processes")
                    # self.full_cleanup()
                    # self.start_print_process(self.instructions_lines())
                    # self.state = 'INSTRUCTIONS'
        finally:
            self.pi.front_button.latest_event = 'hold'
            self.pi.front_button.latest_hold_time = pressed_time

    def front_button_release_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        try:
            if self.pi.front_button.latest_event:
                if self.pi.front_button.latest_event == 'hold':
                    latest_hold_time = self.pi.front_button.latest_hold_time
                    logger.debug(f"Release After Hold (Front, {latest_hold_time} seconds) - No Action")
                    if self.pi.front_button.was_latest_hold_long():
                        self.pi.front_button.hold_repeat = True
                        self.start_print_process(self.instructions_lines())
                        self.state = 'INSTRUCTIONS'
                        # self.full_cleanup()

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
