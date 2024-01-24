#!/usr/bin/env python3

#ToDo - test against real sequences of events from wyoming protocol

import asyncio
from .base import AbstractLedPattern, LedPatternRunner

from wyoming.event import Event
from wyoming.pipeline import RunPipeline,PipelineStage
from wyoming.asr import Transcript, Transcribe
from wyoming.audio import AudioStart, AudioStop
from wyoming.error import Error
from wyoming.snd import Played
from wyoming.tts import Synthesize
from wyoming.vad import VoiceStarted, VoiceStopped
from wyoming.wake import Detection
from wyoming.satellite import SatelliteConnected, SatelliteDisconnected, StreamingStarted, StreamingStopped


async def test_successfull(runner : LedPatternRunner):
    print("wake -> listen to voice command -> think -> speak")
    #ToDo -> real events from Log

    await runner.handle_event(Detection().event())
    await asyncio.sleep(3)
    await runner.handle_event(VoiceStarted().event())
    await asyncio.sleep(3)
    await runner.handle_event(VoiceStopped().event())
    await asyncio.sleep(3)
    await runner.handle_event(AudioStart(rate=16000, width=32, channels=1).event())
    await asyncio.sleep(3)
    await runner.handle_event(Played().event())


async def test_erroneous(runner : LedPatternRunner):
    print("wake -> listen to voice command -> error")
    #ToDo -> real events from Log
    await runner.handle_event(Detection().event())
    await asyncio.sleep(3)
    await runner.handle_event(VoiceStarted().event())
    await asyncio.sleep(3)
    await runner.handle_event(VoiceStopped().event())
    await asyncio.sleep(3)
    await runner.handle_event(Error(text="test").event())


# voice command which has been cancelled via cancel commang (e.g. nevermind)
async def test_cancelled_command(runner : LedPatternRunner):
    print("wake -> listen to voice command -> think -> nevermind / no response")

#    Jan 23 18:05:04 Event(type='run-pipeline', data={'start_stage': 'asr', 'end_stage': 'tts', 'restart_on_end': False}, payload=None)
#    Jan 23 18:05:04 Event(type='detection', data={'name': 'jarvis', 'timestamp': 142290504007}, payload=None)
#    Jan 23 18:05:04 Event(type='streaming-started', data=None, payload=None)
#    Jan 23 18:05:04 Event(type='transcribe', data={'language': 'en'}, payload=None)
#    Jan 23 18:05:07 Event(type='voice-started', data={'timestamp': 1135}, payload=None)
#    Jan 23 18:05:08 Event(type='voice-stopped', data={'timestamp': 1615}, payload=None)
#    Jan 23 18:05:13 Event(type='transcript', data={'text': 'nevermind.'}, payload=None)
#    Jan 23 18:05:13 Event(type='streaming-stopped', data=None, payload=None)

    await runner.handle_event(RunPipeline(start_stage=PipelineStage(PipelineStage.ASR), end_stage=PipelineStage(PipelineStage.TTS), restart_on_end=False).event())
    await runner.handle_event(Detection(name='jarvis', timestamp=142290504007).event())
    await runner.handle_event(StreamingStarted().event())
    await runner.handle_event(Transcribe(language='en').event())
    await asyncio.sleep(3)
    await runner.handle_event(VoiceStarted(timestamp=1135).event())
    await asyncio.sleep(1)
    await runner.handle_event(VoiceStopped(timestamp=1615).event())
    await asyncio.sleep(5)
    await runner.handle_event(Transcript(text="nevermind").event())
    await runner.handle_event(StreamingStopped().event())



async def test_pattern(pattern : AbstractLedPattern):
    runner = LedPatternRunner(pattern)
    runner.setup()

    try:
        print("Connected")
        await runner.handle_event(SatelliteConnected().event())
        await asyncio.sleep(3)

        await test_successfull(runner)
        await asyncio.sleep(3)

        await test_erroneous(runner)
        await asyncio.sleep(5)

        await test_cancelled_command(runner)
        await asyncio.sleep(5)

        print("Disconnected")
        await runner.handle_event(SatelliteDisconnected().event())
        await asyncio.sleep(5)
        pattern.cleanup()
    finally:
        runner.cleanup()