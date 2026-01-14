"""Const for ufanet."""

DOMAIN = "ufanet_domofon"
DEFAULT_NAME = "Ufanet Domofon"
SCAN_INTERVAL = 30  # seconds

# API endpoints
BASE_URL = "https://dom.ufanet.ru/"
AUTH_ENDPOINT = "api/v1/auth/auth_by_contract/"
DOMOFONS_ENDPOINT = "api/v0/skud/shared/"
OPEN_DOOR_ENDPOINT = "api/v0/skud/shared/{id}/open/"
CAMERAS_ENDPOINT = "api/v1/cctv"

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
PLATFORMS = ["camera", "button"]
