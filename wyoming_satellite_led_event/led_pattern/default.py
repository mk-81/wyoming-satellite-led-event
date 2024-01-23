import asyncio
from ..base import GenericLedPattern
from typing import Tuple


#DEBUG:root:Event(type='detection', data={'name': 'alexa_v0.1', 'timestamp': 209553854762}, payload=None)
#DEBUG:root:Event(type='streaming-started', data=None, payload=None)
#DEBUG:root:Event(type='transcribe', data={'language': 'de'}, payload=None)
#DEBUG:root:Event(type='voice-started', data={'timestamp': 230}, payload=None)
#DEBUG:root:Event(type='voice-stopped', data={'timestamp': 830}, payload=None)
#DEBUG:root:Event(type='transcript', data={'text': '...'}, payload=None)
#DEBUG:root:Event(type='streaming-stopped', data=None, payload=None)
#DEBUG:root:Event(type='synthesize', data={'text': '...', 'voice': {'name': '...'}}, payload=None)


_BLACK = (0, 0, 0)
_WHITE = (255, 255, 255)
_RED = (255, 0, 0)
_YELLOW = (255, 255, 0)
_BLUE = (0, 0, 255)
_GREEN = (0, 255, 0)

class LedPattern(GenericLedPattern):
    def color(self, rgb: Tuple[int, int, int]) -> None:
        for i in range(self.led_controller.num_led):
            self.led_controller.set_led_color(i, *rgb)

        self.led_controller.show()


    async def satellite_connected(self) -> None:
        # Flash
        for _ in range(3):
            self.color(_GREEN)
            await asyncio.sleep(0.3)
            self.color(_BLACK)
            await asyncio.sleep(0.3)


    async def idle(self) -> None:
        self.color(_BLACK)


    async def disconnected(self) -> None:
        self.color(_RED)


    async def off(self) -> None:
        self.color(_BLACK)


    async def wakeup(self) -> None:
        self.color(_BLUE)
        await asyncio.sleep(1.0)  # show for (at least) 1 sec


    async def listen(self) -> None:
        self.color(_YELLOW)


    async def think(self) -> None:
        self.color(_GREEN)
        await asyncio.sleep(1.0) # show for (at least) 1 sec 


    async def speak(self) -> None:
        self.color(_BLACK)


    async def error(self) -> None:
        # Flash
        for _ in range(3):
            self.color(_RED)
            await asyncio.sleep(0.3)
            self.color(_BLACK)
            await asyncio.sleep(0.3)