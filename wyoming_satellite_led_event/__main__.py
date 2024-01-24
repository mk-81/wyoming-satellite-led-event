import argparse
import logging
import asyncio
import time
import importlib
import sys

from functools import partial
from wyoming.server import AsyncEventHandler, AsyncServer
from wyoming.event import Event
from .base import LedPatternRunner, AbstractLedPattern

_LOGGER   = logging.getLogger()
_PCK_NAME = "wyoming_satellite_led_event"

def create_led_pattern(name : str) -> AbstractLedPattern:
    #name scheme LED Controller(Proxy)/pattern for generic patterns
    #more to come?

    p = name.split("/")

    try:
        led_controller_lib = importlib.import_module(".led_controller." + p[0], _PCK_NAME)
        led_controller_cls = getattr(led_controller_lib, "LedController", None)
        if led_controller_cls is None:
            _LOGGER.fatal("LED Controller implementation error")
            sys.exit(1)

    except ModuleNotFoundError:
        _LOGGER.fatal("LED Controller not found")
        sys.exit(1)



    pattern_name = p[1] if len(p) > 1 else "default"
    try:
        led_pattern_lib = importlib.import_module(".led_pattern." +pattern_name, _PCK_NAME)
        led_pattern_cls = getattr(led_pattern_lib, "LedPattern", None)
        if led_pattern_cls is None:
            _LOGGER.fatal("LED Pattern implementation error")
            sys.exit(1)
    except ModuleNotFoundError:
        _LOGGER.fatal("LED Pattern not found")
        sys.exit(1)



    return led_pattern_cls(
             led_controller=led_controller_cls()
           )



async def main():
    """Main entry point."""
    parser = argparse.ArgumentParser()

    parser.add_argument("--led-pattern", required=True, help="LED Pattern to use in format led_controller/pattern or led_controller. Last uses the default model from wyoming-satellite", )

    parser.add_argument("--uri", required=False, help="unix:// or tcp://")
    parser.add_argument("--test", action="store_true", help="Test supplied LED Pattern")

    parser.add_argument("--debug", action="store_true", help="Log DEBUG messages")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)
    _LOGGER.debug(args)

    args = parser.parse_args()

    if not args.test and not args.uri:
        _LOGGER.fatal("Either --test or --uri is required")
        sys.exit(1)

    led_pattern : AbstractLedPattern = create_led_pattern(args.led_pattern)
    led_pattern.setup()

    if args.test:
        from .test_pattern import test_pattern
        await test_pattern(led_pattern)
        return


    _LOGGER.info("Ready")
    # Start server
    server = AsyncServer.from_uri(args.uri)

    try:
        await server.run(partial(EventHandler, led_pattern))
    except KeyboardInterrupt:
        pass
    finally:
        led_pattern.cleanup()


class EventHandler(AsyncEventHandler):
    def __init__(
        self,
        led_pattern : AbstractLedPattern,
        *args,
        **kwargs,
    ) -> None:
        super().__init__(*args, **kwargs)

        self.led_pattern : LedPatternRunner = LedPatternRunner(led_pattern)
        self.led_pattern.setup()
        self.client_id = str(time.monotonic_ns())

        _LOGGER.debug("Client connected: %s", self.client_id)

    async def handle_event(self, event: Event) -> bool:
        _LOGGER.debug(event)

        if self.led_pattern:
            await self.led_pattern.handle_event(event)

        return True


def run():
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    run()
