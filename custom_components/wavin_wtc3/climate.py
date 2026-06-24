"""Climate entities for Wavin WTC-3 zones."""
from __future__ import annotations

import logging

from homeassistant.components.climate import ClimateEntity
from homeassistant.components.climate.const import (
    ClimateEntityFeature,
    HVACAction,
    HVACMode,
)
from homeassistant.const import UnitOfTemperature, ATTR_TEMPERATURE
from homeassistant.exceptions import HomeAssistantError

from .api import WavinWTC3Api, WavinWTC3Error
from .const import DOMAIN, PRESET_COMFORT, PRESET_ECONOMY
from .entity import WavinEntity

_LOGGER = logging.getLogger(__name__)


def _climate_features():
    features = ClimateEntityFeature.TARGET_TEMPERATURE | ClimateEntityFeature.PRESET_MODE
    if hasattr(ClimateEntityFeature, "TURN_ON"):
        features |= ClimateEntityFeature.TURN_ON | ClimateEntityFeature.TURN_OFF
    return features


async def async_setup_entry(hass, entry, async_add_entities):
    stored = hass.data[DOMAIN][entry.entry_id]
    coordinator = stored["coordinator"]
    entities = [
        WavinZoneClimate(coordinator, entry, stored, zone, stored["zone_names"][zone - 1])
        for zone in range(1, stored["zone_count"] + 1)
    ]
    async_add_entities(entities)


class WavinZoneClimate(WavinEntity, ClimateEntity):
    """One Wavin DRT-300 / TH zone as a Home Assistant climate entity."""

    _attr_temperature_unit = UnitOfTemperature.CELSIUS
    _attr_target_temperature_step = 0.5
    _attr_min_temp = 5.0
    _attr_max_temp = 50.0
    _attr_hvac_modes = [HVACMode.OFF, HVACMode.HEAT, HVACMode.COOL]
    _attr_preset_modes = [PRESET_COMFORT, PRESET_ECONOMY]
    _attr_supported_features = _climate_features()

    def __init__(self, coordinator, entry, stored, zone: int, name: str) -> None:
        super().__init__(coordinator, entry, stored, f"zone_{zone}_climate", zone=zone, zone_name=name)
        self.zone = zone
        self._attr_name = None

    @property
    def _api(self) -> WavinWTC3Api:
        return self.stored["api"]

    @property
    def _zone(self):
        return self.coordinator.data.zones.get(self.zone)

    @property
    def available(self) -> bool:
        zone = self._zone
        return super().available and zone is not None and zone.live is not False

    @property
    def current_temperature(self) -> float | None:
        return self._zone.temperature if self._zone else None

    @property
    def current_humidity(self) -> float | None:
        return self._zone.humidity if self._zone else None

    @property
    def hvac_mode(self):
        zone = self._zone
        if not zone or zone.on is False:
            return HVACMode.OFF
        return HVACMode.COOL if zone.cooling else HVACMode.HEAT

    @property
    def hvac_action(self):
        zone = self._zone
        if not zone or zone.on is False:
            return HVACAction.OFF
        if zone.output:
            return HVACAction.COOLING if zone.cooling else HVACAction.HEATING
        return HVACAction.IDLE

    @property
    def preset_mode(self) -> str | None:
        zone = self._zone
        if not zone:
            return None
        return PRESET_COMFORT if zone.comfort else PRESET_ECONOMY

    @property
    def target_temperature(self) -> float | None:
        zone = self._zone
        if not zone:
            return None
        if zone.cooling:
            return zone.cool_setpoint if zone.comfort else zone.economy_cool_setpoint
        return zone.heat_setpoint if zone.comfort else zone.economy_heat_setpoint

    @property
    def extra_state_attributes(self):
        zone = self._zone
        if not zone:
            return {}
        return {
            "th_index": self.zone,
            "is_master_zone": self.zone == 1,
            "locked": zone.locked,
            "live": zone.live,
            "dewpoint": zone.dewpoint,
            "wheel_offset": zone.wheel_offset,
            "wheel_position_code": zone.wheel_position,
            "condensation": zone.condensation,
            "dwp_input": zone.dwp_input,
            "dry_output": zone.dry,
            "cool_setpoint": zone.cool_setpoint,
            "heat_setpoint": zone.heat_setpoint,
            "economy_heat_setpoint": zone.economy_heat_setpoint,
            "economy_cool_setpoint": zone.economy_cool_setpoint,
        }

    async def async_set_hvac_mode(self, hvac_mode) -> None:
        try:
            if hvac_mode == HVACMode.OFF:
                if self.zone == 1:
                    await self._api.set_global_on(False)
                await self._api.set_zone_on(self.zone, False)
            elif hvac_mode in (HVACMode.HEAT, HVACMode.COOL):
                cooling = hvac_mode == HVACMode.COOL
                if self.zone == 1:
                    await self._api.set_global_on(True)
                    await self._api.set_global_cooling(cooling)
                await self._api.set_zone_on(self.zone, True)
                await self._api.set_zone_cooling(self.zone, cooling)
            else:
                raise HomeAssistantError(f"Nem támogatott HVAC mód: {hvac_mode}")
        except WavinWTC3Error as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()

    async def async_turn_on(self) -> None:
        zone = self._zone
        mode = HVACMode.COOL if zone and zone.cooling else HVACMode.HEAT
        await self.async_set_hvac_mode(mode)

    async def async_turn_off(self) -> None:
        await self.async_set_hvac_mode(HVACMode.OFF)

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        if preset_mode not in (PRESET_COMFORT, PRESET_ECONOMY):
            raise HomeAssistantError(f"Nem támogatott preset: {preset_mode}")
        comfort = preset_mode == PRESET_COMFORT
        try:
            if self.zone == 1:
                await self._api.set_global_comfort(comfort)
            await self._api.set_zone_comfort(self.zone, comfort)
        except WavinWTC3Error as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()

    async def async_set_temperature(self, **kwargs) -> None:
        if ATTR_TEMPERATURE not in kwargs:
            return
        zone = self._zone
        if not zone:
            raise HomeAssistantError("A zóna állapota még nem ismert")
        temp = round(float(kwargs[ATTR_TEMPERATURE]) * 2) / 2
        if zone.cooling:
            kind = "cool" if zone.comfort else "economy_cool"
        else:
            kind = "heat" if zone.comfort else "economy_heat"
        try:
            await self._api.write_setpoint(self.zone, kind, temp)
        except WavinWTC3Error as err:
            raise HomeAssistantError(str(err)) from err
        await self.coordinator.async_request_refresh()
