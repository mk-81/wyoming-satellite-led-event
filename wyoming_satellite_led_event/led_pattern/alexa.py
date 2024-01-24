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
        middle = int(round(self.led_controller.num_led / 2))
        for i in range(middle):
            self.led_controller.set_led_color(middle - i - 1, *_BLACK)
            self.led_controller.set_led_color(middle + i,     *_BLACK)

            self.led_controller.show()
            await asyncio.sleep(0.02)

#        for i in range(int(round(self.led_controller.num_led / 2)) + 1):
#            self.led_controller.set_led_color(i, *_BLACK)
#            self.led_controller.set_led_color(self.led_controller.num_led - i, *_BLACK)
#
#            self.led_controller.show()
#            await asyncio.sleep(0.02)


    async def wakeup(self) -> None:
        self._active = True

        steps = int(round(self.led_controller.num_led / 2))
        brightness_stepwidth = int(round(50/steps))
        brightness = max(100 - brightness_stepwidth * steps, 0)

        for i in range(steps):
            brightness = min(brightness + brightness_stepwidth, 100)
            self.led_controller.set_led_color(i, *_WHITE, brightness)
            self.led_controller.set_led_color(self.led_controller.num_led - i - 1,  *_WHITE, brightness)

            if i >= 1:
                self.led_controller.set_led_color(i - 1, *_BLUE, brightness)
                self.led_controller.set_led_color(self.led_controller.num_led - i, *_BLUE, brightness)

            self.led_controller.show()
            await asyncio.sleep(0.02)


#        brightness = 50
#        for i in range(int(round(self.led_controller.num_led / 2)) + 1):
#            brightness += 5
#            self.led_controller.set_led_color(i, *_WHITE, brightness)
#            if i > 0:
#                self.led_controller.set_led_color(self.led_controller.num_led - i,  *_WHITE, brightness)
#
#            if i > 1:
#                self.led_controller.set_led_color(i - 2, *_BLUE, brightness)
#                if i > 2:
#                    self.led_controller.set_led_color(self.led_controller.num_led - i + 2, *_BLUE, brightness)
#
#            self.led_controller.show()
#            await asyncio.sleep(0.02)

        await asyncio.sleep(0.5)


    async def listen(self) -> None:
        pass


    async def think(self) -> None:
        self._active = True

        o = 0
        while True:
            o = (o + 1) % 2 #o = offset can be either zero or one and is used to switch between blue and white on the led for each iteration
            for i in range(0, self.led_controller.num_led):
                if (i + o) % 2 == 0:
                    self.led_controller.set_led_color(i, *_BLUE)
                else:
                    self.led_controller.set_led_color(i, *_WHITE)

            self.led_controller.show()
            await asyncio.sleep(0.15)


    async def speak(self) -> None:
        self._active = True

        direction = 1
        val = 255

        self.color(*_WHITE, show=False)

        while True:
            self.color(red=val, green=val, blue=255)

            val -= direction
            if val >= 255 or val <= 0:
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

        while True:
            self.color(*_RED, brightness)
            if brightness <= min_brightness or brightness >= max_brightness:
                step = step * -1

            brightness += step
            await asyncio.sleep(0.04)
