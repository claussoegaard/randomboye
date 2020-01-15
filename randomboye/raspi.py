from gpiozero import (
    Button,
    LED
)
from RPLCD.gpio import CharLCD
from RPi import GPIO
from definitions import FUNCTION_CALL_MSG
import os
from signal import pause
import threading

from logs.config import logger
logger = logger(__name__)


class RaspberryPi(object):
    def __init__(self):
        super().__init__()
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

        self.front_button = PiButton(
            pin=self.front_button_gpio,
            bounce_time=0.01,
            hold_time=1,
            # hold_repeat=True
        )

        self.front_button.start()

        # self.front_button.when_pressed = self.front_button__when_pressed
        # self.front_button.when_held = self.front_button__when_held
        # self.front_button.when_released = self.front_button__when_released

        self.back_button = PiButton(
            pin=self.back_button_gpio,
            bounce_time=0.01,
            hold_time=1,
            # hold_repeat=True
        )

        self.back_button.start()

        # self.back_button.when_pressed = self.back_button__when_pressed
        # self.back_button.when_held = self.back_button__when_held
        # self.back_button.when_released = self.back_button__when_released

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

        self.lcd.create_char(0, smiley)

        s = chr(0)

        line1 = f"{s*3}RASPBERRY{s*4}"
        line2 = f"{s*7}PI{s*7}"

        self.lcd.cursor_pos = (0, 0)
        self.lcd.write_string(line1)
        self.lcd.cursor_pos = (1, 0)
        self.lcd.write_string(line2)

        # pause()

    # def shutdown(self, hold_time=6):
    #     # find how long the button has been held
    #     p = self.back_button.pressed_time
    #     # blink rate will increase the longer we hold
    #     # the button down. E.g., at 2 seconds, use 1/4 second rate.
    #     self.back_led.blink(on_time=0.5 / p, off_time=0.5 / p)
    #     if p > hold_time:
    #         self.lcd.clear()
    #         self.lcd.write_string('Byeeee')
    #         self.led.on()
    #         os.system("sudo poweroff")

    # def front_button__when_pressed(self):
    #     logger.debug(FUNCTION_CALL_MSG)

    # def front_button__when_held(self):
    #     logger.debug(FUNCTION_CALL_MSG)

    # def front_button__when_released(self):
    #     logger.debug(FUNCTION_CALL_MSG)

    # def back_button__when_pressed(self):
    #     logger.debug(FUNCTION_CALL_MSG)

    # def back_button__when_held(self):
    #     logger.debug(FUNCTION_CALL_MSG)
    #     # self.shutdown()

    # def back_button__when_released(self):
    #     logger.debug(FUNCTION_CALL_MSG)
        # self.back_led.off()


class PiButton(Button, threading.Thread):
    def __init__(self, pin, bounce_time, hold_time):
        logger.debug(FUNCTION_CALL_MSG)
        super().__init__(pin=pin, bounce_time=bounce_time, hold_time=hold_time)
        self.press_event = threading.Event()
        self.hold_event = threading.Event()
        self.release_event = threading.Event()
        self.when_pressed = self.set_press_event
        self.when_held = self.set_hold_event
        self.when_released = self.set_release_event

    def set_press_event(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.press_event.set()

    def set_hold_event(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.hold_event.set()

    def set_release_event(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.release_event.set()

    def press_action(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.press_event.wait()
        logger.debug("Pressed")

    def hold_action(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.hold_event.wait()
        self.press_event.clear()
        logger.debug("Held")

    def release_action(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.release_event.wait()
        self.hold_event.clear()
        self.release_event.clear()
        logger.debug("Released")

    def run(self):
        threading.Thread(name='press', target=self.press_action)
        threading.Thread(name='hold', target=self.hold_action)
        threading.Thread(name='release', target=self.release_action)


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
