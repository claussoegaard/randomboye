from definitions import FUNCTION_CALL_MSG
import signal
from unittest.mock import Mock
from threading import Thread
import time
from randomboye.helpers import (
    create_multiple_framebuffers
)
from threading import Lock, Event

from logs.config import get_logger
logger = get_logger(__name__)


class IODevice(Thread):
    def __init__(self, shutdown_system=False, output_rows=2, output_columns=16):
        super().__init__()
        logger.debug(f"{FUNCTION_CALL_MSG}, {__class__}")

        self.shutdown_system = shutdown_system

        self.lock = Lock()

        self.done_printing = Event()
        self.done_printing.set()

        self.output_rows = output_rows
        self.output_columns = output_columns

        # Override
        self.print_method = self.default_print_method
        self.print_cleanup_method = self.default_print_cleanup

        # Override these with Button in Raspberry Pi class, and
        # whatever other mechanism for triggering events you
        # have in other test setups
        self.front_button = Mock()
        self.front_button.when_pressed = self.front_button__when_pressed
        self.front_button.when_held = self.front_button__when_held
        self.front_button.when_released = self.front_button__when_released

        self.back_button = Mock()
        self.back_button.when_pressed = self.back_button__when_pressed
        self.back_button.when_held = self.back_button__when_held
        self.back_button.when_released = self.back_button__when_released

        self.startup_method = self.default_startup_method

    def default_print_cleanup(self):
        logger.debug(FUNCTION_CALL_MSG)
        pass

    def default_print_method(self, framebuffer):
        logger.debug(FUNCTION_CALL_MSG)
        for row in framebuffer:
            print(row)

    def default_startup_method(self):
        logger.debug(FUNCTION_CALL_MSG)

    def shutdown(self):
        logger.debug(FUNCTION_CALL_MSG)
        raise NotImplementedError

    def print_framebuffer(self, framebuffer):
        """Inheriting classes should/could call super().print_framebuffer first
        to get these validations for free.
        After that, each inheriting class should implement its own print
        functionality. Whether an LCD screen on a Raspberry Pi, some curses
        app, maybe pygame, maybe just simple print(), etc.
        """
        logger.debug(FUNCTION_CALL_MSG)
        logger.debug(f"Doing checks on {framebuffer}")
        if len(framebuffer) != self.output_rows:
            error = f"framebuffer must have exactly {self.output_rows} rows, has {len(framebuffer)}"
            raise ValueError(error)
        if not all([len(row) == self.output_columns and isinstance(row, str) for row in framebuffer]):
            error = f"all rows in framebuffer must be strings, exactly {self.output_columns} characters long"
            raise ValueError(error)
        logger.debug(f"About to print {framebuffer}")
        self.lock.acquire()
        logger.debug("Lock acquired in print_framebuffer")
        self.print_method(framebuffer)
        self.lock.release()
        logger.debug("Lock released in print_framebuffer")

    def print_framebuffers(self, framebuffers,
                           start_delay=3, end_delay=2, scroll_delay=0.4,
                           end_on_start=True):
        """
        """
        self.print_cleanup_method()
        # Overriding stuff if framebuffers only has one frame
        if len(framebuffers) == 1:
            end_on_start = False
            start_delay = 0
        for i, framebuffer in enumerate(framebuffers):
            self.print_framebuffer(framebuffer)
            if i == 0:
                time.sleep(start_delay)
            elif i == len(framebuffers) - 1:
                time.sleep(end_delay)
            else:
                time.sleep(scroll_delay)
        if end_on_start:
            self.print_framebuffer(framebuffers[0])

    def stream_multiples_of_lines(self, lines_list,
                                  start_delay=3, end_delay=2, scroll_delay=0.4,
                                  lines_delay=0.5, end_on_start=True):
        """
        lines = [line1, ..., lineN]
        ergo:
        lines_list = [[line1, ..., lineN], ..., [line1, ..., lineN]]
        For each set of lines in lines_list, will do the following:
        1. Create framebuffers for streaming
        2. Write the first framebuffer then wait start_delay seconds
        3. Write the remaining framebuffers with a scroll_delay gap
        4. Wait end_delay at the last framebuffer
        5. If end_on_start==True it will then write the first framebuffer again
        Then after lines_delay it will do the same for the next line in
        lines_list
        """
        logger.debug(FUNCTION_CALL_MSG)
        # All print calls go through this method, so setting flag here only
        self.done_printing.clear()
        if len(lines_list) == 1:
            lines_delay = 0
        multiple_framebuffers = create_multiple_framebuffers(lines_list)
        for framebuffers in multiple_framebuffers:
            self.print_framebuffers(
                framebuffers=framebuffers,
                start_delay=start_delay,
                end_delay=end_delay,
                scroll_delay=scroll_delay,
                end_on_start=end_on_start
            )
            time.sleep(lines_delay)
        self.done_printing.set()

    def stream_lines(self, lines,
                     start_delay=3, end_delay=2, scroll_delay=0.4,
                     lines_delay=0.5, end_on_start=True):
        """
        Its not very intuitive to pass [[line1, ..., lineN]] to stream_multiples_of_lines
        when you just want to write a single line, so this just wraps
        [line1, ..., lineN] in a list and passes to stream_multiples_of_lines
        """
        lines_list = [lines]
        self.stream_multiples_of_lines(
            lines_list=lines_list,
            start_delay=start_delay,
            end_delay=end_delay,
            scroll_delay=scroll_delay,
            lines_delay=0,
            end_on_start=end_on_start
        )

    def front_button__when_pressed(self):
        logger.debug(FUNCTION_CALL_MSG)

    def front_button__when_held(self):
        logger.debug(FUNCTION_CALL_MSG)

    def front_button__when_released(self):
        logger.debug(FUNCTION_CALL_MSG)

    def back_button__when_pressed(self):
        logger.debug(FUNCTION_CALL_MSG)

    def back_button__when_held(self):
        logger.debug(FUNCTION_CALL_MSG)

    def back_button__when_released(self):
        logger.debug(FUNCTION_CALL_MSG)

    def run(self):
        signal.pause()
