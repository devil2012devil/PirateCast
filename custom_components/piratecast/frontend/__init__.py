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

    async def async_register(self) -> None:
        # 1. Сначала всегда регистрируем статический путь (это можно делать сразу)
        await self._async_register_path()
        # 2. Затем пробуем зарегистрировать ресурс в Lovelace (с ожиданием)
        await self._async_wait_for_lovelace_resources()

    async def _async_register_path(self) -> None:
        try:
            await self.hass.http.async_register_static_paths(
                [StaticPathConfig(URL_BASE, Path(__file__).parent, False)]
            )
            _LOGGER.debug("PirateCast: static path registered: %s", URL_BASE)
        except RuntimeError:
            _LOGGER.debug("PirateCast: static path already registered")

    async def _async_wait_for_lovelace_resources(self) -> None:
        async def _check_loaded(_now: Any) -> None:
            lovelace = self.hass.data.get("lovelace")
            if lovelace and getattr(lovelace, "resources", None):
                # Дополнительно проверяем, что коллекция ресурсов загружена
                if getattr(lovelace.resources, "loaded", False):
                    await self._async_register_modules(lovelace)
                    return
            # Если ещё не готово — пробуем снова через 5 секунд
            async_call_later(self.hass, 5, _check_loaded)

        await _check_loaded(0)

    async def _async_register_modules(self, lovelace) -> None:
        existing = [
            r for r in lovelace.resources.async_items()
            if r["url"].startswith(URL_BASE)
        ]
        for module in JSMODULES:
            url = f"{URL_BASE}/{module['filename']}"
            if any(res["url"].split("?")[0] == url for res in existing):
                continue
            try:
                await lovelace.resources.async_create_item({
                    "res_type": "module",
                    "url": f"{url}?v={module['version']}",
                })
                _LOGGER.info("PirateCast: card registered: %s", url)
            except Exception as err:
                _LOGGER.warning("PirateCast: failed to register card: %s", err)