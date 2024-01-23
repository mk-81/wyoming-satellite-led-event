import abc

class AbstractLedController:
    def __init__(self) -> None:
        self.num_led = None

    def cleanup(self):
        pass

    @abc.abstractmethod
    def set_led_color(self, led_num, red, green, blue, bright_percent=100):
        pass

    @abc.abstractmethod
    def show(self):
        pass