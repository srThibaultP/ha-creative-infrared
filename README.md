# Creative Infrared

Home Assistant integration that controls a **Creative Stage V2** soundbar over infrared, through any entity of Home Assistant's `infrared` domain (an ESPHome IR blaster, a ZHA IR remote...). It follows the same pattern as the core `*_infrared` integrations (`lg_infrared`, `edifier_infrared`) and meets the Platinum rules of the [Integration Quality Scale](https://developers.home-assistant.io/docs/core/integration-quality-scale/) (see [`quality_scale.yaml`](custom_components/creative_infrared/quality_scale.yaml)).

## Supported devices

- Creative Stage V2 (original remote, NEC extended address `0xA4BF`). Other Creative soundbars that share this remote may work too.
- Any IR emitter exposed by Home Assistant's `infrared` integration.

## Requirements

Home Assistant 2026.11 or later, and an IR emitter already set up in Home Assistant with a clear line of sight to the soundbar.

## Installation

**Marketplace (HACS):** add `srThibaultP/ha-creative-infrared` as a custom repository with category *Integration*, install **Creative Infrared**, then restart Home Assistant.

**Manual:** copy `custom_components/creative_infrared` to `/config/custom_components/` and restart Home Assistant.

Then go to **Settings > Devices & services > Add integration > Creative Infrared**.

### Installation parameters

| Parameter | Description |
| --- | --- |
| Infrared emitter | The `infrared` entity that sends the codes. Only emitters are listed. |
| Name | Name of the soundbar device (default `Creative Stage V2`). |

To switch to another emitter later, use **Reconfigure** on the integration entry. There are no other options.

## Entities

| Entity | Description |
| --- | --- |
| Media player | Turn on/off, volume up/down, mute, play/pause, next/previous, source (TV ARC / USB, OPT / AUX, Bluetooth). |
| Surround, Dialog, Bass / Treble, More, Less, Reset buttons | Sound settings keys (configuration category). |
| Power, Mute, source, volume and transport buttons | Same keys as the media player, disabled by default; enable them if you prefer raw key presses. |

Every entity becomes unavailable when the IR emitter is unavailable.

## Examples

Turn the soundbar on and switch to the TV input when the TV turns on:

```yaml
automation:
  - alias: Soundbar follows the TV
    triggers:
      - trigger: state
        entity_id: media_player.living_room_tv
        to: "on"
    actions:
      - action: media_player.select_source
        target:
          entity_id: media_player.creative_stage_v2
        data:
          source: TV ARC / USB
```

Lower the volume by three steps:

```yaml
actions:
  - repeat:
      count: 3
      sequence:
        - action: media_player.volume_down
          target:
            entity_id: media_player.creative_stage_v2
```

Use cases: voice control through Assist, turning the soundbar off with the rest of the room, night mode with Dialog enhancement.

## Known limitations

- IR is one-way: power, mute and source are **assumed** from the last command Home Assistant sent (and restored after a restart). If you use the physical remote, the state can drift; press **Power** or **Mute** on the media player card (or the disabled-by-default raw buttons) to get back in sync.
- There is no absolute volume, only volume steps.
- Each source key toggles between the two inputs printed on it (TV ARC / USB, OPT / AUX), so the reported source is the key, not the exact input.
- This integration does not poll and cannot discover devices.

## Troubleshooting

- **The soundbar does not react:** check that the emitter entity's state (a timestamp) changes when you press a button. If it does, move the emitter closer or aim it at the soundbar's IR window. If it does not, check the emitter device itself.
- **Entities are unavailable:** the IR emitter entity is unavailable (device offline). They come back on their own.
- **On/off is inverted:** the assumed state drifted; see Known limitations.
- Download the diagnostics from the integration entry when opening an issue.

## Removal

Go to **Settings > Devices & services > Creative Infrared**, open the entry menu and choose **Delete**. If installed from the Marketplace, also remove the repository there; otherwise delete `custom_components/creative_infrared`.

## Development

Tests run against a Home Assistant core checkout (the `pytest-home-assistant` helpers live in `packages/` there):

```bash
uv pip install -e path/to/core -e path/to/core/packages/pytest-home-assistant infrared-protocols pytest-cov syrupy mypy
pytest --cov
mypy
```
