"""Config flow for Wavin WTC-3 / WTC-NET."""
from __future__ import annotations

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME
from homeassistant.core import callback

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
)


def _parse_zone_names(value: str, zone_count: int) -> list[str]:
    names = [x.strip() for x in (value or "").split(",") if x.strip()]
    names.extend([f"TH{i}" for i in range(len(names) + 1, zone_count + 1)])
    return names[:zone_count]


class WavinConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Wavin WTC-3."""

    VERSION = 1

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
                title = data.get(CONF_NAME) or DEFAULT_NAME
                return self.async_create_entry(title=title, data=data)

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
            }
        )
        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)

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

    @property
    def _entry(self) -> config_entries.ConfigEntry:
        """Return the config entry in a way that is compatible with HA versions."""
        return getattr(self, "config_entry", None) or self._wavin_config_entry

    async def async_step_init(self, user_input=None):
        if user_input is not None:
            zone_count = int(user_input[CONF_ZONE_COUNT])
            user_input[CONF_ZONE_NAMES] = _parse_zone_names(user_input.get(CONF_ZONE_NAMES, ""), zone_count)
            return self.async_create_entry(title="", data=user_input)

        current = {**self._entry.data, **self._entry.options}
        zone_names = current.get(CONF_ZONE_NAMES) or [f"TH{i}" for i in range(1, current.get(CONF_ZONE_COUNT, 7) + 1)]
        if isinstance(zone_names, list):
            zone_names_value = ", ".join(zone_names)
        else:
            zone_names_value = zone_names
        schema = vol.Schema(
            {
                vol.Optional(CONF_ZONE_COUNT, default=current.get(CONF_ZONE_COUNT, DEFAULT_ZONE_COUNT)): vol.All(int, vol.Range(min=1, max=7)),
                vol.Optional(CONF_ZONE_NAMES, default=zone_names_value): str,
                vol.Optional(CONF_TIMEOUT, default=current.get(CONF_TIMEOUT, DEFAULT_TIMEOUT)): vol.All(int, vol.Range(min=1, max=30)),
                vol.Optional(CONF_ADDRESS_OFFSET, default=current.get(CONF_ADDRESS_OFFSET, DEFAULT_ADDRESS_OFFSET)): int,
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
