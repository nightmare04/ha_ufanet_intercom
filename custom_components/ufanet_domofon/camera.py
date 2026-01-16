"""Camera platform for Ufanet Domofon."""

import logging

from homeassistant.components.camera import Camera, CameraEntityDescription, CameraEntityFeature
from homeassistant.components.camera.const import StreamType
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
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
    for data in coordinator.domofons_cameras.values():
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

    _attr_has_entity_name = True
    _attr_supported_features = CameraEntityFeature.STREAM
    _attr_frontend_stream_type = StreamType.HLS
    _attr_motion_detection_enabled = False

    entity_description = CameraEntityDescription(
        key="camera",
        icon="mdi:doorbell-video",
    )

    def __init__(self, coordinator, camera_data):
        """Initialize."""
        CoordinatorEntity.__init__(self, coordinator)
        Camera.__init__(self)

        self._camera_data = camera_data
        self._number = camera_data.get("number")
        self._unique_id = f"ufanet_camera_{self._number}"
        self._attr_unique_id = self._unique_id

    @property
    def use_stream_for_stills(self) -> bool:
        """Use stream to generate stills."""
        return True

    async def stream_source(self) -> str | None:
        """Return the stream source."""
        return self._camera_data.get("stream_source")


class DomofonCamera(UfanetCamera):
    """Camera attached to a domofon."""

    def __init__(self, coordinator, domofon_data, camera_data):
        """Initialize."""
        super().__init__(coordinator, camera_data)

        self._domofon_data = domofon_data
        self.entity_id = f"camera.domofon_{domofon_data['id']}"
        self._attr_name = f"Камера {self._domofon_data.get('custom_name', '')}"
        self._attr_unique_id = f"ufanet_domofon_{domofon_data['id']}_camera"

    @property
    def device_info(self):
        """Return device information for linking entities."""
        return {
            "identifiers": {(DOMAIN, self._domofon_data["id"])},
            "name": f"Домофон {self._domofon_data.get('custom_name', '')}",
            "manufacturer": "Ufanet",
        }


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
