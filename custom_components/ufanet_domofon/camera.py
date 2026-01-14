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
    for domofon_camera in coordinator.domofon_camera_map.values():
        if domofon_camera["camera"]:
            domofon = domofon_camera["domofon"]
            camera = domofon_camera["camera"]
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
        self._name = camera_data.get("title", f"Camera {self._number}")
        self._unique_id = f"ufanet_camera_{self._number}"

        self._attr_name = self._name
        self._attr_unique_id = self._unique_id
        self._attr_extra_state_attributes = {
            ATTR_ADDRESS: camera_data.get("address"),
            ATTR_LATITUDE: camera_data.get("latitude"),
            ATTR_LONGITUDE: camera_data.get("longitude"),
            "camera_type": camera_data.get("type", "unknown"),
            "vendor": camera_data.get("servers", {}).get("vendor_name", "Ufanet"),
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
        domofon_name = domofon_data.get("name", "Domofon")

        self._attr_name = f"{domofon_name} Camera"
        self._attr_unique_id = f"ufanet_domofon_{domofon_data['id']}_camera"

        self._attr_extra_state_attributes.update({"domofon_id": domofon_data.get("id"), "domofon_name": domofon_name})

    @property
    def device_info(self):
        """Return device information for linking entities."""
        return {
            "identifiers": {(DOMAIN, self._domofon_data["id"])},
            "name": self._domofon_data.get("name", "Domofon"),
            "manufacturer": "Ufanet",
            "model": "Domofon System",
        }

    # async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
    #     """Return bytes of camera image."""
    #     if "still_image_url" in self._camera_data:
    #         # Fetch from screenshot endpoint
    #         try:
    #             session = self.coordinator._session
    #             headers = await self.coordinator._get_headers()

    #             async with session.get(self._camera_data["still_image_url"], headers=headers) as response:
    #                 if response.status == 200:
    #                     return await response.read()
    #         except Exception as err:
    #             _LOGGER.error("Error fetching still image: %s", err)

    #     # Fallback to RTSP frame capture would require additional setup
    #     return None

    @property
    def stream_source(self) -> str | None:
        """Return the stream source."""
        return self._camera_data.get("stream_source")


class StandaloneCamera(UfanetCamera):
    """Standalone camera not attached to any domofon."""

    def __init__(self, coordinator, camera_data):
        """Initialize."""
        super().__init__(coordinator, camera_data)

    # async def async_camera_image(self, width: int | None = None, height: int | None = None) -> bytes | None:
    #     """Return bytes of camera image."""
    #     # Similar implementation as DomofonCamera
    #     if "still_image_url" in self._camera_data:
    #         try:
    #             session = self.coordinator._session
    #             headers = await self.coordinator._get_headers()

    #             async with session.get(self._camera_data["still_image_url"], headers=headers) as response:
    #                 if response.status == 200:
    #                     return await response.read()
    #         except Exception:
    #             pass
    #     return None

    @property
    def stream_source(self) -> str | None:
        """Return the stream source."""
        return self._camera_data.get("stream_source")
