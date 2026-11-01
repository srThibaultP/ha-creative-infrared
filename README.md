# Creative Infrared

Home Assistant custom integration that controls a **Creative Stage V2** soundbar over infrared, through any entity of Home Assistant's `infrared` domain (ESPHome, ZHA...). It follows the same pattern as the core `*_infrared` integrations (`edifier_infrared`, `marantz_infrared`).

## Entities

- `media_player`: on/off, volume step, mute, play/pause, next/previous, source (TV ARC / USB, OPT / AUX, Bluetooth). IR is one-way, so power, mute and source are assumed from the last command sent and restored after a restart.
- One `button` per remote key (16): power, mute, sources, volume, transport, surround, reset, dialog, more/less, bass/treble.

The remote uses NEC extended address `0xA4BF`; command bytes are in `custom_components/creative_infrared/const.py`.

## Install

Copy `custom_components/creative_infrared` to `/config/custom_components/`, restart Home Assistant, then add **Creative Infrared** from Settings > Devices & services and pick the IR emitter.

Requires Home Assistant 2026.11 or later (the `infrared` integration).
