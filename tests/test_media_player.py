"""Tests for the Creative infrared media player platform."""

import pytest
from pytest_homeassistant.common import (
    MockConfigEntry,
    mock_restore_cache,
    snapshot_platform,
)
from pytest_homeassistant.components.common import (
    assert_availability_follows_source_entity,
)
from pytest_homeassistant.components.infrared import EMITTER_ENTITY_ID
from pytest_homeassistant.components.infrared.common import MockInfraredEmitterEntity
from syrupy.assertion import SnapshotAssertion

from custom_components.creative_infrared.const import NEC_ADDRESS, CreativeStageV2Code
from homeassistant.components.media_player import (
    ATTR_INPUT_SOURCE,
    ATTR_MEDIA_VOLUME_MUTED,
    DOMAIN as MEDIA_PLAYER_DOMAIN,
    SERVICE_MEDIA_NEXT_TRACK,
    SERVICE_MEDIA_PAUSE,
    SERVICE_MEDIA_PLAY,
    SERVICE_MEDIA_PREVIOUS_TRACK,
    SERVICE_SELECT_SOURCE,
    SERVICE_TURN_OFF,
    SERVICE_TURN_ON,
    SERVICE_VOLUME_DOWN,
    SERVICE_VOLUME_MUTE,
    SERVICE_VOLUME_UP,
)
from homeassistant.const import ATTR_ENTITY_ID, STATE_OFF, STATE_ON, Platform
from homeassistant.core import HomeAssistant, State
from homeassistant.helpers import entity_registry as er

ENTITY_ID = "media_player.creative_stage_v2"


@pytest.fixture
def platforms() -> list[Platform]:
    """Return platforms to set up."""
    return [Platform.MEDIA_PLAYER]


def _sent(emitter: MockInfraredEmitterEntity) -> list[CreativeStageV2Code]:
    assert all(call.address == NEC_ADDRESS for call in emitter.send_command_calls)
    return [CreativeStageV2Code(call.command) for call in emitter.send_command_calls]


async def _call(hass: HomeAssistant, service: str, **data: object) -> None:
    await hass.services.async_call(
        MEDIA_PLAYER_DOMAIN,
        service,
        {ATTR_ENTITY_ID: ENTITY_ID, **data},
        blocking=True,
    )


@pytest.mark.usefixtures("init_integration")
async def test_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test the media player entity."""
    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


@pytest.mark.parametrize(
    ("service", "service_data", "expected_code"),
    [
        (SERVICE_TURN_ON, {}, CreativeStageV2Code.POWER),
        (SERVICE_TURN_OFF, {}, CreativeStageV2Code.POWER),
        (SERVICE_VOLUME_UP, {}, CreativeStageV2Code.VOLUME_UP),
        (SERVICE_VOLUME_DOWN, {}, CreativeStageV2Code.VOLUME_DOWN),
        (
            SERVICE_VOLUME_MUTE,
            {ATTR_MEDIA_VOLUME_MUTED: True},
            CreativeStageV2Code.MUTE,
        ),
        (SERVICE_MEDIA_PLAY, {}, CreativeStageV2Code.PLAY_PAUSE),
        (SERVICE_MEDIA_PAUSE, {}, CreativeStageV2Code.PLAY_PAUSE),
        (SERVICE_MEDIA_NEXT_TRACK, {}, CreativeStageV2Code.NEXT),
        (SERVICE_MEDIA_PREVIOUS_TRACK, {}, CreativeStageV2Code.PREVIOUS),
        (
            SERVICE_SELECT_SOURCE,
            {ATTR_INPUT_SOURCE: "Bluetooth"},
            CreativeStageV2Code.BLUETOOTH,
        ),
    ],
)
@pytest.mark.usefixtures("init_integration")
async def test_action_sends_code(
    hass: HomeAssistant,
    mock_infrared_emitter_entity: MockInfraredEmitterEntity,
    service: str,
    service_data: dict[str, object],
    expected_code: CreativeStageV2Code,
) -> None:
    """Test each action sends the matching remote code."""
    await _call(hass, service, **service_data)

    assert _sent(mock_infrared_emitter_entity) == [expected_code]


@pytest.mark.usefixtures("init_integration")
async def test_power_is_not_tracked(
    hass: HomeAssistant,
    mock_infrared_emitter_entity: MockInfraredEmitterEntity,
) -> None:
    """Test turn on and turn off always send the power toggle.

    The soundbar flips power on its own (auto standby, HDMI CEC), so an
    assumed on/off state would drift and invert the buttons.
    """
    await _call(hass, SERVICE_TURN_OFF)
    await _call(hass, SERVICE_TURN_OFF)
    await _call(hass, SERVICE_TURN_ON)
    await _call(hass, SERVICE_TURN_ON)

    assert _sent(mock_infrared_emitter_entity) == [CreativeStageV2Code.POWER] * 4
    assert hass.states.get(ENTITY_ID).state == STATE_ON


@pytest.mark.usefixtures("init_integration")
async def test_mute_toggle_is_tracked(
    hass: HomeAssistant,
    mock_infrared_emitter_entity: MockInfraredEmitterEntity,
) -> None:
    """Test the mute key is only sent when the assumed state changes."""
    await _call(hass, SERVICE_VOLUME_MUTE, **{ATTR_MEDIA_VOLUME_MUTED: False})
    await _call(hass, SERVICE_VOLUME_MUTE, **{ATTR_MEDIA_VOLUME_MUTED: True})
    await _call(hass, SERVICE_VOLUME_UP)

    assert _sent(mock_infrared_emitter_entity) == [
        CreativeStageV2Code.MUTE,
        CreativeStageV2Code.VOLUME_UP,
    ]
    assert hass.states.get(ENTITY_ID).attributes[ATTR_MEDIA_VOLUME_MUTED] is False


async def test_state_is_restored(
    hass: HomeAssistant,
    mock_config_entry: MockConfigEntry,
    mock_infrared_emitter_entity: MockInfraredEmitterEntity,
) -> None:
    """Test mute and source are restored after a restart, power is not."""
    mock_restore_cache(
        hass,
        [
            State(
                ENTITY_ID,
                STATE_OFF,
                {ATTR_MEDIA_VOLUME_MUTED: True, ATTR_INPUT_SOURCE: "Bluetooth"},
            )
        ],
    )
    mock_config_entry.add_to_hass(hass)
    await hass.config_entries.async_setup(mock_config_entry.entry_id)
    await hass.async_block_till_done()

    state = hass.states.get(ENTITY_ID)
    assert state.state == STATE_ON
    assert state.attributes[ATTR_MEDIA_VOLUME_MUTED] is True
    assert state.attributes[ATTR_INPUT_SOURCE] == "Bluetooth"
    assert _sent(mock_infrared_emitter_entity) == []


@pytest.mark.usefixtures("init_integration")
async def test_availability_follows_ir_entity(hass: HomeAssistant) -> None:
    """Test the media player follows the emitter's availability."""
    await assert_availability_follows_source_entity(
        hass, ENTITY_ID, [EMITTER_ENTITY_ID]
    )
