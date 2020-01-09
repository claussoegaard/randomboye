from gpiozero import (
    Button,
    LED
)
from signal import pause
from RPLCD.gpio import CharLCD
from RPi import GPIO
import time
# import os
# import warnings

import logging
from logging.config import dictConfig
from logging_config import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
FUNCTION_CALL_MSG = 'function_call'


class RaspberryPiIODiagnoser:
    def __init__(self):
        logger.debug(FUNCTION_CALL_MSG)
        GPIO.setwarnings(False)
        self.front_button_gpio = 4
        self.back_button_gpio = 3
        self.back_led_gpio = 14  # power LED
        self.bit_mode = 4
        self.pin_modes = {
            4: [33, 31, 29, 23],
            8: [40, 38, 36, 32, 33, 31, 29, 23]
        }

        self.lcd = CharLCD(
            numbering_mode=GPIO.BOARD,
            cols=16,
            rows=2,
            pin_rs=37,
            pin_e=35,
            pins_data=self.pin_modes[self.bit_mode]
        )

        self.front_button = Button(
            pin=self.front_button_gpio,
            # bounce_time=1,
            # hold_time=self.mintime,
            # hold_repeat=True
        )

        self.front_button.when_pressed = self.front_button__when_pressed
        self.front_button.when_held = self.front_button__when_held
        self.front_button.when_released = self.front_button__when_released

        self.back_button = Button(
            pin=self.back_button_gpio,
            # bounce_time=0.5,
            # hold_time=self.mintime,
            # hold_repeat=True
        )

        self.back_button.when_pressed = self.back_button__when_pressed
        self.back_button.when_held = self.back_button__when_held
        self.back_button.when_released = self.back_button__when_released

        self.back_led = LED(self.back_led_gpio)

        self.lcd.clear()
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
        self.lcd.cursor_pos = (1, 14)
        self.lcd.create_char(0, smiley)
        self.lcd.write_string(chr(0))

        pause()

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


"""
Times Front Button:
('04:55:34,118', '04:55:34,317'),
('04:55:55,979', '04:55:56,241'),
('04:58:49,928', '04:58:50,050'),
('04:59:12,629', '04:59:12,887'),
('04:59:40,564', '04:59:40,756'),
('05:00:00,903', '05:00:01,264'),
('05:00:19,886', '05:00:19,994')

('04:57:40,652', '04:57:40,745') --No bug
('04:58:10,908', '04:58:11,013') --No bug

('', '')
('', '')
('', '')
('', '')
('', '')
"""
