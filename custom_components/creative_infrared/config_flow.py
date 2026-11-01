"""Config flow for the Creative infrared integration."""

from typing import Any

import probatio

from homeassistant.components.infrared import (
    DOMAIN as INFRARED_DOMAIN,
    async_get_emitters,
)
from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_NAME
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    TextSelector,
)

from .const import CONF_INFRARED_ENTITY_ID, DEFAULT_NAME, DOMAIN


def _emitter_selector(emitter_entity_ids: list[str]) -> EntitySelector:
    return EntitySelector(
        EntitySelectorConfig(
            domain=INFRARED_DOMAIN, include_entities=emitter_entity_ids
        )
    )


class CreativeIrConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle config flow for the soundbar."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Select the IR emitter and name the soundbar."""
        emitter_entity_ids = async_get_emitters(self.hass)
        if not emitter_entity_ids:
            return self.async_abort(reason="no_emitters")

        if user_input is not None:
            infrared_entity_id = user_input[CONF_INFRARED_ENTITY_ID]
            await self.async_set_unique_id(infrared_entity_id)
            self._abort_if_unique_id_configured()
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={CONF_INFRARED_ENTITY_ID: infrared_entity_id},
            )

        return self.async_show_form(
            step_id="user",
            data_schema=probatio.Schema(
                {
                    probatio.Required(CONF_INFRARED_ENTITY_ID): _emitter_selector(
                        emitter_entity_ids
                    ),
                    probatio.Required(CONF_NAME, default=DEFAULT_NAME): TextSelector(),
                }
            ),
        )

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Point the soundbar at another IR emitter."""
        entry = self._get_reconfigure_entry()
        emitter_entity_ids = async_get_emitters(self.hass)
        if not emitter_entity_ids:
            return self.async_abort(reason="no_emitters")

        if user_input is not None:
            infrared_entity_id = user_input[CONF_INFRARED_ENTITY_ID]
            await self.async_set_unique_id(infrared_entity_id)
            if infrared_entity_id != entry.unique_id:
                self._abort_if_unique_id_configured()
            return self.async_update_reload_and_abort(
                entry,
                unique_id=infrared_entity_id,
                data={CONF_INFRARED_ENTITY_ID: infrared_entity_id},
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                probatio.Schema(
                    {
                        probatio.Required(CONF_INFRARED_ENTITY_ID): _emitter_selector(
                            emitter_entity_ids
                        )
                    }
                ),
                entry.data,
            ),
        )
