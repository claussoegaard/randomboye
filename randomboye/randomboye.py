from definitions import FUNCTION_CALL_MSG
from randomboye.discogs_collection import DiscogsCollection
from logs.config import get_logger
from multiprocessing import Process
from threading import Thread
import signal
import time
logger = get_logger(__name__)


class RandomBoye(Thread):
    """docstring for Randomboye"""

    def __init__(self, auth_token, is_test, refresh_collection, shutdown_system):
        super().__init__()
        logger.debug(f"{FUNCTION_CALL_MSG}, {__class__}")
        self.auth_token = auth_token
        self.is_test = is_test
        self.refresh_collection = refresh_collection
        self.shutdown_system = shutdown_system
        self.dc = None
        self.io = None
        self.print_processes = []
        self.current_print_process = None
        self.state = 'STARTUP'  # Valids: STARTUP, INSTRUCTIONS, RECORD

    def run(self):
        self.startup()
        signal.pause()

    def startup(self):
        self.io = self.get_io(self.is_test)
        self.io.startup_method = self.io_startup_method_override
        self.io.front_button.latest_event = None
        self.io.back_button.latest_event = None
        logger.debug("Setting button overrides")
        self.io.front_button.when_pressed = self.front_button_press_override
        self.io.front_button.when_held = self.front_button_hold_override
        self.io.front_button.when_released = self.front_button_release_override
        self.io.back_button.when_held = self.back_button_hold_override
        self.io.back_button.when_pressed = self.back_button_press_override
        self.io.back_button.when_released = self.back_button_release_override
        logger.debug("Starting IO Device")
        self.io.start()

    def get_io(self, is_test):
        logger.debug(FUNCTION_CALL_MSG)
        if not is_test:
            from randomboye.raspi import RaspberryPi
            io = RaspberryPi(shutdown_system=self.shutdown_system)
            return io
        else:
            from randomboye.raspi_default_test import RaspberryPiDefaultTest
            io = RaspberryPiDefaultTest(shutdown_system=self.shutdown_system)
            return io

    def io_startup_method_override(self):
        logger.debug("Regular Startup")
        self.io.default_startup_method()
        logger.debug("Sleep 1")
        time.sleep(1)
        logger.debug("Get Collection")
        self.get_discogs_collection_startup()
        logger.debug("Sleep 2")
        time.sleep(2)

    def get_discogs_collection_startup(self):
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
        self.dc = DiscogsCollection(auth_token=self.auth_token, refresh_collection=self.refresh_collection)
        logger.debug("Sleep at least 2 while discogs collection is being fetched")
        time.sleep(2)
        record_count = self.dc.collection['record_count']
        ending_lines = [
            'Got Collection',
            f'Records: {record_count}'
        ]
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
            'Press Button For',
            f'Random Record {self.io.smiley} '
        ]

    def start_print_process(self, lines):
        logger.debug(FUNCTION_CALL_MSG)
        # Start by terminating any existing print process
        self.terminate_current_print_process()
        self.current_print_process = Process(
            target=self.io.stream_lines,
            kwargs={'lines': lines}
        )
        self.current_print_process.start()
        self.print_processes.append(self.current_print_process)

    def terminate_print_process(self, process):
        logger.debug(FUNCTION_CALL_MSG)
        # This lock is locked during each framebuffer print,
        # so this ensures we only kill print processes when
        # its safe to do so. An LCD is particularly sensitive
        # to being interrupted in the middle of a data stream,
        # other print methods might be too
        self.io.lock.acquire()
        logger.debug("Lock Acquired In Terminate Process")
        process.terminate()
        logger.debug("Blocking until print process dead")
        process.join()
        self.io.lock.release()
        logger.debug("Lock Released In Terminate Process")

    def terminate_current_print_process(self):
        logger.debug(FUNCTION_CALL_MSG)
        if self.current_print_process is not None:
            self.terminate_print_process(self.current_print_process)

    def print_processes_cleanup(self):
        logger.debug(FUNCTION_CALL_MSG)
        logger.debug(f"{len(self.print_processes)} threads to clean up")
        while len(self.print_processes) > 0:
            self.terminate_print_process(self.print_processes[0])
            self.print_processes.pop(0)

    def cleanup(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.terminate_current_print_process()
        self.print_processes_cleanup()
        self.io.lcd_cleanup()

    def back_button_press_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.io.back_button.latest_event = 'press'

    def back_button_hold_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        pressed_time = 0
        try:
            if self.io.back_button.latest_event:
                if self.io.back_button.latest_event == 'hold':
                    pressed_time = self.io.back_button.pressed_time
                    logger.debug(f"Hold After Hold (Back, {pressed_time} seconds) - No Action")
                    if self.io.back_button.is_long_hold_time():
                        self.io.back_button.hold_repeat = False
                        self.cleanup()
                        self.start_print_process(["Release To", "Shut Down"])
                        # self.io.shutdown_message()
                        # self.io.back_button.latest_event = 'long_hold'
                        # self.io.shutdown()

                if self.io.back_button.latest_event == 'release':
                    logger.debug("Hold After Release (Back) - No Action")

                if self.io.back_button.latest_event == 'press':
                    logger.debug("Hold After Press (Back) - Cleanup Processes")
                    # self.io.stream_lines(['Shutting Down', 'Byeee!'])
        finally:
            self.io.back_button.latest_event = 'hold'
            self.io.back_button.latest_hold_time = pressed_time

    def back_button_release_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        try:
            if self.io.back_button.latest_event:
                if self.io.back_button.latest_event == 'hold':
                    latest_hold_time = self.io.back_button.latest_hold_time
                    logger.debug(f"Release After Hold (Back, {latest_hold_time} seconds) - No Action")
                    if self.io.back_button.was_latest_hold_long():
                        self.cleanup()
                        self.start_print_process(["Byeeeee...", ""])
                        self.current_print_process.join()
                        self.io.shutdown()

                if self.io.back_button.latest_event == 'release':
                    logger.debug("Release After Release (Back) - No Action")

                if self.io.back_button.latest_event == 'press':
                    logger.debug("Release After Press (Back) - No Action")
        finally:
            self.io.back_button.latest_event = 'release'

    def front_button_press_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.io.front_button.latest_event = 'press'

    def front_button_hold_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        pressed_time = 0
        try:
            if self.io.front_button.latest_event:
                if self.io.front_button.latest_event == 'hold':
                    pressed_time = self.io.front_button.pressed_time
                    logger.debug(f"Hold After Hold (Front, {pressed_time} seconds) - No Action")
                    if self.io.front_button.is_long_hold_time():
                        self.io.front_button.hold_repeat = False
                        self.cleanup()
                        # self.start_print_process(["Release To", "Shut Down"])

                if self.io.front_button.latest_event == 'release':
                    logger.debug("Hold After Release (Front) - No Action")

                if self.io.front_button.latest_event == 'press':
                    logger.debug("Hold After Press (Front) - Cleanup Processes")
                    # self.start_print_process(self.instructions_lines())
                    # self.state = 'INSTRUCTIONS'
        finally:
            self.io.front_button.latest_event = 'hold'
            self.io.front_button.latest_hold_time = pressed_time

    def front_button_release_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        try:
            if self.io.front_button.latest_event:
                if self.io.front_button.latest_event == 'hold':
                    latest_hold_time = self.io.front_button.latest_hold_time
                    logger.debug(f"Release After Hold (Front, {latest_hold_time} seconds) - No Action")
                    if self.io.front_button.was_latest_hold_long():
                        self.io.front_button.hold_repeat = True
                        self.start_print_process(self.instructions_lines())
                        self.state = 'INSTRUCTIONS'

                if self.io.front_button.latest_event == 'release':
                    logger.debug("Release After Release - No Action")

                if self.io.front_button.latest_event == 'press':
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
            self.io.front_button.latest_event = 'release'
