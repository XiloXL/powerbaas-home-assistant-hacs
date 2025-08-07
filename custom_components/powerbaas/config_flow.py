from homeassistant import config_entries
from homeassistant.core import callback
import voluptuous as vol
from .const import DOMAIN

DEFAULT_HOST = "http://192.168.x.x"

class PowerbaasConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        errors = {}

        if user_input is not None:
            # TODO: eventueel verbinding testen met het opgegeven adres
            return self.async_create_entry(title="Powerbaas", data=user_input)

        schema = vol.Schema({
            vol.Required("host", default=DEFAULT_HOST): str,
        })

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return PowerbaasOptionsFlow(config_entry)


class PowerbaasOptionsFlow(config_entries.OptionsFlow):
    def __init__(self, config_entry):
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        schema = vol.Schema({
            vol.Required("host", default=self.config_entry.data.get("host", DEFAULT_HOST)): str,
        })

        return self.async_show_form(step_id="init", data_schema=schema)
