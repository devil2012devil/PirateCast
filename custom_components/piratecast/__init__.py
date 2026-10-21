"""PirateCast integration."""

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from .const import DOMAIN

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
"""Set up PirateCast."""
hass.data.setdefault(DOMAIN, {})
return True

async def async_setup_entry(
hass: HomeAssistant,
entry: ConfigEntry,
) -> bool:
"""Set up PirateCast from a config entry."""
hass.data.setdefault(DOMAIN, {})

await hass.config_entries.async_forward_entry_setups(
    entry,
    ["sensor"],
)

return True

async def async_unload_entry(
hass: HomeAssistant,
entry: ConfigEntry,
) -> bool:
"""Unload PirateCast config entry."""
return await hass.config_entries.async_unload_platforms(
entry,
["sensor"],
)
