import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SENSOR_DEFINITIONS = [
    ("Power Usage", ["meterReading", "powerUsage"], "W", "power", "measurement", 1),
    ("Power Delivered High", ["meterReading", "powerDeliverHigh"], "kWh", "energy", "total_increasing", 1000),
    ("Power Delivered Low", ["meterReading", "powerDeliverLow"], "kWh", "energy", "total_increasing", 1000),
    ("Power Returned High", ["meterReading", "powerReturnHigh"], "kWh", "energy", "total_increasing", 1000),
    ("Power Returned Low", ["meterReading", "powerReturnLow"], "kWh", "energy", "total_increasing", 1000),
    ("Gas Consumption", ["meterReading", "gas"], "m³", "gas", "total_increasing", 1000),
    ("Voltage L1", ["meterReading", "voltageL1"], "V", "voltage", "measurement", 1),
    ("Voltage L2", ["meterReading", "voltageL2"], "V", "voltage", "measurement", 1),
    ("Voltage L3", ["meterReading", "voltageL3"], "V", "voltage", "measurement", 1),
    ("Current L1", ["meterReading", "currentL1"], "A", "current", "measurement", 1),
    ("Current L2", ["meterReading", "currentL2"], "A", "current", "measurement", 1),
    ("Current L3", ["meterReading", "currentL3"], "A", "current", "measurement", 1),
    ("Power Usage L1", ["meterReading", "powerUsageL1"], "W", "power", "measurement", 1),
    ("Power Usage L2", ["meterReading", "powerUsageL2"], "W", "power", "measurement", 1),
    ("Power Usage L3", ["meterReading", "powerUsageL3"], "W", "power", "measurement", 1),
    ("Solar Current Output", ["solarReading", "current"], "W", "power", "measurement", 1),
    ("Solar Total Production", ["solarReading", "total"], "kWh", "energy", "total_increasing", 1000),
    ("Dynamic Tariff - Usage", ["dynamicPrices", "usage"], "ct/kWh", None, None, 1),
    ("Dynamic Tariff - Return", ["dynamicPrices", "return"], "ct/kWh", None, None, 1),
    ("Powerbaas WiFi Strength", ["system", "wifiStrength"], "dBm", None, None, 1),
    ("Powerbaas Firmware Version", ["system", "firmwareVersion"], None, None, None, 1),
    ("Powerbaas Uptime", ["system", "upSince"], None, None, None, 1),
]

async def async_setup_entry(hass, entry, async_add_entities):
    coordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    entities = []
    for name, path, unit, device_class, state_class, multiplier in SENSOR_DEFINITIONS:
        unique_id = f"powerbaas_{'_'.join(path).lower()}"
        entities.append(
            PowerBaasSensor(
                coordinator,
                name,
                path,
                unit,
                device_class,
                state_class,
                unique_id,
                multiplier,
            )
        )

    async_add_entities(entities, True)

class PowerBaasSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, name, path, unit, device_class, state_class, unique_id, multiplier):
        super().__init__(coordinator)
        self._attr_name = name
        self._path = path
        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_unique_id = unique_id
        self._multiplier = multiplier
        self._last_value = None 

    @property
    def native_value(self):
        data = self.coordinator.data
        try:
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
