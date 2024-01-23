#!/usr/bin/env python3

#ToDo - test against real sequences of events from wyoming protocol

import asyncio
from .base import AbstractLedPattern

from wyoming.event import Event
from wyoming.asr import Transcript
from wyoming.audio import AudioStart, AudioStop
from wyoming.error import Error
from wyoming.snd import Played
from wyoming.tts import Synthesize
from wyoming.vad import VoiceStarted, VoiceStopped
from wyoming.wake import Detection
from wyoming.satellite import SatelliteConnected, SatelliteDisconnected


async def test_successfull(pattern : AbstractLedPattern):
    print("successful")
    print("Detection")
    await pattern.push_event(Detection().event())
    await asyncio.sleep(3)
    print("Voice started")
    await pattern.push_event(VoiceStarted().event())
    await asyncio.sleep(3)
    print("Voice Stopped")
    await pattern.push_event(VoiceStopped().event())
    await asyncio.sleep(3)
    print("Audio Start")
    await pattern.push_event(AudioStart(rate=16000, width=32, channels=1).event())
    await asyncio.sleep(3)
    print("Audio Stop")
    await pattern.push_event(Played().event())


async def test_erroneous(pattern : AbstractLedPattern):
    print("erroneous")
    print("Detection")
    await pattern.push_event(Detection().event())
    await asyncio.sleep(3)
    print("Voice started")
    await pattern.push_event(VoiceStarted().event())
    await asyncio.sleep(3)
    print("Voice Stopped")
    await pattern.push_event(VoiceStopped().event())
    await asyncio.sleep(3)
    print("Error")
    await pattern.push_event(Error(text="test").event())



async def test_pattern(pattern):
    print("Connected")
    await pattern.push_event(SatelliteConnected().event())
    await asyncio.sleep(3)

    await test_successfull(pattern)
    await asyncio.sleep(3)

    await test_erroneous(pattern)
    await asyncio.sleep(5)

    print("Disconnected")
    await pattern.push_event(SatelliteDisconnected().event())
    await asyncio.sleep(5)
    pattern.cleanup()



