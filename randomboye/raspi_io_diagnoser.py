from gpiozero import (
    Button,
    LED
)
# from RPLCD.gpio import CharLCD
from RPi import GPIO
# import time
# import os
# import warnings

import logging
from logging.config import dictConfig
from logging_config import LOGGING_CONFIG

dictConfig(LOGGING_CONFIG)
logger = logging.getLogger(__name__)
FUNCTION_CALL_MSG = 'function_call'


class RaspberryPiDiagnoser:
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
            hold_repeat=True
        )

        self.front_button.when_pressed = logger.debug("Front Button Pressed")

        self.back_button = Button(
            self.back_button_gpio,
            # hold_time=self.mintime,
            hold_repeat=True
        )

        self.back_led = LED(self.back_led_gpio)

    def bogus(self):
        logger.debug(FUNCTION_CALL_MSG)
        return "bogus"
