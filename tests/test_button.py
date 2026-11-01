"""Tests for the Creative infrared button platform."""

import pytest
from pytest_homeassistant.common import MockConfigEntry, snapshot_platform
from pytest_homeassistant.components.common import (
    assert_availability_follows_source_entity,
)
from pytest_homeassistant.components.infrared import EMITTER_ENTITY_ID
from pytest_homeassistant.components.infrared.common import MockInfraredEmitterEntity
from syrupy.assertion import SnapshotAssertion

from custom_components.creative_infrared.const import NEC_ADDRESS, CreativeStageV2Code
from homeassistant.components.button import DOMAIN as BUTTON_DOMAIN, SERVICE_PRESS
from homeassistant.const import ATTR_ENTITY_ID, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er


@pytest.fixture
def platforms() -> list[Platform]:
    """Return platforms to set up."""
    return [Platform.BUTTON]


@pytest.mark.usefixtures("entity_registry_enabled_by_default", "init_integration")
async def test_entities(
    hass: HomeAssistant,
    snapshot: SnapshotAssertion,
    entity_registry: er.EntityRegistry,
    mock_config_entry: MockConfigEntry,
) -> None:
    """Test all remote buttons are created."""
    await snapshot_platform(hass, entity_registry, snapshot, mock_config_entry.entry_id)


@pytest.mark.parametrize("code", list(CreativeStageV2Code))
@pytest.mark.usefixtures("entity_registry_enabled_by_default", "init_integration")
async def test_press_sends_code(
    hass: HomeAssistant,
    mock_infrared_emitter_entity: MockInfraredEmitterEntity,
    code: CreativeStageV2Code,
) -> None:
    """Test each button sends its NEC code."""
    await hass.services.async_call(
        BUTTON_DOMAIN,
        SERVICE_PRESS,
        {ATTR_ENTITY_ID: f"button.creative_stage_v2_{code.name.lower()}"},
        blocking=True,
    )

    [command] = mock_infrared_emitter_entity.send_command_calls
    assert (command.address, command.command) == (NEC_ADDRESS, code)


@pytest.mark.usefixtures("init_integration")
async def test_availability_follows_ir_entity(hass: HomeAssistant) -> None:
    """Test buttons follow the emitter's availability."""
    await assert_availability_follows_source_entity(
        hass, "button.creative_stage_v2_surround", [EMITTER_ENTITY_ID]
    )
