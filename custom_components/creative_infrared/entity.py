"""Common entity for the Creative infrared integration."""

from infrared_protocols.commands.nec import NECCommand

from homeassistant.components.infrared import InfraredEmitterConsumerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.device_registry import DeviceInfo

from .const import CONF_INFRARED_ENTITY_ID, DOMAIN, NEC_ADDRESS, CreativeStageV2Code


class CreativeIrEntity(InfraredEmitterConsumerEntity):
    """Creative IR base entity: device info and NEC sending."""

    _attr_has_entity_name = True

    def __init__(self, entry: ConfigEntry, unique_id_suffix: str) -> None:
        """Initialize the soundbar IR entity."""
        self._infrared_emitter_entity_id = entry.data[CONF_INFRARED_ENTITY_ID]
        self._attr_unique_id = f"{entry.entry_id}_{unique_id_suffix}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry.entry_id)},
            name=entry.title,
            manufacturer="Creative",
            model="Stage V2",
        )

    async def _send_code(self, code: CreativeStageV2Code) -> None:
        """Send one remote button press."""
        await self._send_command(NECCommand(address=NEC_ADDRESS, command=code))
