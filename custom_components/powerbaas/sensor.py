import logging
from datetime import datetime

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.util import dt as dt_util

from .const import DOMAIN, MAIN_SENSORS, DIAGNOSTIC_SENSORS

_LOGGER = logging.getLogger(__name__)


def _parse_timestamp(value):
    """Parse a timestamp string (ISO or 'YYYY-MM-DD HH:MM:SS') into a local datetime."""
    if not value:
        return None
    try:
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            dt = datetime.strptime(str(value), "%Y-%m-%d %H:%M:%S")
        if dt.tzinfo is None:
            dt = dt_util.as_local(dt)
        return dt
    except ValueError as err:
        _LOGGER.warning("Error parsing timestamp %s: %s", value, err)
        return None


async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]
    host_url = hass.data[DOMAIN][entry.entry_id]["host"]
    device_name = hass.data[DOMAIN][entry.entry_id]["name"]

    entities = []
    for name, path, unit, device_class, state_class, multiplier, entity_category in MAIN_SENSORS + DIAGNOSTIC_SENSORS:
        unique_id = f"{entry.entry_id}_{'_'.join(path).lower()}"
        entities.append(
            PowerBaasSensor(
                coordinator,
                entry.entry_id,
                device_name,
                host_url,
                name,
                path,
                unit,
                device_class,
                state_class,
                unique_id,
                multiplier,
                entity_category,
            )
        )

    async_add_entities(entities, True)

class PowerBaasSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, entry_id, device_name, host_url, name, path, unit, device_class, state_class, unique_id, multiplier, entity_category=None):
        super().__init__(coordinator)
        self._attr_name = name
        self._path = path
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_unique_id = unique_id
        self._attr_entity_category = entity_category
        self._multiplier = multiplier
        self._last_value = None

        config_url = host_url
        if host_url and not host_url.startswith(("http://", "https://")):
            config_url = f"http://{host_url}"

        system_data = coordinator.data.get("system", {}) if coordinator.data else {}

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, entry_id)},
            name=device_name,
            manufacturer="Powerbaas",
            model="Energy Monitor",
            sw_version=str(system_data.get("firmwareVersion", "Unknown")),
            configuration_url=config_url,
        )

    @property
    def native_value(self):
        data = self.coordinator.data
        try:
            if self._attr_device_class == "timestamp":
                for key in self._path:
                    data = data.get(key, {}) if isinstance(data, dict) else None
                return _parse_timestamp(data) if isinstance(data, str) else None

            for key in self._path:
                data = data.get(key, {})

            if isinstance(data, (int, float)):
                value = data / self._multiplier if self._multiplier else data

                if (
                    self._attr_state_class == "total_increasing"
                    and value == 0
                    and self._last_value not in (None, 0)
                ):
                    return self._last_value

                self._last_value = value
                return value

            return data

        except Exception as err:
            _LOGGER.warning("Error accessing sensor path %s: %s", self._path, err)
            return None
