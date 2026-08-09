"""Config flow for Wavin WTC-3 / WTC-NET."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

from .api import WavinWTC3Api, WavinWTC3Error
from .const import (
    CONF_ADDRESS_OFFSET,
    CONF_EXTRA_UNITS,
    CONF_HOST,
    CONF_PORT,
    CONF_SLAVE_ID,
    CONF_TIMEOUT,
    CONF_UNIT_COUNT,
    CONF_UNIT_NAME,
    CONF_ZONE_COUNT,
    CONF_ZONE_NAMES,
    DEFAULT_ADDRESS_OFFSET,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DEFAULT_SLAVE_ID,
    DEFAULT_TIMEOUT,
    DEFAULT_UNIT_COUNT,
    DEFAULT_ZONE_COUNT,
    DOMAIN,
    MAX_WTC_UNITS,
)

# Steps for additional (slave) WTC-3 units, beyond the master configured in
# the "user"/"init" step. Index 0 -> unit #2, index 1 -> unit #3, index 2 ->
# unit #4 (MAX_WTC_UNITS = 1 master + 3 extra units).
EXTRA_UNIT_STEP_IDS = ("unit2", "unit3", "unit4")


def _parse_zone_names(value: str, zone_count: int) -> list[str]:
    names = [x.strip() for x in (value or "").split(",") if x.strip()]
    names.extend([f"TH{i}" for i in range(len(names) + 1, zone_count + 1)])
    return names[:zone_count]


def _zone_names_default(value) -> str:
    if isinstance(value, list):
        return ", ".join(value)
    return value or "TH1, TH2, TH3, TH4, TH5, TH6, TH7"


def _extra_unit_schema(defaults: dict) -> vol.Schema:
    return vol.Schema(
        {
            vol.Optional(CONF_UNIT_NAME, default=defaults.get(CONF_UNIT_NAME, "")): str,
            vol.Required(CONF_SLAVE_ID, default=defaults.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)): int,
            vol.Optional(CONF_ZONE_COUNT, default=defaults.get(CONF_ZONE_COUNT, DEFAULT_ZONE_COUNT)): vol.All(int, vol.Range(min=1, max=7)),
            vol.Optional(CONF_ZONE_NAMES, default=_zone_names_default(defaults.get(CONF_ZONE_NAMES))): str,
        }
    )


async def _validate_extra_unit(
    host: str,
    port: int,
    timeout: int,
    address_offset: int,
    slave_id: int,
    zone_count: int,
    existing_slave_ids: set[int],
) -> str | None:
    """Validate one additional WTC-3 unit. Returns an error code, or None."""
    if slave_id in existing_slave_ids:
        return "duplicate_slave_id"
    api = WavinWTC3Api(host, port, slave_id, timeout, address_offset)
    try:
        await api.read_all(zone_count)
    except WavinWTC3Error:
        return "cannot_connect"
    finally:
        await api.close()
    return None


class WavinConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wavin WTC-3."""

    VERSION = 1

    def __init__(self) -> None:
        self._data: dict = {}
        self._extra_units: list[dict] = []

    def _finish_entry(self):
        data = dict(self._data)
        data[CONF_EXTRA_UNITS] = self._extra_units
        title = data.get(CONF_NAME) or DEFAULT_NAME
        return self.async_create_entry(title=title, data=data)

    async def async_step_user(self, user_input=None):
        errors: dict[str, str] = {}
        if user_input is not None:
            zone_count = int(user_input[CONF_ZONE_COUNT])
            zone_names = _parse_zone_names(user_input.get(CONF_ZONE_NAMES, ""), zone_count)
            await self.async_set_unique_id(f"wavin_wtc3_{user_input[CONF_HOST]}_{user_input[CONF_SLAVE_ID]}")
            self._abort_if_unique_id_configured()
            api = WavinWTC3Api(
                user_input[CONF_HOST],
                user_input[CONF_PORT],
                user_input[CONF_SLAVE_ID],
                user_input[CONF_TIMEOUT],
                user_input[CONF_ADDRESS_OFFSET],
            )
            try:
                await api.read_all(zone_count)
            except WavinWTC3Error:
                errors["base"] = "cannot_connect"
            finally:
                await api.close()
            if not errors:
                data = dict(user_input)
                data[CONF_ZONE_NAMES] = zone_names
                self._data = data
                self._extra_units = []
                if int(user_input.get(CONF_UNIT_COUNT, DEFAULT_UNIT_COUNT)) > 1:
                    return await self.async_step_unit2()
                return self._finish_entry()

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default=DEFAULT_NAME): str,
                vol.Required(CONF_HOST): str,
                vol.Optional(CONF_PORT, default=DEFAULT_PORT): int,
                vol.Optional(CONF_SLAVE_ID, default=DEFAULT_SLAVE_ID): int,
                vol.Optional(CONF_ZONE_COUNT, default=DEFAULT_ZONE_COUNT): vol.All(int, vol.Range(min=1, max=7)),
                vol.Optional(CONF_ZONE_NAMES, default="TH1, TH2, TH3, TH4, TH5, TH6, TH7"): str,
                vol.Optional(CONF_TIMEOUT, default=DEFAULT_TIMEOUT): vol.All(int, vol.Range(min=1, max=30)),
                vol.Optional(CONF_ADDRESS_OFFSET, default=DEFAULT_ADDRESS_OFFSET): int,
                vol.Optional(CONF_UNIT_COUNT, default=DEFAULT_UNIT_COUNT): vol.All(int, vol.Range(min=1, max=MAX_WTC_UNITS)),
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

    async def _async_step_extra_unit(self, position: int, user_input=None):
        """Handle the step that configures one additional (slave) WTC-3 unit."""
        step_id = EXTRA_UNIT_STEP_IDS[position]
        errors: dict[str, str] = {}
        existing_slave_ids = {self._data[CONF_SLAVE_ID]} | {u[CONF_SLAVE_ID] for u in self._extra_units}

        if user_input is not None:
            zone_count = int(user_input[CONF_ZONE_COUNT])
            slave_id = int(user_input[CONF_SLAVE_ID])
            error = await _validate_extra_unit(
                self._data[CONF_HOST],
                self._data[CONF_PORT],
                self._data[CONF_TIMEOUT],
                self._data[CONF_ADDRESS_OFFSET],
                slave_id,
                zone_count,
                existing_slave_ids,
            )
            if error:
                errors["base"] = error
            else:
                self._extra_units.append(
                    {
                        CONF_SLAVE_ID: slave_id,
                        CONF_ZONE_COUNT: zone_count,
                        CONF_ZONE_NAMES: _parse_zone_names(user_input.get(CONF_ZONE_NAMES, ""), zone_count),
                        CONF_UNIT_NAME: user_input.get(CONF_UNIT_NAME) or f"{DEFAULT_NAME} #{position + 2}",
                    }
                )
                unit_count = int(self._data.get(CONF_UNIT_COUNT, DEFAULT_UNIT_COUNT))
                if position + 2 < unit_count:
                    next_step = getattr(self, f"async_step_{EXTRA_UNIT_STEP_IDS[position + 1]}")
                    return await next_step()
                return self._finish_entry()

        default_slave_id = (self._extra_units[-1][CONF_SLAVE_ID] if self._extra_units else self._data[CONF_SLAVE_ID]) + 1
        schema = _extra_unit_schema({CONF_UNIT_NAME: f"{DEFAULT_NAME} #{position + 2}", CONF_SLAVE_ID: default_slave_id})
        return self.async_show_form(step_id=step_id, data_schema=schema, errors=errors)

    async def async_step_unit2(self, user_input=None):
        return await self._async_step_extra_unit(0, user_input)

    async def async_step_unit3(self, user_input=None):
        return await self._async_step_extra_unit(1, user_input)

    async def async_step_unit4(self, user_input=None):
        return await self._async_step_extra_unit(2, user_input)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return WavinOptionsFlow(config_entry)


class WavinOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Wavin WTC-3."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        # Do not assign to self.config_entry. In newer Home Assistant versions
        # OptionsFlow exposes config_entry as a read-only property, and assigning
        # to it makes the options flow fail with HTTP 500 when opened.
        self._wavin_config_entry = config_entry
        self._data: dict = {}
        self._extra_units: list[dict] = []

    @property
    def _entry(self) -> config_entries.ConfigEntry:
        """Return the config entry in a way that is compatible with HA versions."""
        return getattr(self, "config_entry", None) or self._wavin_config_entry

    def _finish_entry(self):
        data = dict(self._data)
        data[CONF_EXTRA_UNITS] = self._extra_units
        return self.async_create_entry(title="", data=data)

    async def async_step_init(self, user_input=None):
        current = {**self._entry.data, **self._entry.options}
        if user_input is not None:
            zone_count = int(user_input[CONF_ZONE_COUNT])
            user_input[CONF_ZONE_NAMES] = _parse_zone_names(user_input.get(CONF_ZONE_NAMES, ""), zone_count)
            self._data = user_input
            self._extra_units = []
            if int(user_input.get(CONF_UNIT_COUNT, DEFAULT_UNIT_COUNT)) > 1:
                return await self.async_step_unit2()
            return self._finish_entry()

        current_unit_count = 1 + len(current.get(CONF_EXTRA_UNITS) or [])
        schema = vol.Schema(
            {
                vol.Optional(CONF_ZONE_COUNT, default=current.get(CONF_ZONE_COUNT, DEFAULT_ZONE_COUNT)): vol.All(int, vol.Range(min=1, max=7)),
                vol.Optional(CONF_ZONE_NAMES, default=_zone_names_default(current.get(CONF_ZONE_NAMES))): str,
                vol.Optional(CONF_TIMEOUT, default=current.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)): vol.All(int, vol.Range(min=1, max=30)),
                vol.Optional(CONF_ADDRESS_OFFSET, default=current.get(CONF_ADDRESS_OFFSET, DEFAULT_ADDRESS_OFFSET)): int,
                vol.Optional(CONF_UNIT_COUNT, default=current_unit_count): vol.All(int, vol.Range(min=1, max=MAX_WTC_UNITS)),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)

    async def _async_step_extra_unit(self, position: int, user_input=None):
        step_id = EXTRA_UNIT_STEP_IDS[position]
        errors: dict[str, str] = {}
        current = {**self._entry.data, **self._entry.options}
        existing_extra = current.get(CONF_EXTRA_UNITS) or []
        master_slave_id = current.get(CONF_SLAVE_ID, DEFAULT_SLAVE_ID)
        existing_slave_ids = {master_slave_id} | {u[CONF_SLAVE_ID] for u in self._extra_units}

        if user_input is not None:
            zone_count = int(user_input[CONF_ZONE_COUNT])
            slave_id = int(user_input[CONF_SLAVE_ID])
            error = await _validate_extra_unit(
                current[CONF_HOST],
                current.get(CONF_PORT, DEFAULT_PORT),
                self._data.get(CONF_TIMEOUT, DEFAULT_TIMEOUT),
                self._data.get(CONF_ADDRESS_OFFSET, DEFAULT_ADDRESS_OFFSET),
                slave_id,
                zone_count,
                existing_slave_ids,
            )
            if error:
                errors["base"] = error
            else:
                self._extra_units.append(
                    {
                        CONF_SLAVE_ID: slave_id,
                        CONF_ZONE_COUNT: zone_count,
                        CONF_ZONE_NAMES: _parse_zone_names(user_input.get(CONF_ZONE_NAMES, ""), zone_count),
                        CONF_UNIT_NAME: user_input.get(CONF_UNIT_NAME) or f"{DEFAULT_NAME} #{position + 2}",
                    }
                )
                unit_count = int(self._data.get(CONF_UNIT_COUNT, DEFAULT_UNIT_COUNT))
                if position + 2 < unit_count:
                    next_step = getattr(self, f"async_step_{EXTRA_UNIT_STEP_IDS[position + 1]}")
                    return await next_step()
                return self._finish_entry()

        existing_default = existing_extra[position] if position < len(existing_extra) else {}
        default_slave_id = existing_default.get(
            CONF_SLAVE_ID,
            (self._extra_units[-1][CONF_SLAVE_ID] if self._extra_units else master_slave_id) + 1,
        )
        schema = _extra_unit_schema(
            {
                CONF_UNIT_NAME: existing_default.get(CONF_UNIT_NAME, f"{DEFAULT_NAME} #{position + 2}"),
                CONF_SLAVE_ID: default_slave_id,
                CONF_ZONE_COUNT: existing_default.get(CONF_ZONE_COUNT, DEFAULT_ZONE_COUNT),
                CONF_ZONE_NAMES: existing_default.get(CONF_ZONE_NAMES),
            }
        )
        return self.async_show_form(step_id=step_id, data_schema=schema, errors=errors)

    async def async_step_unit2(self, user_input=None):
        return await self._async_step_extra_unit(0, user_input)

    async def async_step_unit3(self, user_input=None):
        return await self._async_step_extra_unit(1, user_input)

    async def async_step_unit4(self, user_input=None):
        return await self._async_step_extra_unit(2, user_input)
