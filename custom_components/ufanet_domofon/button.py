"""Button platform for Ufanet Domofon."""

from datetime import datetime
import logging

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_LAST_OPENED, DOMAIN
from .coordinator import UfanetDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ufanet buttons from a config entry."""
    coordinator: UfanetDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for domofon in coordinator.domofons:
        entities.append(OpenDoorButton(coordinator, domofon))  # noqa: PERF401

    async_add_entities(entities, True)


class OpenDoorButton(CoordinatorEntity, ButtonEntity):
    """Button to open a domofon door."""

    def __init__(self, coordinator, domofon_data):
        """Initialize."""
        super().__init__(coordinator)

        self._domofon_data = domofon_data
        self._domofon_id = domofon_data.get("id")
        self._domofon_name = domofon_data.get("custom_name", "Domofon")
        self._last_opened = None

        self._attr_name = f"{self._domofon_name} Open Door"
        self._attr_unique_id = f"ufanet_domofon_{self._domofon_id}_button"
        self._attr_icon = "mdi:door-open"

        self._attr_extra_state_attributes = {
            "domofon_id": self._domofon_id,
            "domofon_name": self._domofon_name,
            ATTR_LAST_OPENED: self._last_opened,
        }

    @property
    def device_info(self):
        """Return device information for linking entities."""
        return {
            "identifiers": {(DOMAIN, self._domofon_id)},
            "name": self._domofon_name,
            "manufacturer": "Ufanet",
            "model": "Domofon System",
        }

    async def async_press(self) -> None:
        """Handle the button press."""
        success = await self.coordinator.async_open_door(self._domofon_id)  # type: ignore  # noqa: PGH003

        if success:
            self._last_opened = datetime.now().isoformat()
            self._attr_extra_state_attributes[ATTR_LAST_OPENED] = self._last_opened

            # Fire an event for automations
            self.hass.bus.async_fire(
                "ufanet_door_opened",
                {"domofon_id": self._domofon_id, "name": self._domofon_name, "timestamp": self._last_opened},
            )

            _LOGGER.info("Door opened for %s", self._domofon_name)
        else:
            _LOGGER.error("Failed to open door for %s", self._domofon_name)

        self.async_write_ha_state()
