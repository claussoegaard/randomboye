from gpiozero import (
    Button,
    LED
)
from RPLCD.gpio import CharLCD
from RPi import GPIO
from definitions import FUNCTION_CALL_MSG
import os
import signal
from multiprocessing import Process, Lock
import time
from randomboye.helpers import (
    create_multiple_framebuffers
)

from logs.config import get_logger
logger = get_logger(__name__)


class RaspberryPi(Process):
    def __init__(self, shutdown_system=False):
        super().__init__()
        logger.debug(f"{FUNCTION_CALL_MSG}, {__class__}")
        GPIO.setwarnings(False)
        self.lock = Lock()

        self.shutdown_system = shutdown_system
        self.front_button_gpio = 4
        self.back_button_gpio = 3
        self.back_led_gpio = 14  # power LED
        self.bit_mode = 4
        self.pin_modes = {
            4: [33, 31, 29, 23],
            8: [40, 38, 36, 32, 33, 31, 29, 23]
        }

        self.lcd_rows = 2
        self.lcd_cols = 16

        self.lcd = CharLCD(
            numbering_mode=GPIO.BOARD,
            cols=self.lcd_cols,
            rows=self.lcd_rows,
            pin_rs=37,
            pin_e=35,
            pins_data=self.pin_modes[self.bit_mode],
        )

        self.lcd_cleanup()

        self.front_button = ButtonWrapper(
            pin=self.front_button_gpio,
            bounce_time=0.01,
            hold_time=1,
            hold_repeat=True
        )

        self.front_button.when_pressed = self.front_button__when_pressed
        self.front_button.when_held = self.front_button__when_held
        self.front_button.when_released = self.front_button__when_released

        self.back_button = ButtonWrapper(
            pin=self.back_button_gpio,
            bounce_time=0.01,
            hold_time=1,
            hold_repeat=True
        )

        self.back_button.when_pressed = self.back_button__when_pressed
        self.back_button.when_held = self.back_button__when_held
        self.back_button.when_released = self.back_button__when_released

        self.back_led = LED(self.back_led_gpio)

        self.startup_method = self.set_startup_method

    def lcd_cleanup(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.lcd.home()
        self.lcd.clear()

    def shutdown2(self):
        logger.debug(FUNCTION_CALL_MSG)
        if self.shutdown_system:
            logger.debug("Shutting down system")
            self.back_led.on()
            os.system("sudo poweroff")
        else:
            logger.debug("Shutting down Pi process")
            # This throws some gpiozero related error on exit, but oh well
            os.kill(self.pid, signal.SIGUSR1)

    def shutdown(self, hold_time=6):
        logger.debug(FUNCTION_CALL_MSG)
        # find how long the button has been held
        p = self.back_button.pressed_time
        logger.debug(f"Held for {p} seconds")
        # blink rate will increase the longer we hold
        # the button down. E.g., at 2 seconds, use 1/4 second rate.
        self.back_led.blink(on_time=0.5 / p, off_time=0.5 / p)
        if p > hold_time:
            # Depending on system, either shutdown
            # whole system, or just the object process
            if self.shutdown_system:
                logger.debug("Shutting down system")
                self.back_led.on()
                os.system("sudo poweroff")
            else:
                logger.debug("Shutting down Pi process")
                # This throws some gpiozero related error on exit, but oh well
                os.kill(self.pid, signal.SIGUSR1)

    def write_framebuffer(self, framebuffer):
        """Writes single framebuffer to LCD screen.
        Framebuffer must fill entire LCD screen.
        Valid framebuffer for 2x16 LCD:
        ["I Am A Raspberry", "Pi                "]
        No need to clear LCD since all cells will be overwritten
        """
        logger.debug(FUNCTION_CALL_MSG)
        self.lock.acquire()
        logger.debug("Lock Acquired")
        if len(framebuffer) != self.lcd_rows:
            error = f"framebuffer must have exactly {self.lcd_rows} rows, has {len(framebuffer)}"
            raise ValueError(error)
        if not all([len(row) == self.lcd_cols and isinstance(row, str) for row in framebuffer]):
            logger.debug(framebuffer)
            error = f"all rows in framebuffer must be strings, exactly {self.lcd_cols} characters long"
            raise ValueError(error)
        self.lcd.home()
        logger.debug(f"Start Printing {framebuffer}")
        for row in framebuffer:
            try:
                self.lcd.write_string(row)
                self.lcd.crlf()
            except Exception as e:
                print("Something went wrong:")
                print(e)
                return
        self.lock.release()
        logger.debug("Lock Released")

    def write_framebuffers(self, framebuffers,
                           start_delay=3, end_delay=2, scroll_delay=0.4,
                           end_on_start=True):
        """Writes N framebuffers to LCD screen.
        If len(framebuffers) > 1 it will first delay scrolling by start_delay,
        then it will progress through framebuffers at scroll_delay speed,
        until it reaches the end, where it will pause for end_delay time.
        See write_framebuffer() for details on valid framebuffers.
        Up to caller to implement a loop if desired, and to construct
        valid framebuffers.
        """
        logger.debug(FUNCTION_CALL_MSG)

        # Overriding stuff if framebuffers only has one frame
        if len(framebuffers) == 1:
            end_on_start = False
            start_delay = 0
        for i, framebuffer in enumerate(framebuffers):
            self.write_framebuffer(framebuffer)
            if i == 0:
                time.sleep(start_delay)
            elif i == len(framebuffers) - 1:
                time.sleep(end_delay)
            else:
                time.sleep(scroll_delay)
        if end_on_start:
            self.write_framebuffer(framebuffers[0])

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
        self.lcd_cleanup()
        logger.debug(FUNCTION_CALL_MSG)
        if len(lines_list) == 1:
            lines_delay = 0
        multiple_framebuffers = create_multiple_framebuffers(lines_list)
        for framebuffers in multiple_framebuffers:
            self.write_framebuffers(
                framebuffers=framebuffers,
                start_delay=start_delay,
                end_delay=end_delay,
                scroll_delay=scroll_delay,
                end_on_start=end_on_start
            )
            time.sleep(lines_delay)

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

    def default_splash_screen(self):
        smiley = (
            0b00000,
            0b01010,
            0b01010,
            0b00000,
            0b10001,
            0b10001,
            0b01110,
            0b00000,
        )
        self.lcd.create_char(0, smiley)
        s = chr(0)
        lines = [f"{s*3}RASPBERRY{s*4}", f"{s*7}PI{s*7}"]
        self.stream_lines(lines)

    def default_startup_text(self):
        startup_steps_lines = [
            ['Loading', '.'],
            ['Loading', '..'],
            ['Loading', '...']
        ]
        self.stream_multiples_of_lines(startup_steps_lines)

    def set_startup_method(self):
        self.default_startup_text()
        self.default_splash_screen()

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
        self.back_led.off()

    def run(self):
        self.lcd_cleanup()
        self.startup_method()
        signal.pause()


class ButtonWrapper(Button):
    """Only making this wrapper to enable additional attributes
    on Button
    """

    def __init__(self, pin, bounce_time, hold_time, hold_repeat=False, long_hold_time=6):
        logger.debug(f"{FUNCTION_CALL_MSG}, {__class__}")
        super().__init__(pin=pin, bounce_time=bounce_time, hold_time=hold_time, hold_repeat=hold_repeat)
        self.latest_event = None
        self.latest_hold_time = 0
        self.long_hold_time = long_hold_time

    def is_long_hold_time(self):
        return self.pressed_time > self.long_hold_time

    def was_latest_hold_long(self):
        return self.latest_hold_time > self.long_hold_time
