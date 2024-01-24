from ..base import AbstractLedController

import gpiozero
from .apa102 import APA102

NUM_LEDS = 12
LEDS_GPIO = 5

class LedController(AbstractLedController):
    def __init__(self):
        super().__init__()
        self.num_led = NUM_LEDS
        self.__led_power = gpiozero.LED(LEDS_GPIO, active_high=True)
        self.__led_power.on()
        self.__apa102 = APA102(num_led=NUM_LEDS)


    def set_led_color(self, led_num, red, green, blue, bright_percent=100):
        self.__apa102.set_pixel(led_num, red, green, blue, bright_percent)


    def show(self):
        self.__apa102.show()


    def cleanup(self):
        self.__apa102.cleanup()
        self.__led_power.off()
        super().cleanup()
