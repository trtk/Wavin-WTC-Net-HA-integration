"""Switch entities for Wavin WTC-3."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.exceptions import HomeAssistantError

from .api import WavinWTC3Api, WavinWTC3Error
from .const import DOMAIN
from .entity import WavinEntity


async def async_setup_entry(hass, entry, async_add_entities):
    stored = hass.data[DOMAIN][entry.entry_id]
    coordinator = stored["coordinator"]
    entities = []
    for zone in range(1, stored["zone_count"] + 1):
        entities.append(WavinZoneLockSwitch(coordinator, entry, stored, zone, stored["zone_names"][zone - 1]))
    async_add_entities(entities)


class WavinZoneLockSwitch(WavinEntity, SwitchEntity):
    """Lock/unlock a DRT-300 zone keypad."""

    def __init__(self, coordinator, entry, stored, zone: int, zone_name: str) -> None:
        super().__init__(coordinator, entry, stored, f"zone_{zone}_lock", zone=zone, zone_name=zone_name)
        self.zone = zone
        self._attr_name = "Zárolás"
        self._attr_icon = "mdi:lock"

    @property
    def _api(self) -> WavinWTC3Api:
        return self.stored["api"]

    @property
    def is_on(self) -> bool | None:
        zone = self.coordinator.data.zones.get(self.zone)
        return zone.locked if zone else None

    async def async_turn_on(self, **kwargs) -> None:
        try:
            await self._api.set_zone_locked(self.zone, True)
        except WavinWTC3Error as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs) -> None:
        try:
            await self._api.set_zone_locked(self.zone, False)
        except WavinWTC3Error as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
