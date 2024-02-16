import asyncio
import logging

from enum import Enum

from wyoming.event import Event
from wyoming.asr import Transcript
from wyoming.audio import AudioStart, AudioStop
from wyoming.error import Error
from wyoming.snd import Played
from wyoming.tts import Synthesize
from wyoming.vad import VoiceStarted, VoiceStopped
from wyoming.wake import Detection
from wyoming.satellite import SatelliteConnected, SatelliteDisconnected, StreamingStarted, StreamingStopped

from .led_controller import AbstractLedController

_LOGGER = logging.getLogger()

class _EVENTS(Enum):
    CONNECTED    = 200
    DISCONNECTED = 201
    WAKEUP       = 202
    LISTEN_START = 203
    LISTEN_END   = 204
    THINK_START  = 205
    THINK_END    = 206
    SPEAK_START  = 207
    SPEAK_END    = 208
    ERROR        = 209


class AbstractLedPattern:
    class STATE(Enum):
        DISCONNECTED = 100
        IDLE         = 101
        LISTENING    = 102
        THINKING     = 103
        SPEAKING     = 104

    async def idle(self) -> None:
        pass

    async def disconnected(self) -> None:
        pass

    async def wakeup(self) -> None:
        pass

    async def listen(self) -> None:
        pass

    async def think(self) -> None:
        pass

    async def speak(self) -> None:
        pass

    async def error(self) -> None:
        pass

    async def client_connected(self) -> None:
        pass

    async def client_disconnected(self) -> None:
        pass

    def setup(self):
        pass

    def cleanup(self):
        pass


class GenericLedPattern(AbstractLedPattern):
    def __init__(self, led_controller : AbstractLedController, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)
        self.led_controller = led_controller

    def cleanup(self):
        self.led_controller.cleanup()
        return super().cleanup()


class LedPatternRunner():
    def __init__(self, pattern: AbstractLedPattern):
        self.__event_queue    : asyncio.Queue = None
        self.__evt_queue_task : asyncio.Task  = None
        self.__pattern_task   : asyncio.Task  = None

        self.__pattern        : AbstractLedPattern = pattern
        self.__state = AbstractLedPattern.STATE.DISCONNECTED


    def setup(self):
        self.__event_queue    = asyncio.Queue()
        self.__evt_queue_task = asyncio.create_task(self.__event_queue_runner())


    def cleanup(self):
        if self.__pattern_task:
            self.__pattern_task.cancel()
        self.__evt_queue_task.cancel()
        self.__pattern.cleanup()


    @property
    def state(self):
        return self.__state



    async def __start_pattern_state(self, c):
        async def __run(c):
            await c()


        if self.__pattern_task:
            self.__pattern_task.cancel()
            try:
                await self.__pattern_task
            except asyncio.CancelledError:
                pass

        self.__pattern_task = asyncio.create_task(__run(c))



    def translate_event(event : Event, assumed_current_state):
