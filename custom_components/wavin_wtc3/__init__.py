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
    CONF_HOST,
    CONF_PORT,
    CONF_SLAVE_ID,
    CONF_TIMEOUT,
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


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Wavin WTC-3 from a config entry."""
    data = {**entry.data, **entry.options}
    host = data[CONF_HOST]
    port = data.get(CONF_PORT, DEFAULT_PORT)
    slave_id = data.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)
    timeout = data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)
    address_offset = data.get(CONF_ADDRESS_OFFSET, DEFAULT_ADDRESS_OFFSET)

    api = WavinWTC3Api(
        host=host,
        port=port,
        slave_id=slave_id,
        timeout=timeout,
        address_offset=address_offset,
    )

    zone_count = int(data.get(CONF_ZONE_COUNT, DEFAULT_ZONE_COUNT))
    zone_names = data.get(CONF_ZONE_NAMES) or [f"TH{i}" for i in range(1, zone_count + 1)]
    if isinstance(zone_names, str):
        zone_names = [name.strip() for name in zone_names.split(",") if name.strip()]
    zone_names = (zone_names + [f"TH{i}" for i in range(1, 8)])[:zone_count]

    async def _async_update_data():
        try:
            return await api.read_all(zone_count)
        except WavinWTC3Error as err:
            raise UpdateFailed(str(err)) from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name=entry.title or DEFAULT_NAME,
        update_method=_async_update_data,
        update_interval=timedelta(seconds=POLL_INTERVAL_SECONDS),
        always_update=False,
    )

    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:  # noqa: BLE001 - converted to HA retry setup
        await api.close()
        raise ConfigEntryNotReady(str(err)) from err

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = {
        "api": api,
        "coordinator": coordinator,
        "zone_count": zone_count,
        "zone_names": zone_names,
        "name": data.get(CONF_NAME, entry.title or DEFAULT_NAME),
    }

    await hass.config_entries.async_forward_entry_setups(entry, _platforms())
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, _platforms())
    if unload_ok:
        stored = hass.data[DOMAIN].pop(entry.entry_id)
        await stored["api"].close()
    return unload_ok
