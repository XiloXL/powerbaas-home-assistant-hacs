import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    api_url = entry.data.get("host")
    scan_interval = entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL)

    if not api_url:
        _LOGGER.error("Geen hostadres opgegeven voor Powerbaas.")
        raise ConfigEntryNotReady("Geen hostadres beschikbaar.")

    async def async_update_data():
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                    response.raise_for_status()
                    data = await response.json()
                    data["_last_update"] = datetime.now().isoformat()
                    return data
        except asyncio.TimeoutError:
            _LOGGER.error("Timeout bij het ophalen van data van Powerbaas API (%s)", api_url)
            raise
        except aiohttp.ClientError as err:
            _LOGGER.error("HTTP-fout bij het ophalen van data van Powerbaas API (%s): %s", api_url, err)
            raise

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=DOMAIN,
        update_method=async_update_data,
        update_interval=timedelta(seconds=scan_interval),
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "coordinator": coordinator,
        "host": api_url,
        "name": entry.title or "Powerbaas",
    }

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    unload_ok = await hass.config_entries.async_unload_platforms(entry, ["sensor"])
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    return unload_ok
