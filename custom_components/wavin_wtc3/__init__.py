"""Wavin WTC-3 / WTC-NET native Home Assistant integration."""
from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import WavinWTC3Api, WavinWTC3Error
from .const import (
    CONF_ADDRESS_OFFSET,
    CONF_EXTRA_UNITS,
    CONF_HOST,
    CONF_PORT,
    CONF_SLAVE_ID,
    CONF_TIMEOUT,
    CONF_UNIT_NAME,
    CONF_ZONE_COUNT,
    CONF_ZONE_NAMES,
    DEFAULT_ADDRESS_OFFSET,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    DEFAULT_TIMEOUT,
    DEFAULT_ZONE_COUNT,
    DOMAIN,
    PLATFORMS,
    POLL_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


def _platforms() -> list[Platform]:
    return [Platform(platform) for platform in PLATFORMS]


def _normalize_zone_names(zone_names, zone_count: int) -> list[str]:
    zone_names = zone_names or [f"TH{i}" for i in range(1, zone_count + 1)]
    if isinstance(zone_names, str):
        zone_names = [name.strip() for name in zone_names.split(",") if name.strip()]
    return (zone_names + [f"TH{i}" for i in range(1, 8)])[:zone_count]


def _build_unit_configs(data: dict, entry_title: str) -> list[dict]:
    """Return the per-WTC-3-unit configuration described by a config entry.

    Unit 1 (the master) is always described by the top-level keys, so a
    single-unit config entry (no CONF_EXTRA_UNITS) behaves exactly as it did
    before multi-unit (master/slave) support existed. Units 2..N describe
    additional slave WTC-3 devices daisy-chained on the same RS-485 bus.
    """
    zone_count = int(data.get(CONF_ZONE_COUNT, DEFAULT_ZONE_COUNT))
    units = [
        {
            "unit_index": 1,
            "slave_id": data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID),
            "zone_count": zone_count,
            "zone_names": _normalize_zone_names(data.get(CONF_ZONE_NAMES), zone_count),
            "name": data.get(CONF_NAME) or entry_title or DEFAULT_NAME,
        }
    ]
    for index, extra in enumerate(data.get(CONF_EXTRA_UNITS) or [], start=2):
        extra_zone_count = int(extra.get(CONF_ZONE_COUNT, DEFAULT_ZONE_COUNT))
        units.append(
            {
                "unit_index": index,
                "slave_id": extra[CONF_SLAVE_ID],
                "zone_count": extra_zone_count,
                "zone_names": _normalize_zone_names(extra.get(CONF_ZONE_NAMES), extra_zone_count),
                "name": extra.get(CONF_UNIT_NAME) or f"{DEFAULT_NAME} #{index}",
            }
        )
    return units


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wavin WTC-3 from a config entry."""
    data = {**entry.data, **entry.options}
    host = data[CONF_HOST]
    port = data.get(CONF_PORT, DEFAULT_PORT)
    timeout = data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
    address_offset = data.get(CONF_ADDRESS_OFFSET, DEFAULT_ADDRESS_OFFSET)

    unit_configs = _build_unit_configs(data, entry.title)

    units: list[dict] = []
    any_ready = False
    for unit_config in unit_configs:
        api = WavinWTC3Api(
            host=host,
            port=port,
            slave_id=unit_config["slave_id"],
            timeout=timeout,
            address_offset=address_offset,
        )
        zone_count = unit_config["zone_count"]

        async def _async_update_data(api: WavinWTC3Api = api, zone_count: int = zone_count):
            try:
                return await api.read_all(zone_count)
            except WavinWTC3Error as err:
                raise UpdateFailed(str(err)) from err

        coordinator = DataUpdateCoordinator(
            hass,
            _LOGGER,
            name=f"{entry.title or DEFAULT_NAME} ({unit_config['name']})",
            update_method=_async_update_data,
            update_interval=timedelta(seconds=POLL_INTERVAL_SECONDS),
            always_update=False,
        )
        # Deliberately non-raising: if one WTC-3 unit does not answer during
        # setup, the other configured units should still load normally. The
        # affected unit's entities simply report "unavailable" until its own
        # 30 second polling cycle succeeds.
        await coordinator.async_refresh()
        if coordinator.last_update_success:
            any_ready = True

        units.append({**unit_config, "api": api, "coordinator": coordinator})

    if not any_ready:
        for unit in units:
            await unit["api"].close()
        raise ConfigEntryNotReady(
            f"Egyik konfigurált WTC-3 egység sem érhető el ezen a címen: {host}:{port}"
        )

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {"units": units}

    await hass.config_entries.async_forward_entry_setups(entry, _platforms())
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, _platforms())
    if unload_ok:
        stored = hass.data[DOMAIN].pop(entry.entry_id)
        for unit in stored["units"]:
            await unit["api"].close()
    return unload_ok
