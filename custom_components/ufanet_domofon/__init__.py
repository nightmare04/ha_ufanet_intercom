"""The Ufanet Domofon integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryAuthFailed

from .const import DOMAIN, PLATFORMS
from .coordinator import UfanetDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ufanet Domofon from a config entry."""

    coordinator = UfanetDataUpdateCoordinator(hass, entry)

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        if "auth" in str(err).lower():
            raise ConfigEntryAuthFailed from err
        raise

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok and DOMAIN in hass.data:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
