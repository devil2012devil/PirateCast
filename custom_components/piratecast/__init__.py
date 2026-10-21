import logging
from homeassistant.core import HomeAssistant, CoreState, EVENT_HOMEASSISTANT_STARTED
from .const import DOMAIN
from .frontend import JSModuleRegistration

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    async def _setup_frontend(_event=None) -> None:
        await JSModuleRegistration(hass).async_register()

    if hass.state == CoreState.running:
        await _setup_frontend()
    else:
        hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STARTED, _setup_frontend)
    return True

async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])
    return True

async def async_unload_entry(hass: HomeAssistant, entry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, ["sensor"])