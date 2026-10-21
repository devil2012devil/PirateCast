"""Сенсоры PirateCast: изменение давления за 1 и 3 часа."""
from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.const import UnitOfPressure
from homeassistant.core import HomeAssistant
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.util import dt as dt_util

from .const import DEFAULT_WINDOWS_HOURS

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=5)


async def async_setup_entry(hass: HomeAssistant, entry, async_add_entities):
    source = entry.data["source_entity"]
    entities = [PirateCastPressureChange(source, h) for h in DEFAULT_WINDOWS_HOURS]
    async_add_entities(entities, update_before_add=True)


class PirateCastPressureChange(SensorEntity):
    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = UnitOfPressure.MMHG
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:gauge"

    def __init__(self, source_entity: str, hours: int) -> None:
        self._source = source_entity
        self._hours = hours
        self._attr_name = f"Изменение давления за {hours} ч"
        self._attr_unique_id = f"piratecast_pressure_change_{hours}h"
        self._attr_native_value = None

    async def async_update(self) -> None:
        # Получаем историю источника за нужный интервал
        from homeassistant.components.recorder import get_instance, history

        start = dt_util.utcnow() - timedelta(hours=self._hours)
        states = await get_instance(self.hass).async_add_executor_job(
            history.state_changes_during_period,
            self.hass,
            start,
            dt_util.utcnow(),
            self._source,
        )
        series = states.get(self._source, [])
        if len(series) < 2:
            self._attr_native_value = None
            return
        try:
            first = float(series[0].state)
            last = float(series[-1].state)
        except (ValueError, TypeError):
            self._attr_native_value = None
            return
        self._attr_native_value = round(last - first, 2)