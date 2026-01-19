"""Const for ufanet."""

DOMAIN = "ufanet_domofon"
DEFAULT_NAME = "Ufanet Domofon"
SCAN_INTERVAL = 24  # hours

# API endpoints
BASE_URL = "https://dom.ufanet.ru/"
AUTH_ENDPOINT = "api/v1/auth/auth_by_contract/"
DOMOFONS_ENDPOINT = "api/v0/skud/shared/"
OPEN_DOOR_ENDPOINT = "api/v0/skud/shared/{id}/open/"
CAMERAS_ENDPOINT = "api/v1/cctv"
CONTRACT_ENDPOINT = "api/v0/contract/"

# Configuration keys
CONF_CONTRACT = "contract"
CONF_PASSWORD = "password"

# Entity attributes
ATTR_DOMOFON_ID = "domofon_id"
ATTR_CAMERA_ID = "camera_id"
ATTR_ADDRESS = "address"
ATTR_LAST_OPENED = "last_opened"
ATTR_LATITUDE = "latitude"
ATTR_LONGITUDE = "longitude"

# Platforms
PLATFORMS = ["camera", "button", "sensor"]

# Attributes
ATTR_CAMERA_NUMBER = "intercom_id"
ATTR_RTSP_URL = "rtsp_url"
ATTR_LAST_UPDATE = "last_update"
