from homeassistant.helpers.entity import EntityCategory

DOMAIN = "powerbaas"

DEFAULT_SCAN_INTERVAL = 15
MIN_SCAN_INTERVAL = 5
MAX_SCAN_INTERVAL = 60

# Main reading sensors - primary energy data
MAIN_SENSORS = [
    ("Power Usage", ["meterReading", "powerUsage"], "W", "power", "measurement", 1, None),
    ("Power Delivered High", ["meterReading", "powerDeliverHigh"], "kWh", "energy", "total_increasing", 1000, None),
    ("Power Delivered Low", ["meterReading", "powerDeliverLow"], "kWh", "energy", "total_increasing", 1000, None),
    ("Power Returned High", ["meterReading", "powerReturnHigh"], "kWh", "energy", "total_increasing", 1000, None),
    ("Power Returned Low", ["meterReading", "powerReturnLow"], "kWh", "energy", "total_increasing", 1000, None),
    ("Gas Consumption", ["meterReading", "gas"], "m³", "gas", "total_increasing", 1000, None),
    ("Voltage L1", ["meterReading", "voltageL1"], "V", "voltage", "measurement", 1, None),
    ("Voltage L2", ["meterReading", "voltageL2"], "V", "voltage", "measurement", 1, None),
    ("Voltage L3", ["meterReading", "voltageL3"], "V", "voltage", "measurement", 1, None),
    ("Current L1", ["meterReading", "currentL1"], "A", "current", "measurement", 1, None),
    ("Current L2", ["meterReading", "currentL2"], "A", "current", "measurement", 1, None),
    ("Current L3", ["meterReading", "currentL3"], "A", "current", "measurement", 1, None),
    ("Power Usage L1", ["meterReading", "powerUsageL1"], "W", "power", "measurement", 1, None),
    ("Power Usage L2", ["meterReading", "powerUsageL2"], "W", "power", "measurement", 1, None),
    ("Power Usage L3", ["meterReading", "powerUsageL3"], "W", "power", "measurement", 1, None),
    ("Solar Current Output", ["solarReading", "current"], "W", "power", "measurement", 1, None),
    ("Solar Total Production", ["solarReading", "total"], "kWh", "energy", "total_increasing", 1000, None),
    ("Dynamic Tariff - Usage", ["dynamicPrices", "usage"], "ct/kWh", None, None, 1, None),
    ("Dynamic Tariff - Return", ["dynamicPrices", "return"], "ct/kWh", None, None, 1, None),
]

# Diagnostic sensors - device and system information
DIAGNOSTIC_SENSORS = [
    ("Powerbaas WiFi Strength", ["system", "wifiStrength"], "dBm", "signal_strength", "measurement", 1, EntityCategory.DIAGNOSTIC),
    ("Powerbaas Firmware Version", ["system", "firmwareVersion"], None, None, None, 1, EntityCategory.DIAGNOSTIC),
    ("Powerbaas Uptime", ["system", "upSince"], None, "timestamp", None, 1, EntityCategory.DIAGNOSTIC),
    ("Powerbaas Last Updated", ["_last_update"], None, "timestamp", None, 1, EntityCategory.DIAGNOSTIC),
]
