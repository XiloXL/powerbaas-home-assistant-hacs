import logging
from urllib.parse import urlparse

import aiohttp
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback

from .const import DOMAIN, DEFAULT_SCAN_INTERVAL, MIN_SCAN_INTERVAL, MAX_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)
DEFAULT_HOST = "http://192.168.x.x"
DEFAULT_NAME = "Powerbaas"

SCAN_INTERVAL_SCHEMA = vol.All(
    vol.Coerce(int), vol.Range(min=MIN_SCAN_INTERVAL, max=MAX_SCAN_INTERVAL)
)


def _is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


async def _test_connection(host):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(host, timeout=aiohttp.ClientTimeout(total=10)) as response:
                return response.status < 400
    except Exception as err:
        _LOGGER.debug("Connection test failed for %s: %s", host, err)
        return False


class PowerbaasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input["host"].rstrip("/")
            name = user_input.get("name") or DEFAULT_NAME

            if not _is_valid_url(host):
                errors["host"] = "invalid_host"
            elif not await _test_connection(host):
                errors["host"] = "cannot_connect"
            else:
                user_input["host"] = host
                user_input["name"] = name
                return self.async_create_entry(title=name, data=user_input)

        schema = vol.Schema({
            vol.Required("host", default=DEFAULT_HOST): str,
            vol.Optional("name", default=DEFAULT_NAME): str,
            vol.Required("scan_interval", default=DEFAULT_SCAN_INTERVAL): SCAN_INTERVAL_SCHEMA,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PowerbaasOptionsFlow()


class PowerbaasOptionsFlow(config_entries.OptionsFlow):

    async def async_step_init(self, user_input=None):
        errors = {}

        if user_input is not None:
            host = user_input["host"].rstrip("/")

            if not _is_valid_url(host):
                errors["host"] = "invalid_host"
            elif not await _test_connection(host):
                errors["host"] = "cannot_connect"
            else:
                new_data = dict(self.config_entry.data)
                new_data["host"] = host
                new_data["scan_interval"] = user_input["scan_interval"]

                self.hass.config_entries.async_update_entry(
                    self.config_entry, data=new_data
                )
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)

                return self.async_create_entry(title="", data={})

        schema = vol.Schema({
            vol.Required("host", default=self.config_entry.data.get("host", DEFAULT_HOST)): str,
            vol.Required(
                "scan_interval",
                default=self.config_entry.data.get("scan_interval", DEFAULT_SCAN_INTERVAL),
            ): SCAN_INTERVAL_SCHEMA,
        })

        return self.async_show_form(step_id="init", data_schema=schema, errors=errors)
