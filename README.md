# powerbaas-home-assistant-hacs
Powerbaas Home Assistant HACS

This Home Assistant integration connects your Powerbaas device to Home Assistant, allowing you to monitor your energy meter, solar and dynamic tariff data directly in your smart home dashboard.

## Features

- **Energy meter data**: power usage, delivered/returned energy (high/low tariff), gas consumption, per-phase voltage and current
- **Solar production**: current output and total production
- **Dynamic tariffs**: usage and return price per kWh
- **Device page**: all sensors are grouped under a single Powerbaas device, with a separate "Diagnostics" section for WiFi strength, firmware version, uptime and last update
- **Multiple devices**: add more than one Powerbaas device by giving each its own name during setup
- **Smart data handling**: energy totals never drop to zero on a temporary glitch (monotonic increasing)

## Installation

### Via HACS (Recommended)
1. Open HACS in Home Assistant
2. Go to "Integrations"
3. Click the three dots in the top right corner
4. Select "Custom repositories"
5. Add this repository URL
6. Select "Integration" as category
7. Click "Add"
8. Find "Powerbaas" in the integration list and install it

### Manual Installation
1. Copy the `custom_components/powerbaas` folder to your Home Assistant `custom_components` directory
2. Restart Home Assistant
3. Go to Settings → Devices & Services → Add Integration
4. Search for "Powerbaas" and add it

## Configuration

1. Go to Settings → Devices & Services → Add Integration
2. Search for "Powerbaas"
3. Enter the IP address of your Powerbaas device (e.g. `http://192.168.1.100`) and optionally a name
4. The integration will create a device with all available sensors

If your device's IP address changes later, go to the integration's options to update the host without removing and re-adding it.

## Upgrading from 1.1.0 to 1.2.0

> **Important:** entity names changed in 1.2.0. Every entity now gets your device's name as a prefix (e.g. `sensor.power_delivered_low` becomes `sensor.powerbaas_power_delivered_low`, based on the name you gave the device during setup).

This happens automatically the first time the integration reloads after updating — your existing entities are renamed in place, so their history, statistics and `unique_id` are preserved, no duplicates are created. However, **any automation, script or dashboard card that references the old entity ID directly will need to be updated** to the new, prefixed entity ID.

## Sensors Created

### Main sensors
- `Power Usage` - Current power usage (W)
- `Power Delivered High` / `Power Delivered Low` - Energy delivered to the home (kWh)
- `Power Returned High` / `Power Returned Low` - Energy returned to the grid (kWh)
- `Gas Consumption` - Gas usage (m³)
- `Voltage L1/L2/L3` - Voltage per phase (V)
- `Current L1/L2/L3` - Current per phase (A)
- `Power Usage L1/L2/L3` - Power usage per phase (W)
- `Solar Current Output` - Current solar power production (W)
- `Solar Total Production` - Total solar energy produced (kWh)
- `Dynamic Tariff - Usage` / `Dynamic Tariff - Return` - Dynamic energy prices (ct/kWh)

### Diagnostic sensors
- `Powerbaas WiFi Strength` - WiFi signal strength (dBm)
- `Powerbaas Firmware Version` - Firmware version
- `Powerbaas Uptime` - Device boot time (timestamp)
- `Powerbaas Last Updated` - Last data fetch timestamp

## Support

For issues related to this Home Assistant integration, please use the GitHub Issues page of this repository.

For questions about the Powerbaas device itself, visit [powerbaas.nl](https://www.powerbaas.nl).
