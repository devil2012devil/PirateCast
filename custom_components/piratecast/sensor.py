
"""Sensors for PirateCast."""

from __future__ import annotations

import logging
import math
from datetime import timedelta

from homeassistant.components.recorder import get_instance, history
from homeassistant.components.sensor import (
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPressure
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from .const import (
    DEFAULT_WINDOWS_HOURS,
    PRESSURE_UNIT_MMHG,
    SCAN_INTERVAL_MINUTES,
)

_LOGGER = logging.getLogger(__name__)

SCAN_INTERVAL = timedelta(minutes=SCAN_INTERVAL_MINUTES)

# Conversion factors to mmHg.
# Pressure differences use the same linear conversion as pressure values.
UNIT_TO_MMHG = {
    "mmhg": 1.0,
    "mm hg": 1.0,
    "hpa": 0.750061683,
    "mbar": 0.750061683,
    "pa": 0.00750061683,
    "kpa": 7.50061683,
    "inhg": 25.4,
    "in hg": 25.4,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up PirateCast sensors."""
    source_entity = entry.data["source_entity"]

    async_add_entities(
        [
            PirateCastPressureChange(source_entity, hours)
            for hours in DEFAULT_WINDOWS_HOURS
        ],
        update_before_add=True,
    )


class PirateCastPressureChange(SensorEntity):
    """Report pressure change over a selected time window."""

    _attr_has_entity_name = False
    _attr_native_unit_of_measurement = UnitOfPressure.MMHG
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_icon = "mdi:gauge"

    def __init__(self, source_entity: str, hours: int) -> None:
        """Initialize the pressure-change sensor."""
        self._source_entity = source_entity
        self._hours = hours

        self._attr_name = f"Изменение давления за {hours} ч"
        self._attr_unique_id = (
            f"{source_entity}_pressure_change_{hours}h"
        )
        self._attr_suggested_object_id = (
            f"piratecast_pressure_change_{hours}h"
        )

        self._attr_native_value = None
        self._attr_available = False

    async def async_update(self) -> None:
        """Calculate pressure change from recorder history."""
        source_state = self.hass.states.get(self._source_entity)

        if source_state is None or source_state.state in (
            "unknown",
            "unavailable",
        ):
            self._attr_native_value = None
            self._attr_available = False
            return

        source_unit = source_state.attributes.get("unit_of_measurement")

        if not source_unit:
            _LOGGER.warning(
                "PirateCast: source sensor %s has no unit",
                self._source_entity,
            )
            self._attr_native_value = None
            self._attr_available = False
            return

        factor = UNIT_TO_MMHG.get(
            str(source_unit).strip().lower()
        )

        if factor is None:
            _LOGGER.warning(
                "PirateCast: unsupported pressure unit %s for sensor %s",
                source_unit,
                self._source_entity,
            )
            self._attr_native_value = None
            self._attr_available = False
            return

        end_time = dt_util.utcnow()
        start_time = end_time - timedelta(hours=self._hours)

        try:
            states = await get_instance(
                self.hass
            ).async_add_executor_job(
                history.state_changes_during_period,
                self.hass,
                start_time,
                end_time,
                self._source_entity,
            )
        except Exception:
            _LOGGER.exception(
                "PirateCast: failed to read history for %s",
                self._source_entity,
            )
            self._attr_native_value = None
            self._attr_available = False
            return

        series = states.get(self._source_entity, [])
        numeric_values = []

        for state in series:
            try:
                value = float(state.state)
            except (ValueError, TypeError):
                continue

            if math.isfinite(value):
                numeric_values.append(value)

        if len(numeric_values) < 2:
            self._attr_native_value = None
            self._attr_available = False
            return

        first_value = numeric_values[0]
        last_value = numeric_values[-1]

        change_mmhg = (last_value - first_value) * factor

        self._attr_native_value = round(change_mmhg, 2)
        self._attr_available = True

    @property
    def extra_state_attributes(self) -> dict:
        """Return additional sensor information."""
        return {
            "source_entity": self._source_entity,
            "period_hours": self._hours,
            "unit_of_measurement": PRESSURE_UNIT_MMHG,
        }