#    Jan 23 18:05:04 Event(type='run-pipeline', data={'start_stage': 'asr', 'end_stage': 'tts', 'restart_on_end': False}, payload=None)
#    Jan 23 18:05:04 Event(type='detection', data={'name': 'jarvis', 'timestamp': 142290504007}, payload=None)
#    Jan 23 18:05:04 Event(type='streaming-started', data=None, payload=None)
#    Jan 23 18:05:04 Event(type='transcribe', data={'language': 'de'}, payload=None)
#    Jan 23 18:05:07 Event(type='voice-started', data={'timestamp': 1135}, payload=None)
#    Jan 23 18:05:08 Event(type='voice-stopped', data={'timestamp': 1615}, payload=None)
#    Jan 23 18:05:13 Event(type='transcript', data={'text': 'Vergiss es.'}, payload=None)
#    Jan 23 18:05:13 Event(type='streaming-stopped', data=None, payload=None)

        if SatelliteConnected.is_type(event.type):
            return _EVENTS.CONNECTED

        elif SatelliteDisconnected.is_type(event.type):
            return _EVENTS.DISCONNECTED

        elif Detection.is_type(event.type):
            return _EVENTS.WAKEUP

        elif VoiceStarted.is_type(event.type) or StreamingStarted.is_type(event.type):
            if assumed_current_state == AbstractLedPattern.STATE.IDLE:
                return _EVENTS.LISTEN_START

        elif VoiceStopped.is_type(event.type):
            return _EVENTS.THINK_START

        elif Transcript.is_type(event.type):
            return _EVENTS.THINK_END

        elif AudioStart.is_type(event.type):
            return _EVENTS.SPEAK_START

        elif Played.is_type(event.type):
            return _EVENTS.SPEAK_END

        elif StreamingStopped.is_type(event.type):
            if assumed_current_state != AbstractLedPattern.STATE.IDLE:
                return

        elif Error.is_type(event.type):
            return _EVENTS.ERROR

        return None



    async def __event_queue_runner(self):
        wyoming_event : Event
        timeout = None

        def __timeout(new):
            if timeout is None:
                return new
            else:
                return min(timeout,new)

        while True:
            try:
                timeout = None
                next_state = self.__state
                pattern_event = None

                while True:
                    process_event = False

                    try:
                        async with asyncio.timeout(timeout):
                            wyoming_event = await self.__event_queue.get()
                    except TimeoutError:
                        process_event = True

                    pattern_event = LedPatternRunner.translate_event(wyoming_event, next_state) or pattern_event
                    if pattern_event in ( _EVENTS.CONNECTED, _EVENTS.LISTEN_END, _EVENTS.THINK_END, _EVENTS.SPEAK_END ):
                        next_state = AbstractLedPattern.STATE.IDLE
                        timeout = __timeout(0.250)

                    elif pattern_event == _EVENTS.ERROR:
                        next_state = AbstractLedPattern.STATE.IDLE
                        timeout = __timeout(0)

                    elif pattern_event == _EVENTS.DISCONNECTED:
                        next_state = AbstractLedPattern.STATE.DISCONNECTED
                        timeout = __timeout(0)

                    elif pattern_event in ( _EVENTS.WAKEUP, _EVENTS.LISTEN_START ):
                        next_state = AbstractLedPattern.STATE.LISTENING
                        timeout = __timeout(0)

                    elif pattern_event == _EVENTS.THINK_START:
                        next_state = AbstractLedPattern.STATE.THINKING
                        timeout = __timeout(0.250)

                    elif pattern_event == _EVENTS.SPEAK_START:
                        next_state = AbstractLedPattern.STATE.SPEAKING
                        timeout = __timeout(0.250)

                    if process_event:
                        break


                if pattern_event == _EVENTS.CONNECTED:
                    await self.__pattern.client_connected()
                elif pattern_event == _EVENTS.DISCONNECTED:
                    await self.__pattern.client_disconnected()
                elif pattern_event == _EVENTS.WAKEUP:
                    await self.__pattern.wakeup()
                elif pattern_event == _EVENTS.ERROR:
                    await self.__pattern.error()

                self.__state = next_state

                if self.__state == AbstractLedPattern.STATE.DISCONNECTED:
                    await self.__start_pattern_state(self.__pattern.disconnected)
                elif self.__state == AbstractLedPattern.STATE.IDLE:
                    await self.__start_pattern_state(self.__pattern.idle)
                elif self.__state == AbstractLedPattern.STATE.LISTENING:
                    await self.__start_pattern_state(self.__pattern.listen)
                elif self.__state == AbstractLedPattern.STATE.THINKING:
                    await self.__start_pattern_state(self.__pattern.think)
                elif self.__state == AbstractLedPattern.STATE.SPEAKING:
                    await self.__start_pattern_state(self.__pattern.speak)

            except Exception as e:
                _LOGGER.exception(e)


    async def handle_event(self, event : Event):
        await self.__event_queue.put(event)


    # async def __runner(self):
    #     event : Event

    #     while True:
    #         try:
    #             #currently we process any event. this is (theoretically) not required, but after wakeup there is no defined state change
    #             #because listening is handled by another wyoming event. same goes propably for others to
    #             event = await self.__event_queue.get()

    #             # satellite-connected -> connection to server = "idle"
    #             # detection -> Wakeup
    #             # voice-started -> listen,
    #             # voice-stopped -> listen end / think
    #             # transcript / think end
    #             # Audio Start / Synthesize.is_type(event.type) -> speech start?
    #             # Played -> speech end

    #             if SatelliteConnected.is_type(event.type):
    #                 await self.client_connected()
    #                 self.__state = AbstractLedPattern.STATE.IDLE
    #                 await self.idle()

    #             elif SatelliteDisconnected.is_type(event.type):
    #                 await self.client_disconnected()
    #                 self.__state = AbstractLedPattern.STATE.DISCONNECTED
    #                 await self.disconnected()

    #             elif Detection.is_type(event.type):
    #                 await self.wakeup()
    #                 self.__state = None #? undefined here

    #             elif VoiceStarted.is_type(event.type):
    #                 self.__state = AbstractLedPattern.STATE.LISTENING
    #                 await self.listen()

    #             elif VoiceStopped.is_type(event.type):
    #                 self.__state = AbstractLedPattern.STATE.THINKING
    #                 await self.think()

    #             elif AudioStart.is_type(event.type):
    #                 self.__state = AbstractLedPattern.STATE.SPEAKING
    #                 await self.speak()

    #             elif Error.is_type(event.type):
    #                 await self.error()
    #                 self.__state = AbstractLedPattern.STATE.IDLE
    #                 await self.idle()

    #             elif Played.is_type(event.type):
    #                 self.__state = AbstractLedPattern.STATE.IDLE
    #                 await self.idle()

    #         except Exception as e:
    #             _LOGGER.exception(e)


    # async def push_event(self, event : Event):
    #     await self.__event_queue.put(event)
