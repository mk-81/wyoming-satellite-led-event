from asyncio import Task, Queue, QueueEmpty
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
from wyoming.satellite import SatelliteConnected, SatelliteDisconnected

from .led_controller import AbstractLedController

_LOGGER = logging.getLogger()

class _EVENTS(Enum):
    CONNECTED    = 200
    DISCONNECTED = 201
    WAKEUP       = 202
    THINK        = 203
    SPEAK        = 204
    DONE         = 205
    ERROR        = 206


class AbstractLedPattern:
    class STATE(Enum):
        DISCONNECTED = 100
        IDLE         = 101
        LISTENING    = 102
        THINKING     = 103
        SPEAKING     = 104


    def __init__(self,*args, **kwargs):
        self.__state = None
        self.__event_queue : Queue
        self.__task : Task
        
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

    def has_pending_event(self) -> bool:
        return not self.__event_queue.empty()
    
    @property
    def state(self):
        return self.__state
   

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

    async def __runner(self):
        while True:
            try:
                #currently we process only the last event as we have a clear (wyoming) event -> state connection
                event = await self.__event_queue.get()
                while True:
                    try:
                        event = self.__event_queue.get_nowait()
                    except QueueEmpty:
                        break
 
               
                if event == _EVENTS.CONNECTED:
                    await self.client_connected()
                    self.__state = AbstractLedPattern.STATE.IDLE
                    await self.idle()
                
                elif event == _EVENTS.DISCONNECTED:
                    await self.client_disconnected()
                    self.__state = AbstractLedPattern.STATE.DISCONNECTED
                    await self.disconnected()

                elif event == _EVENTS.WAKEUP:
                    await self.wakeup()
                    self.__state = AbstractLedPattern.STATE.LISTENING
                    await self.listen()

                elif event == _EVENTS.THINK:
                    self.__state = AbstractLedPattern.STATE.THINKING
                    await self.think()
                
                elif event == _EVENTS.SPEAK:
                    self.__state = AbstractLedPattern.STATE.SPEAKING
                    await self.speak()

                elif event == _EVENTS.ERROR:
                    await self.error()
                    self.__state = AbstractLedPattern.STATE.IDLE
                    await self.idle()

                elif event == _EVENTS.DONE:
                    self.__state = AbstractLedPattern.STATE.IDLE
                    await self.idle()

            except Exception as e:
                _LOGGER.exception(e)


    async def push_event(self, event : Event):
        e = None

        if SatelliteConnected.is_type(event.type):
            e = _EVENTS.CONNECTED
        
        elif SatelliteDisconnected.is_type(event.type):
            e = _EVENTS.DISCONNECTED

        elif Detection.is_type(event.type):
            e = _EVENTS.WAKEUP

        elif VoiceStopped.is_type(event.type):
            e = _EVENTS.THINK
        
        elif AudioStart.is_type(event.type):
            e = _EVENTS.SPEAK

        elif Error.is_type(event.type):
            e = _EVENTS.ERROR

        elif Played.is_type(event.type):
            e = _EVENTS.DONE

        if e is not None:
            await self.__event_queue.put(e)


    def setup(self):
        self.__state       = AbstractLedPattern.STATE.DISCONNECTED
        self.__event_queue = Queue()
        self.__task        = Task(self.__runner())


    def cleanup(self):
        self.__task.cancel()
        


class GenericLedPattern(AbstractLedPattern):
    def __init__(self, led_controller : AbstractLedController, *agrs, **kwargs):
        super().__init__(*agrs, **kwargs)
        self.led_controller = led_controller

    def cleanup(self):
        self.led_controller.cleanup()
        return super().cleanup()