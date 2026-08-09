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
        # unit_index 1 is the master/only WTC-3 in a config entry. Its
        # unique_id and device identifiers are kept exactly as before
        # multi-unit support existed, so existing single-unit installs keep
        # their entity_id, device and area assignments unchanged. Extra units
        # (2..N, added for master/slave setups) get namespaced identifiers so
        # they cannot collide with the master or with each other.
        unit_index = stored.get("unit_index", 1)
        is_master_unit = unit_index == 1

        host = entry.data.get("host")

        if is_master_unit:
            self._attr_unique_id = f"{entry.entry_id}_{suffix}"
            system_identifier = (DOMAIN, entry.entry_id)
            zone_identifier = (DOMAIN, entry.entry_id, f"th{zone}") if zone is not None else None
            zone_device_name = zone_name or f"TH{zone}"
        else:
            self._attr_unique_id = f"{entry.entry_id}_u{unit_index}_{suffix}"
            system_identifier = (DOMAIN, entry.entry_id, f"unit{unit_index}")
            zone_identifier = (DOMAIN, entry.entry_id, f"unit{unit_index}_th{zone}") if zone is not None else None
            unit_name = stored.get("name") or f"Wavin WTC-3 #{unit_index}"
            zone_device_name = f"{unit_name} {zone_name or f'TH{zone}'}"

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
                identifiers={zone_identifier},
                name=zone_device_name,
                manufacturer="Wavin",
                model=f"DRT-300 / TH{zone}",
                via_device=system_identifier,
                configuration_url=f"http://{host}",
            )
