"""Base entity helpers for Wavin WTC-3."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN


class WavinEntity(CoordinatorEntity):
    """Base Wavin entity.

    System entities are attached to the WTC-3/WTC-NET device.
    Zone entities are attached to separate TH devices, so Home Assistant can
    assign every zone to its own Area.
    """

    _attr_has_entity_name = True

    def __init__(self, coordinator, entry, stored, suffix: str, zone: int | None = None, zone_name: str | None = None) -> None:
        super().__init__(coordinator)
        self.entry = entry
        self.stored = stored
        self.zone_device = zone
        self._attr_unique_id = f"{entry.entry_id}_{suffix}"

        host = entry.data.get("host")
        system_identifier = (DOMAIN, entry.entry_id)

        if zone is None:
            self._attr_device_info = DeviceInfo(
                identifiers={system_identifier},
                name=stored["name"],
                manufacturer="Wavin",
                model="WTC-3 / WTC-NET",
                configuration_url=f"http://{host}",
            )
        else:
            self._attr_device_info = DeviceInfo(
                identifiers={(DOMAIN, entry.entry_id, f"th{zone}")},
                name=zone_name or f"TH{zone}",
                manufacturer="Wavin",
                model=f"DRT-300 / TH{zone}",
                via_device=system_identifier,
                configuration_url=f"http://{host}",
            )
