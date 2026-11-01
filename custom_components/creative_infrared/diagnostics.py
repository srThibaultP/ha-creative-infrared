"""Diagnostics platform for the Creative infrared integration."""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_INFRARED_ENTITY_ID


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    emitter = hass.states.get(entry.data[CONF_INFRARED_ENTITY_ID])
    return {
        "data": dict(entry.data),
        "emitter_state": emitter.state if emitter else None,
    }
