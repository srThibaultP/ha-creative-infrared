"""Button platform for the Creative infrared integration."""

from dataclasses import dataclass

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .const import CreativeStageV2Code
from .entity import CreativeIrEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class CreativeButtonEntityDescription(ButtonEntityDescription):
    """Describes a soundbar remote button."""

    code: CreativeStageV2Code


BUTTONS = tuple(
    CreativeButtonEntityDescription(key=code.name.lower(), translation_key=code.name.lower(), code=code)
    for code in CreativeStageV2Code
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the soundbar remote buttons."""
    async_add_entities(CreativeIrButton(entry, description) for description in BUTTONS)


class CreativeIrButton(CreativeIrEntity, ButtonEntity):
    """One button of the soundbar remote."""

    entity_description: CreativeButtonEntityDescription

    def __init__(
        self, entry: ConfigEntry, description: CreativeButtonEntityDescription
    ) -> None:
        """Initialize the button."""
        super().__init__(entry, unique_id_suffix=description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        """Send the button's IR code."""
        await self._send_code(self.entity_description.code)
