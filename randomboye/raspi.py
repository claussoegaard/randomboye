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

        self.write_framebuffer(self.default_startup_framebuffer())

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
        # Framebuffer must fill entire LCD screen.
        # Valid framebuffer for 2x16 LCD:
        # [["I Am A Raspberry"], ["Pi                "]]
        # No need to clear LCD since all cells will be overwritten
        if len(framebuffer) != self.lcd_rows:
            raise ValueError(f"framebuffer must have exactly {self.lcd_rows} rows")
        if not all([len(row) == self.lcd_cols and isinstance(row, str) for row in framebuffer]):
            raise ValueError(f"all rows in framebuffer must be strings, exactly {self.lcd_cols} characters long")
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

    def default_startup_framebuffer(self):
        self.lcd.home()
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
        line1 = f"{s*3}RASPBERRY{s*4}"
        line2 = f"{s*7}PI{s*7}"
        return [line1, line2]

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
        # self.run = False
        # self.shutdown()
        # raise SystemExit
        # signal.SIG_DFL

    def back_button__when_released(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.back_led.off()

    def run(self):
        signal.pause()
