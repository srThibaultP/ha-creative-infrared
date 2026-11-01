"""Tests for the Creative infrared config flow."""

import pytest
from pytest_homeassistant.common import MockConfigEntry
from pytest_homeassistant.components.infrared import EMITTER_ENTITY_ID
from pytest_homeassistant.components.infrared.common import MockInfraredEmitterEntity

from custom_components.creative_infrared.const import CONF_INFRARED_ENTITY_ID, DOMAIN
from homeassistant.components.infrared import DATA_COMPONENT, DOMAIN as INFRARED_DOMAIN
from homeassistant.config_entries import SOURCE_USER
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.setup import async_setup_component

OTHER_EMITTER_ENTITY_ID = "infrared.other_ir_emitter"


@pytest.mark.usefixtures("mock_infrared_emitter_entity")
async def test_user_flow(hass: HomeAssistant) -> None:
    """Test creating an entry."""
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID, CONF_NAME: "Soundbar"},
    )

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Soundbar"
    assert result["data"] == {CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID}
    assert result["result"].unique_id == EMITTER_ENTITY_ID


@pytest.mark.usefixtures("mock_infrared_emitter_entity")
async def test_user_flow_already_configured(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test an emitter can only drive one soundbar."""
    mock_config_entry.add_to_hass(hass)

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"],
        {CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID, CONF_NAME: "Soundbar"},
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_user_flow_no_emitters(hass: HomeAssistant) -> None:
    """Test the flow aborts without an IR emitter."""
    assert await async_setup_component(hass, INFRARED_DOMAIN, {})

    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": SOURCE_USER}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_emitters"


async def _add_other_emitter(hass: HomeAssistant) -> None:
    await hass.data[DATA_COMPONENT].async_add_entities(
        [MockInfraredEmitterEntity("other_ir_emitter", "Other IR emitter")]
    )


@pytest.mark.usefixtures("init_integration")
async def test_reconfigure_flow(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test moving the soundbar to another emitter."""
    await _add_other_emitter(hass)

    result = await mock_config_entry.start_reconfigure_flow(hass)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "reconfigure"

    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_INFRARED_ENTITY_ID: OTHER_EMITTER_ENTITY_ID}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"
    assert mock_config_entry.data == {CONF_INFRARED_ENTITY_ID: OTHER_EMITTER_ENTITY_ID}
    assert mock_config_entry.unique_id == OTHER_EMITTER_ENTITY_ID


@pytest.mark.usefixtures("init_integration")
async def test_reconfigure_flow_same_emitter(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test reconfiguring with the current emitter."""
    result = await mock_config_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_INFRARED_ENTITY_ID: EMITTER_ENTITY_ID}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "reconfigure_successful"


@pytest.mark.usefixtures("init_integration")
async def test_reconfigure_flow_emitter_in_use(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test an emitter used by another soundbar is refused."""
    await _add_other_emitter(hass)
    MockConfigEntry(
        domain=DOMAIN,
        data={CONF_INFRARED_ENTITY_ID: OTHER_EMITTER_ENTITY_ID},
        unique_id=OTHER_EMITTER_ENTITY_ID,
    ).add_to_hass(hass)

    result = await mock_config_entry.start_reconfigure_flow(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_INFRARED_ENTITY_ID: OTHER_EMITTER_ENTITY_ID}
    )

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


async def test_reconfigure_flow_no_emitters(
    hass: HomeAssistant, mock_config_entry: MockConfigEntry
) -> None:
    """Test reconfigure aborts without an IR emitter."""
    assert await async_setup_component(hass, INFRARED_DOMAIN, {})
    mock_config_entry.add_to_hass(hass)

    result = await mock_config_entry.start_reconfigure_flow(hass)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "no_emitters"
