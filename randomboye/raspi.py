from gpiozero import (
    Button,
    LED
)
from RPLCD.gpio import CharLCD
from RPi import GPIO
from definitions import FUNCTION_CALL_MSG
import os

from randomboye.io_device import IODevice

from logs.config import get_logger
logger = get_logger(__name__)


class RaspberryPi(IODevice):
    def __init__(self, shutdown_system=False, output_rows=2, output_columns=16):
        logger.debug(f"{FUNCTION_CALL_MSG}, {__class__}")
        super().__init__(shutdown_system=shutdown_system, output_rows=output_rows, output_columns=output_columns)
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
            cols=self.output_columns,
            rows=self.output_rows,
            pin_rs=37,
            pin_e=35,
            pins_data=self.pin_modes[self.bit_mode],
        )

        self.print_cleanup_method = self.print_cleanup_method_override
        self.print_method = self.print_method_override

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
        self.smiley = chr(0)

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

    def print_cleanup_method_override(self):
        logger.debug(FUNCTION_CALL_MSG)
        self.lock.acquire()
        self.lcd.home()
        self.lcd.clear()
        self.lock.release()

    def print_method_override(self, framebuffer):
        for row in framebuffer:
            try:
                self.lcd.write_string(row)
                self.lcd.crlf()
            except Exception as e:
                print("Something went wrong:")
                print(e)
                return

    def shutdown(self):
        logger.debug(FUNCTION_CALL_MSG)
        if self.shutdown_system:
            logger.debug("Shutting down system")
            self.back_led.on()
            os.system("sudo poweroff")
        else:
            raise NotImplementedError
            # logger.debug("Shutting down Pi process")
            # This throws some gpiozero related error on exit, but oh well
            # os.kill(self.pid, signal.SIGUSR1)

    # TODO: Keeping this around for the blinking logic that I need to reimplement
    # def shutdown_old(self, hold_time=6):
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
    #             raise NotImplementedError
    #             # logger.debug("Shutting down Pi process")
    #             # # This throws some gpiozero related error on exit, but oh well
    #             # os.kill(self.pid, signal.SIGUSR1)

    def default_splash_screen(self):
        lines = [f"{self.smiley*3}RASPBERRY{self.smiley*4}", f"{self.smiley*7}PI{self.smiley*7}"]
        self.stream_lines(lines)

    def default_startup_text(self):
        startup_steps_lines = [
            ['Loading', '.'],
            ['Loading', '..'],
            ['Loading', '...']
        ]
        self.stream_multiples_of_lines(startup_steps_lines)

    # TODO: Rename this
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
        self.print_cleanup_method()
        self.startup_method()
        super().run()


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
