from randomboye.io_device import IODevice

from logs.config import get_logger
logger = get_logger(__name__)


class RaspberryPiDefaultTest(IODevice):
    def __init__(self, shutdown_system=False, output_rows=2, output_columns=16):
        super().__init__(shutdown_system=shutdown_system, output_rows=output_rows, output_columns=output_columns)

        self.front_button = TestButton(
            press_key='a',
            hold_key='s',
            release_key='d'
        )

        self.back_button = TestButton(
            press_key='q',
            hold_key='w',
            release_key='e'
        )

        self.startup_method = self.default_startup_method

        self.smiley = 'ツ'

    def button_press_handler(self, input):

        if len(input) != 1:
            raise ValueError("Must be exactly 1 long")
        if input not in self.front_button.get_keys() + self.back_button.get_keys():
            raise ValueError(f"Input must be in {self.front_button.get_keys() + self.back_button.get_keys()}")

        button = None
        if input in self.front_button.get_keys():
            button = self.front_button
        elif input in self.back_button.get_keys():
            button = self.back_button
        button.fire_action(input)

    def default_startup_method(self):
        logger.debug("Starting Up")

    def run(self):
        self.print_cleanup_method()
        self.startup_method()
        while True:
            self.done_printing.wait()
            # self.done_printing.clear()
            # self.lock.acquire()
            print("Randomboye")
            print("a, s or d for press, hold, release on front button")
            print("q, w or e for press, hold, release on back button")
            try:
                bp = input("'Button': ")
                self.button_press_handler(bp)
            except ValueError:
                logger.exception("Caught input exception")
                logger.debug("Try Again")
            # self.lock.release()


class TestButton(object):
    def __init__(self, press_key, hold_key, release_key, long_hold_time=6):
        super().__init__()
        self.press_key = press_key
        self.hold_key = hold_key
        self.release_key = release_key
        self.when_pressed = None
        self.when_held = None
        self.when_released = None
        self.latest_event = None
        self.long_hold_time = long_hold_time

    def get_keys(self):
        return (self.press_key, self.hold_key, self.release_key)

    def _fire_when_pressed(self):
        self.when_pressed()

    def _fire_when_held(self):
        self.when_held()

    def _fire_when_released(self):
        self.when_released()

    def fire_action(self, key):
        if key == self.press_key:
            self._fire_when_pressed()
        elif key == self.hold_key:
            self._fire_when_held()
        elif key == self.release_key:
            self._fire_when_released()

    def is_long_hold_time(self):
        return self.pressed_time > self.long_hold_time

    def was_latest_hold_long(self):
        return self.latest_hold_time > self.long_hold_time
