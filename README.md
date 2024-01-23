# Wyoming Satellite - LED Event Services

Event Service for the [Wyoming protocol](https://github.com/rhasspy/wyoming) especially for [wyoming-satellite](https://github.com/rhasspy/wyoming-satellite)

Supports currently ReSpeaker 2Mic and 4Mic HAT but has an "abstract" LED and Pattern interface for other LEDs or pattern. Not any pattern might be useful with any LED Setup.

Works (propably) only with local wake word detection.

* Python 3.7+ (tested on 3.11+)
* A wyoming-satellite (or later a rhasspy 3 setup)

## Installation

Install the necessary system dependencies:

``` sh
sudo apt-get install python3-venv python3-pip
```

Then run the install script:

``` sh
script/setup --respeaker
```


## Test LED pattern

``` sh
cd wyoming-satellite-led-event/
script/test_pattern \
  --led-pattern respeaker_4mic/default
```

## Run

``` sh
cd wyoming-satellite-led-event/
script/run \
  --uri 'tcp://0.0.0.0:10700' \
  --led-pattern respeaker_4mic/default
```

This will use the respeaker 4Mic Hat with the default model.

Add `--debug` to print additional logs. See `--help` for more information.

## included LED "Controller"

* `respeaker_4mic` - ReSpeaker 4 Mic HAT
* `respeaker_2mic` - ReSpeaker 2 Mic HAT
* `mock` - Mock LED Controller for testing / development purposes

## included pattern
* `default` - default pattern from wyoming-satellite
* `alexa`   - Alexa like model (modified)
* `google`  - Google Nest like model (modified) (not yet implemented)


The pattern `alexa` and `google` are ported from [project-alice-assistant/HermesLedControl](https://github.com/project-alice-assistant/HermesLedControl). Many thanks to them.