"""Config flow for Ufanet Domofon."""

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_CONTRACT, CONF_PASSWORD, DOMAIN

_LOGGER = logging.getLogger(__name__)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input."""
    # Basic validation
    if not data.get(CONF_CONTRACT) or not data.get(CONF_PASSWORD):
        raise InvalidAuth("Contract number and password are required")

    # Additional validation can be added here
    return {"title": f"Ufanet Domofon ({data[CONF_CONTRACT]})"}


class UfanetConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ufanet Domofon."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                await self.async_set_unique_id(user_input[CONF_CONTRACT])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)
            except InvalidAuth:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        data_schema = vol.Schema(
            {
                vol.Required(CONF_CONTRACT): str,
                vol.Required(CONF_PASSWORD): str,
            }
        )

        return self.async_show_form(step_id="user", data_schema=data_schema, errors=errors)


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
