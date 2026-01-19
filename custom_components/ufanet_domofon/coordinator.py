"""Data update coordinator for Ufanet Domofon."""

import asyncio
from datetime import timedelta
import logging

import aiohttp

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import AUTH_ENDPOINT, BASE_URL, CAMERAS_ENDPOINT, CONTRACT_ENDPOINT, DOMOFONS_ENDPOINT, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class UfanetDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Ufanet data."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry):
        """Initialize."""
        super().__init__(
            hass,
            _LOGGER,
            name="Ufanet Domofon",
            update_interval=timedelta(hours=SCAN_INTERVAL),
        )

        self.entry = entry
        self._session = aiohttp.ClientSession()
        self._access_token = None
        self._refresh_token = None

        self.domofons = []
        self.contracts = []
        self.all_cameras = []
        self.domofons_cameras = {}
        self.standalone_cameras = []

    async def _async_login(self):
        """Authenticate and get access token."""
        contract = self.entry.data["contract"]
        password = self.entry.data["password"]

        auth_data = {"contract": contract, "password": password}

        try:
            async with self._session.post(f"{BASE_URL}{AUTH_ENDPOINT}", json=auth_data) as response:
                if response.status != 200:
                    raise UpdateFailed(f"Auth failed: {response.status}")

                data = await response.json()

                # Извлечение токена из ответа
                self._access_token = data.get("token").get("access")
                self._refresh_token = data.get("token").get("refresh")

                if not self._access_token:
                    _LOGGER.error("Token not found in response: %s", data)
                    raise UpdateFailed("Authentication token not received")

                _LOGGER.debug("Successfully authenticated")

        except aiohttp.ClientError as err:
            _LOGGER.error("Connection error during auth: %s", err)
            raise UpdateFailed(f"Connection error: {err}")  # noqa: B904

    async def _get_headers(self):
        """Get headers with authentication token."""
        if not self._access_token:
            await self._async_login()

        return {"Authorization": f"JWT {self._access_token}", "Content-Type": "application/json"}

    async def _fetch_domofons(self):
        """Fetch domofons list."""
        try:
            headers = await self._get_headers()
            async with self._session.get(f"{BASE_URL}{DOMOFONS_ENDPOINT}", headers=headers) as response:
                response.raise_for_status()
                self.domofons = await response.json()
                _LOGGER.debug("Fetched %s domofons", len(self.domofons))
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Failed to fetch domofons: %s", err)
            self.domofons = []

    async def _fetch_contracts(self):
        """Fetch domofons list."""
        try:
            headers = await self._get_headers()
            async with self._session.get(f"{BASE_URL}{CONTRACT_ENDPOINT}", headers=headers) as response:
                response.raise_for_status()
                self.contracts = await response.json()
                _LOGGER.debug("Fetched %s domofons", len(self.domofons))
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Failed to fetch domofons: %s", err)
            self.contracts = []

    async def _fetch_cameras(self):
        """Fetch cameras list and generate RTSP URLs."""
        try:
            headers = await self._get_headers()
            async with self._session.get(f"{BASE_URL}{CAMERAS_ENDPOINT}", headers=headers) as response:
                response.raise_for_status()
                cameras_data = await response.json()

                self.all_cameras = []
                for camera in cameras_data:
                    # Generate RTSP URL
                    domain = camera.get("servers", {}).get("domain", "")
                    token_l = camera.get("token_l", "")
                    number = camera.get("number", "")

                    if domain and token_l and number:
                        rtsp_url = f"rtsp://{domain}/{number}?token={token_l}"
                        camera["stream_source"] = rtsp_url

                    self.all_cameras.append(camera)

                _LOGGER.debug("Fetched %s cameras", len(self.all_cameras))

        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Failed to fetch cameras: %s", err)
            self.all_cameras = []

    def _map_cameras_to_domofons(self):
        """Map cameras to domofons based on cctv_number."""
        self.domofons_cameras = {}
        self.standalone_cameras = []

        # Create a lookup dictionary for cameras by number
        cameras_by_number = {cam.get("number"): cam for cam in self.all_cameras}

        # Map cameras to domofons
        for domofon in self.domofons:
            domofon_id = domofon.get("id")
            cctv_number = domofon.get("cctv_number")

            camera_data = None
            if cctv_number and cctv_number in cameras_by_number:
                camera_data = cameras_by_number[cctv_number]
                # Mark this camera as used
                cameras_by_number.pop(cctv_number)

            self.domofons_cameras[domofon_id] = {"domofon": domofon, "camera": camera_data}

        # Remaining cameras are standalone
        self.standalone_cameras = list(cameras_by_number.values())

    async def _async_update_data(self):
        """Update data from API."""
        try:
            # Ensure we have a valid token
            if not self._access_token:
                await self._async_login()

            # Fetch data in parallel
            await asyncio.gather(self._fetch_domofons(), self._fetch_cameras(), self._fetch_contracts())

            # Map cameras to domofons
            self._map_cameras_to_domofons()

        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error updating data: %s", err)
            raise UpdateFailed(f"Error updating data: {err}")  # noqa: B904

        else:
            # Return structured data for platforms
            return {
                "domofons": self.domofons,
                "cameras": self.all_cameras,
                "domofon_camera_map": self.domofons_cameras,
                "standalone_cameras": self.standalone_cameras,
                "contract": self.contracts,
            }

    async def async_open_door(self, domofon_id: str) -> bool:
        """Send open door command for specific domofon."""
        try:
            headers = await self._get_headers()
            async with self._session.get(
                f"{BASE_URL}{DOMOFONS_ENDPOINT}{domofon_id}/open/", headers=headers
            ) as response:
                if response.status == 200:
                    _LOGGER.info("Door opened for domofon %s", domofon_id)
                    return True

                _LOGGER.error("Failed to open door: %s", response.status)
                return False
        except Exception as err:  # noqa: BLE001
            _LOGGER.error("Error opening door: %s", err)
            return False

    async def async_close(self):
        """Close the session."""
        if self._session:
            await self._session.close()
