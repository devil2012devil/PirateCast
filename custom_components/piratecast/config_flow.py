
"""Config flow for PirateCast."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import DOMAIN


class PirateCastConfigFlow(
    config_entries.ConfigFlow,
    domain=DOMAIN,
):
    """Handle a config flow for PirateCast."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial setup step."""
        if user_input is not None:
            source_entity = user_input["source_entity"]

            await self.async_set_unique_id(
                f"{DOMAIN}_{source_entity}"
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title="PirateCast",
                data=user_input,
            )

        schema = vol.Schema(
            {
                vol.Required("source_entity"): selector.EntitySelector(
                    selector.EntitySelectorConfig(
                        domain="sensor",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )
