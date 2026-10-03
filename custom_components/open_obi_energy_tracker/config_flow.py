"""Config flow for the Open OBI Energy Tracker integration."""

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN, LOGGER
from .OpenEnergyTrackerGateway import OpenEnergyTrackerGateway

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_USERNAME): str,
        vol.Optional(CONF_PASSWORD): str,
    }
)

async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from CONFIG_SCHEMA with values provided by the user.
    """
    # TODO validate the data can be used to set up a connection.

    # If your PyPI package is not built with async, pass your methods
    # to the executor:
    # await hass.async_add_executor_job(
    #     your_validate_func, data[CONF_USERNAME], data[CONF_PASSWORD]
    # )

    hub = OpenEnergyTrackerGateway(data[CONF_HOST], session=async_get_clientsession(hass))

    if not await hub.update():
        raise CannotConnect

    #if not await hub.authenticate(data[CONF_USERNAME], data[CONF_PASSWORD]):
    #    raise InvalidAuth

    # Return info that you want to store in the config entry.
    return {"serial": hub.serial_number, "name": hub.gateway_name }


class ConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Open OBI Energy Tracker."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                self._async_abort_entries_match({CONF_HOST: user_input[CONF_HOST]})
                info = await validate_input(self.hass, user_input)
                await self.async_set_unique_id(info['serial'])
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            else:
                return self.async_create_entry(title=info["name"], data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors
        )


class CannotConnect(Exception):
    """Error to indicate we cannot connect."""


class InvalidAuth(Exception):
    """Error to indicate there is invalid auth."""
