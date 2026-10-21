import logging
from pathlib import Path
from typing import Any
from homeassistant.components.http import StaticPathConfig
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_call_later
from ..const import JSMODULES, URL_BASE

_LOGGER = logging.getLogger(__name__)

class JSModuleRegistration:
    def __init__(self, hass: HomeAssistant) -> None:
        self.hass = hass
        self.lovelace = self.hass.data.get("lovelace")

    async def async_register(self) -> None:
        await self._async_register_path()
        if self.lovelace and self.lovelace.mode == "storage":
            await self._async_wait_for_lovelace_resources()

    async def _async_register_path(self) -> None:
        try:
            await self.hass.http.async_register_static_paths(
                [StaticPathConfig(URL_BASE, Path(__file__).parent, False)]
            )
        except RuntimeError:
            pass

    async def _async_wait_for_lovelace_resources(self) -> None:
        async def _check_loaded(_now: Any) -> None:
            if self.lovelace.resources.loaded:
                await self._async_register_modules()
            else:
                async_call_later(self.hass, 5, _check_loaded)
        await _check_loaded(0)

    async def _async_register_modules(self) -> None:
        existing = [
            r for r in self.lovelace.resources.async_items()
            if r["url"].startswith(URL_BASE)
        ]
        for module in JSMODULES:
            url = f"{URL_BASE}/{module['filename']}"
            if any(res["url"].split("?")[0] == url for res in existing):
                continue
            await self.lovelace.resources.async_create_item({
                "res_type": "module",
                "url": f"{url}?v={module['version']}",
            })