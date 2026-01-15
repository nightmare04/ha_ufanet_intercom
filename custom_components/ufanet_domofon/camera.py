"""Camera platform for Ufanet Domofon."""

import logging

from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import ATTR_ADDRESS, ATTR_LATITUDE, ATTR_LONGITUDE, DOMAIN
from .coordinator import UfanetDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Ufanet cameras from a config entry."""
    coordinator: UfanetDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    # Add cameras attached to domofons
    for data in coordinator.domofons_cameras.values():  # type: ignore  # noqa: PGH003
        if data["camera"]:
            domofon = data["domofon"]
            camera = data["camera"]
            entities.append(DomofonCamera(coordinator, domofon, camera))

    # Add standalone cameras
    for camera in coordinator.standalone_cameras:
        alone_camera = StandaloneCamera(coordinator, camera)
        entities.append(alone_camera)

    async_add_entities(entities, True)


class UfanetCamera(CoordinatorEntity, Camera):
    """Base class for Ufanet cameras."""

    def __init__(self, coordinator, camera_data):
        """Initialize."""
        CoordinatorEntity.__init__(self, coordinator)
        Camera.__init__(self)

        self._camera_data = camera_data
        self._number = camera_data.get("number")
        self._unique_id = f"ufanet_camera_{self._number}"
        self._attr_unique_id = self._unique_id
        self._attr_extra_state_attributes = {
            ATTR_ADDRESS: camera_data.get("address"),
            ATTR_LATITUDE: camera_data.get("latitude"),
            ATTR_LONGITUDE: camera_data.get("longitude"),
        }

    @property
    def use_stream_for_stills(self) -> bool:
        """Use stream to generate stills."""
        return True


class DomofonCamera(UfanetCamera):
    """Camera attached to a domofon."""

    def __init__(self, coordinator, domofon_data, camera_data):
        """Initialize."""
        super().__init__(coordinator, camera_data)

        self._domofon_data = domofon_data
        self.entity_id = f"camera.domofon_{domofon_data['id']}"
        self._attr_friendly_name = "Камера домофона"
        self.device_name = f"Домофон {camera_data.get('title', '')}"
        self._attr_name = "Камера"
        self._attr_unique_id = f"ufanet_domofon_{domofon_data['id']}_camera"
        self._attr_extra_state_attributes.update(
            {"domofon_id": domofon_data.get("id"), "camera_name": self.device_name}
        )

    @property
    def device_info(self):
        """Return device information for linking entities."""
        return {
            "identifiers": {(DOMAIN, self._domofon_data["id"])},
            "name": self.device_name,
            "manufacturer": "Ufanet",
        }

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Камера"

    def stream_source(self) -> str | None:
        """Return the stream source."""
        return self._camera_data.get("stream_source")


class StandaloneCamera(UfanetCamera):
    """Standalone camera not attached to any domofon."""

    def __init__(self, coordinator, camera_data):
        """Initialize."""
        super().__init__(coordinator, camera_data)
        self._name = camera_data.get("title", f"Camera {self._number}")
        self._attr_name = self._name

    @property
    def device_info(self):
        """Return device information for linking entities."""
        return {
            "identifiers": {(DOMAIN, "standalone_camera")},
            "name": "Камеры Ufanet",
            "manufacturer": "Ufanet",
        }

    def stream_source(self) -> str | None:
        """Return the stream source."""
        return self._camera_data.get("stream_source")
