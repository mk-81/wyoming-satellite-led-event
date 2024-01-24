from ..base import AbstractLedController

NUM_LEDS = 12

_BLACK = (0,0,0,0)

class LedController(AbstractLedController):
    def __init__(self):
        super().__init__()
        self.num_led = NUM_LEDS
        self._color = list()
        for _ in range(self.num_led):
            self._color.append(_BLACK)


    def set_led_color(self, led_num, red, green, blue, bright_percent=100):
        if led_num < 0 or led_num >= self.num_led:
            return
        
        self._color[led_num] = (red, green, blue, bright_percent)

    def show(self):
        print(self._color)

    def cleanup(self):
        self._color = None
        super().cleanup()
