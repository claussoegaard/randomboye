from gpiozero import (
    Button,
    LED
)
from RPLCD.gpio import CharLCD
from RPi import GPIO
from definitions import FUNCTION_CALL_MSG
import os
import signal
from multiprocessing import Process, Queue
from threading import Thread
import time
from randomboye.helpers import (
    # create_framebuffers,
    create_multiple_framebuffers
)

from logs.config import logger
logger = logger(__name__)


class RaspberryPi(Process):
    def __init__(self, shutdown_system=False):
        super().__init__()
        logger.debug(f"{FUNCTION_CALL_MSG}, {__class__}")
        GPIO.setwarnings(False)
        # self.daemon = False

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

        self.print_jobs = Queue()
        self.lcd_printer = self.LCDFramebufferPrinter(self)

    def print_framebuffers(self, framebuffers,
                           scroll_start_delay=3000, scroll_end_delay=2000, scroll_step_delay=400,
                           end_on_start=True, end_delay=0):
        """Takes N framebuffers and creates N or N+1 (depending on end_on_start)
        print jobs in the print_jobs queue
        """
        logger.debug(FUNCTION_CALL_MSG)
        if len(framebuffers) == 1:
            end_on_start = False
            scroll_start_delay = 0
        for i, framebuffer in enumerate(framebuffers):
            print_job_delay = 0
            if i == 0:
                print_job_delay = scroll_start_delay
            elif i == len(framebuffers) - 1:
                print_job_delay = scroll_end_delay
            else:
                print_job_delay = scroll_step_delay
            self.create_framebuffer_print_job(framebuffer, print_job_delay)
        if end_on_start:
            self.create_framebuffer_print_job(framebuffers[0], end_delay)

    def print_multiples_of_lines(self, lines_list,
                                 scroll_start_delay=3000, scroll_end_delay=2000, scroll_step_delay=400,
                                 end_on_start=True, end_delay=500):
        """
        lines = [line1, ..., lineN]
        ergo:
        lines_list = [[line1, ..., lineN], ..., [line1, ..., lineN]]
        For **each set** of lines in lines_list, will do the following:
        1. Create framebuffers for printing/streaming
        2. Print the first framebuffer then wait scroll_start_delay seconds
        3. Print the remaining framebuffers with a scroll_step_delay gap
        4. Wait scroll_end_delay after the last framebuffer
        5. If end_on_start==True it will then print the first framebuffer again
        Then after end_delay it will do the same for the next line in
        lines_list
        """
        logger.debug(FUNCTION_CALL_MSG)
        if len(lines_list) == 1:
            end_delay = 0
        multiple_framebuffers = create_multiple_framebuffers(lines_list)
        for framebuffers in multiple_framebuffers:
            self.print_framebuffers(
                framebuffers=framebuffers,
                scroll_start_delay=scroll_start_delay,
                scroll_end_delay=scroll_end_delay,
                scroll_step_delay=scroll_step_delay,
                end_on_start=end_on_start,
                end_delay=end_delay
            )

    def print_lines(self, lines,
                    scroll_start_delay=3000, scroll_end_delay=2000, scroll_step_delay=400,
                    end_on_start=True, end_delay=0):
        """
        Its not very intuitive to pass [[line1, ..., lineN]] to print_multiples_of_lines
        when you just want to write a single line, so this just wraps
        [line1, ..., lineN] in a list and passes to print_multiples_of_lines
        """
        lines_list = [lines]
        self.print_multiples_of_lines(
            lines_list=lines_list,
            scroll_start_delay=scroll_start_delay,
            scroll_end_delay=scroll_end_delay,
            scroll_step_delay=scroll_step_delay,
            end_delay=end_delay,
            end_on_start=end_on_start
        )

    # def shutdown2(self):
    #     logger.debug(FUNCTION_CALL_MSG)
    #     if self.shutdown_system:
    #         logger.debug("Shutting down system")
    #         self.back_led.on()
    #         os.system("sudo poweroff")
    #     else:
    #         logger.debug("Shutting down Pi process")
    #         # This throws some gpiozero related error on exit, but oh well
    #         os.kill(self.pid, signal.SIGUSR1)

    # def shutdown(self, hold_time=6):
    #     logger.debug(FUNCTION_CALL_MSG)
    #     # find how long the button has been held
    #     p = self.back_button.pressed_time
    #     logger.debug(f"Held for {p} seconds")
    #     # blink rate will increase the longer we hold
    #     # the button down. E.g., at 2 seconds, use 1/4 second rate.
    #     self.back_led.blink(on_time=0.5 / p, off_time=0.5 / p)
    #     if p > hold_time:
    #         # Depending on system, either shutdown
    #         # whole system, or just the object process
    #         if self.shutdown_system:
    #             logger.debug("Shutting down system")
    #             self.back_led.on()
    #             os.system("sudo poweroff")
    #         else:
    #             logger.debug("Shutting down Pi process")
    #             # This throws some gpiozero related error on exit, but oh well
    #             os.kill(self.pid, signal.SIGUSR1)

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
        # framebuffers = create_framebuffers(lines)
        # self.write_framebuffers(framebuffers)
        self.print_lines(lines)

    def default_startup_text(self):
        startup_steps_lines = [
            ['Loading', '.'],
            ['Loading', '..'],
            ['Loading', '...']
        ]
        self.print_multiples_of_lines(startup_steps_lines, end_delay=500)
        # for lines in startup_steps_lines:
        #     framebuffers = create_framebuffers(lines)
        #     logger.debug(framebuffers)
        #     self.write_framebuffers(framebuffers)
        #     time.sleep(0.5)

    def set_startup_method(self):
        self.default_startup_text()
        self.default_splash_screen()

    def create_framebuffer_print_job(self, framebuffer, delay=0):
        logger.debug(FUNCTION_CALL_MSG)
        print_job = (framebuffer, delay)
        self.print_jobs.put(print_job)
        logger.info(f"{print_job} added to print_queue")

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
        # self.lcd_cleanup()
        self.startup_method()
        self.lcd_printer.start()
        signal.pause()

    class LCDFramebufferPrinter(Thread):
        def __init__(self, pi):
            super().__init__()
            logger.debug(f"{FUNCTION_CALL_MSG}, {__class__}")
            self.pi = pi

        def validate_print_job(self, print_job):
            logger.debug(FUNCTION_CALL_MSG)
            if len(print_job) != 2 or not isinstance(print_job, tuple):
                raise ValueError(f"print_job must be tuple with 2 elements ({print_job})")
            if not isinstance(print_job[0], list):
                raise ValueError(f"1st element must be a list ({print_job})")
            if not isinstance(print_job[1], int):
                raise ValueError(f"2nd element must be an int ({print_job})")
            if len(print_job[0]) != self.pi.lcd_rows:
                raise ValueError(f"1st element must be list with {self.pi.lcd_rows} elements ({print_job})")
            if any([len(s) != self.pi.lcd_cols for s in print_job[0]]):
                raise ValueError(f"1st element must be list with only {self.pi.lcd_cols} long elements ({print_job})")
            logger.debug(f"{print_job} is valid print_job")

        def lcd_cleanup(self):
            logger.debug(FUNCTION_CALL_MSG)
            self.pi.lcd.home()
            self.pi.lcd.clear()

        def write_framebuffer(self, framebuffer):
            """Writes single framebuffer to LCD screen.
            Framebuffer must fill entire LCD screen.
            Valid framebuffer for 2x16 LCD:
            ["I Am A Raspberry", "Pi                "]
            No need to clear LCD since all cells will be overwritten
            """
            logger.debug(FUNCTION_CALL_MSG)
            self.pi.lcd.home()
            for row in framebuffer:
                try:
                    self.pi.lcd.write_string(row)
                    self.pi.lcd.crlf()
                except Exception as e:
                    print("Something went wrong:")
                    print(e)
                    return

        def run_print_job(self, print_job):
            logger.debug(FUNCTION_CALL_MSG)
            try:
                self.validate_print_job(print_job)
            except ValueError as e:
                logger.debug(e)
                return
            framebuffer, delay = print_job

            # If all framebuffers are blank
            if framebuffer == [" " * self.pi.lcd_cols] * self.pi.lcd_rows:
                self.lcd_cleanup()
            else:
                self.write_framebuffer(framebuffer)
            # Always sleeping for at least 0.1
            # to make sure data is done transmitting
            # to the LCD before next write.
            delay = max(delay, 100)
            delay_sec = delay / 1000
            time.sleep(delay_sec)

        def run(self):
            logger.debug(FUNCTION_CALL_MSG)
            while True:
                print_job = self.pi.print_jobs.get()
                self.run_print_job(print_job)


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
        # logger.debug(dir(self))

    def is_long_hold_time(self):
        return self.pressed_time > self.long_hold_time

    def was_latest_hold_long(self):
        return self.latest_hold_time > self.long_hold_time
