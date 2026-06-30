import aiohttp
import asyncio
import logging
from datetime import datetime, timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.util import slugify

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

LEGACY_UNIQUE_ID_PREFIX = f"{DOMAIN}_"


def _migrate_legacy_entities(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Move entities created before the per-device unique_id/entity_id scheme.

    Old unique_id: "powerbaas_<path>" (no entry_id -> orphaned once we switched
    to "<entry_id>_<path>" to support multiple devices). Renaming here keeps the
    existing entity_id/history/automations instead of creating a duplicate entity.
    """
    registry = er.async_get(hass)
    new_prefix = f"{entry.entry_id}_"
    device_slug = slugify(entry.title or DOMAIN)

    for reg_entry in er.async_entries_for_config_entry(registry, entry.entry_id):
        if reg_entry.platform != DOMAIN:
            continue
        if not reg_entry.unique_id.startswith(LEGACY_UNIQUE_ID_PREFIX):
            continue
        if reg_entry.unique_id.startswith(new_prefix):
            continue

        suffix = reg_entry.unique_id[len(LEGACY_UNIQUE_ID_PREFIX):]
        updates = {"new_unique_id": f"{new_prefix}{suffix}"}

        domain, object_id = reg_entry.entity_id.split(".", 1)
        if not object_id.startswith(f"{device_slug}_"):
            new_entity_id = f"{domain}.{device_slug}_{object_id}"
            if not registry.async_get(new_entity_id):
                updates["new_entity_id"] = new_entity_id

        _LOGGER.info(
            "Migrating legacy Powerbaas entity %s to unique_id=%s entity_id=%s",
            reg_entry.entity_id,
            updates["new_unique_id"],
            updates.get("new_entity_id", reg_entry.entity_id),
        )
        registry.async_update_entity(reg_entry.entity_id, **updates)


async def async_migrate_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Migrate an old config entry to the current version."""
    if entry.version == 1:
        _migrate_legacy_entities(hass, entry)
        hass.config_entries.async_update_entry(entry, version=2)
        _LOGGER.info("Powerbaas entry %s migrated to version 2", entry.entry_id)

    return True


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
