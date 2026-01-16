"""Button platform for Ufanet Domofon."""

import logging

from homeassistant.components.sensor import SensorEntity
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
    """Set up Ufanet sensors from a config entry."""
    coordinator: UfanetDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []

    for contract in coordinator.contracts:
        entities.append(BalanceSensor(coordinator, contract, "Баланс", "RUB"))  # noqa: PERF401
        # entities.append(LimitSensor(coordinator, contract))
        # entities.append(ActivitySensor(coordinator, contract))

    async_add_entities(entities, True)


class BalanceSensor(CoordinatorEntity, SensorEntity):
    """Balance sensor."""

    _attr_has_entity_name = True

    def __init__(self, coordinator, contract, name, unit):
        """Initialize."""
        super().__init__(coordinator)
        self._name = name
        self._unit = unit
        self._contract_data = contract
        self._contract_id = contract.get("id")
        self._balance = contract.get("balance")
        self._attr_unique_id = f"ufanet_contract_{self._contract_id}_balance"
        self._attr_name = "Баланс"
        self.entity_id = f"sensor.ufanet_{self._contract_id}_balance"

    @property
    def device_info(self):
        """Return device information for linking entities."""
        return {
            "identifiers": {(DOMAIN, self._contract_id)},
            "name": f"Данные по аккаунту {self._contract_data.get('title')}",
        }

    @property
    def native_value(self):
        """Возвращает значение баланса."""
        return round(float(self._balance), 2) if self._balance is not None else None

    @property
    def native_unit_of_measurement(self):
        """Возвращает единицу измерения."""
        return self._unit

    @property
    def icon(self):
        """Иконка для баланса."""
        return "mdi:cash"
