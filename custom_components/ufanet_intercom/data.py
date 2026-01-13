"""Custom types for ufanet_intercom."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from homeassistant.config_entries import ConfigEntry
    from homeassistant.loader import Integration

    from .api import UfanetIntercomApiClient
    from .coordinator import UfanetIntercomDataUpdateCoordinator


type UfanetIntercomConfigEntry = ConfigEntry[UfanetIntercomData]


@dataclass
class UfanetIntercomData:
    """Data for ufanet_intercom."""

    client: UfanetIntercomApiClient
    coordinator: UfanetIntercomDataUpdateCoordinator
    integration: Integration
