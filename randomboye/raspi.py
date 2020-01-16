from gpiozero import (
    Button,
    LED
)
from RPLCD.gpio import CharLCD
from RPi import GPIO
from definitions import FUNCTION_CALL_MSG
import os
import signal
from multiprocessing import Process
import time
from randomboye.helpers import create_framebuffers

from logs.config import logger
logger = logger(__name__)


class RaspberryPi(Process):
    def __init__(self):
        super().__init__()
        logger.debug(f"{FUNCTION_CALL_MSG}, {__class__}")
        GPIO.setwarnings(False)
        # self.run = True
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
            auto_linebreaks=False
        )

        self.front_button = Button(
            pin=self.front_button_gpio,
            bounce_time=0.01,
            hold_time=1,
            # hold_repeat=True
        )

        # self.front_button.start()

        self.front_button.when_pressed = self.front_button__when_pressed
        self.front_button.when_held = self.front_button__when_held
        self.front_button.when_released = self.front_button__when_released

        self.back_button = Button(
            pin=self.back_button_gpio,
            bounce_time=0.01,
            hold_time=1,
            # hold_repeat=True
        )

        # self.back_button.start()

        self.back_button.when_pressed = self.back_button__when_pressed
        self.back_button.when_held = self.back_button__when_held
        self.back_button.when_released = self.back_button__when_released

        self.back_led = LED(self.back_led_gpio)

        self.lcd.clear()
        # self.lcd.home()

        self.default_startup_text()
        # self.daemon = True

        # if self.run:
        # signal.pause()

    def shutdown(self, hold_time=6):
        # find how long the button has been held
        p = self.back_button.pressed_time
        # blink rate will increase the longer we hold
        # the button down. E.g., at 2 seconds, use 1/4 second rate.
        self.back_led.blink(on_time=0.5 / p, off_time=0.5 / p)
        if p > hold_time:
            self.lcd.clear()
            self.lcd.write_string('Byeeee')
            self.led.on()
            os.system("sudo poweroff")

    def write_framebuffer(self, framebuffer):
        """Writes single framebuffer to LCD screen.
        Framebuffer must fill entire LCD screen.
        Valid framebuffer for 2x16 LCD:
        ["I Am A Raspberry", "Pi                "]
        No need to clear LCD since all cells will be overwritten
        """
        if len(framebuffer) != self.lcd_rows:
            error = f"framebuffer must have exactly {self.lcd_rows} rows, has {len(framebuffer)}"
            raise ValueError(error)
        if not all([len(row) == self.lcd_cols and isinstance(row, str) for row in framebuffer]):
            logger.debug(framebuffer)
            error = f"all rows in framebuffer must be strings, exactly {self.lcd_cols} characters long"
            raise ValueError(error)
        self.lcd.home()
        for row in framebuffer:
            try:
                self.lcd.write_string(row)
                # self.lcd.write_string(row.ljust(self.lcd.cols)[:self.lcd.cols])
                self.lcd.crlf()
            except Exception as e:
                print("Something went wrong:")
                print(e)
                return

    def write_framebuffers(self, framebuffers, start_delay=3, end_delay=2, scroll_delay=0.4):
        """Writes N framebuffers to LCD screen.
        If len(framebuffers) > 1 it will first delay scrolling by start_delay,
        then it will progress through framebuffers at scroll_delay speed,
        until it reaches the end, where it will pause for end_delay time.
        See write_framebuffer() for details on valid framebuffers.
        Up to caller to implement a loop if desired, and to construct
        valid framebuffers.
        """
        for i, framebuffer in enumerate(framebuffers):
            self.write_framebuffer(framebuffer)
            if i == 0:
                time.sleep(start_delay)
            elif i == len(framebuffers) - 1:
                time.sleep(end_delay)
            else:
                time.sleep(scroll_delay)
                # ['Loading         ']
                # ['.               ']
        # self.write_framebuffer(framebuffers[0])

    # def default_startup_framebuffers(self):
    #     self.lcd.home()
    #     smiley = (
    #         0b00000,
    #         0b01010,
    #         0b01010,
    #         0b00000,
    #         0b10001,
    #         0b10001,
    #         0b01110,
    #         0b00000,
    #     )
    #     self.lcd.create_char(0, smiley)
    #     s = chr(0)
    #     line1 = f"{s*3}RASPBERRY{s*4}"
    #     line2 = f"{s*7}PI{s*7}"
    #     return [line1, line2]

    def default_startup_text(self):
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
        startup_steps_lines = [
            ['Loading', '.'],
            ['Loading', '..'],
            ['Loading', '...'],
            [f"{s*3}RASPBERRY{s*4}", f"{s*7}PI{s*7}"]
        ]
        for lines in startup_steps_lines:
            framebuffers = create_framebuffers(lines)[0]
            self.write_framebuffer(framebuffers)
            time.sleep(0.5)
            #     framebuffers = create_framebuffers(lines) for lines in startup_steps_lines
            #     self.write_framebuffers(framebuffers)
            # framebuffers = [create_framebuffers(lines) for lines in startup_steps_lines]
            # logger.debug(framebuffers)
            # framebuffers = create_framebuffers(lines)
        # self.write_framebuffers(framebuffers)

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
        os.kill(self.pid, signal.SIGUSR1)
        # self.run = False
        # self.shutdown()
        # raise SystemExit
        # signal.SIG_DFL

    def back_button__when_released(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.back_led.off()

    def run(self):
        signal.pause()
