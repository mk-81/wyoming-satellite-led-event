import asyncio
from ..base import GenericLedPattern

_BLACK   = (0, 0, 0)
_BLUE   = (0, 0, 255)
_RED    = (60, 0, 0)
_YELLOW = (255, 255, 0)
_WHITE  = (255, 255, 255)

class LedPattern(GenericLedPattern):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._active = False;

    def color(self, red, green, blue, brightness = 100, show=True) -> None:
        for i in range(self.led_controller.num_led):
            self.led_controller.set_led_color(i, red, green, blue, brightness)

        if show:
            self.led_controller.show()

    async def client_connected(self) -> None:
        self.color(*_WHITE, 80)
        await asyncio.sleep(0.5)
        await self.stop()


    async def idle(self) -> None:
        # no idle
        active = self._active
        self._active = False
        if active:
            await self.stop()
        else:
            self.color(*_BLACK)



    async def stop(self) -> None:
        self._active = False
        for i in range(int(round(self.led_controller.num_led / 2)) + 1):
            self.led_controller.set_led_color(i, *_BLACK)
            self.led_controller.set_led_color(self.led_controller.num_led - i, *_BLACK)

            self.led_controller.show()
            await asyncio.sleep(0.02)



    async def wakeup(self) -> None:
        self._active = True

        brightness = 50
        for i in range(int(round(self.led_controller.num_led / 2)) + 1):
            brightness += 5
            self.led_controller.set_led_color(i, *_WHITE, brightness)
            if i > 0:
                self.led_controller.set_led_color(self.led_controller.num_led - i,  *_WHITE, brightness)

            if i > 1:
                self.led_controller.set_led_color(i - 2, *_BLUE, brightness)
                if i > 2:
                    self.led_controller.set_led_color(self.led_controller.num_led - i + 2, *_BLUE, brightness)

            self.led_controller.show()
            await asyncio.sleep(0.02)

        await asyncio.sleep(0.5)


    async def listen(self) -> None:
        pass


    async def think(self) -> None:
        self._active = True

        first = _BLUE
        second = _WHITE

        while not self.has_pending_event():
            for i in range(1, self.led_controller.num_led + 1):
                if self.has_pending_event():
                    break

                if i % 2 == 0:
                    self.led_controller.set_led_color(i - 1, *first)
                else:
                    self.led_controller.set_led_color(i - 1, *second)

            self.led_controller.show()

            if first == _BLUE:
                first = _WHITE
                second = _BLUE
            else:
                first = _BLUE
                second = _WHITE

            await asyncio.sleep(0.15)


    async def speak(self) -> None:
        self._active = True

        direction = 1
        red = 255
        green = 255

        self.color(*_WHITE, show=False)

        while not self.has_pending_event():
            self.color(red=red, green=green, blue=255)

            red -= direction
            green -= direction
            if red >= 255 or red <= 0:
                direction *= -1

            await asyncio.sleep(0.002)


    async def error(self) -> None:
        for _ in range(3):
            self.color(*_RED)
            await asyncio.sleep(0.3)
            self.color(*_BLACK)
            await asyncio.sleep(0.3)
        self.color(*_RED) # "off" Animation from red not black
        await self.stop()

    async def disconnected(self) -> None:
        step = 1
        max_brightness = 40
        min_brightness = 2

        brightness = max_brightness

        while not self.has_pending_event():
            self.color(*_RED, brightness)
            if brightness <= min_brightness or brightness >= max_brightness:
                step = step * -1

            brightness += step
            await asyncio.sleep(0.04)
