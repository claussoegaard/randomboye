from gpiozero import (
    Button,
    LED
)
from signal import pause
# from RPLCD.gpio import CharLCD
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
        self.pin_modes = {
            4: [33, 31, 29, 23],
            8: [40, 38, 36, 32, 33, 31, 29, 23]
        }

        self.front_button = Button(
            self.front_button_gpio,
            # hold_time=self.mintime,
            # hold_repeat=True
        )

        self.front_button.when_pressed = self.front_button__when_pressed
        self.front_button.when_held = self.front_button__when_held
        self.front_button.when_released = self.front_button__when_released

        self.back_button = Button(
            self.back_button_gpio,
            # hold_time=self.mintime,
            # hold_repeat=True
        )

        self.back_button.when_pressed = self.back_button__when_pressed
        self.back_button.when_held = self.back_button__when_held
        self.back_button.when_released = self.back_button__when_released

        self.back_led = LED(self.back_led_gpio)

        pause()

    def front_button__when_pressed(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.front_button.last_pressed = time.time()

    def front_button__when_held(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.front_button.last_held = time.time()

    def front_button__when_released(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.front_button.last_released = time.time()

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
