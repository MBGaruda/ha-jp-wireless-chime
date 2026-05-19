"""Config flow for JP Wireless Chime."""

from __future__ import annotations

from copy import deepcopy
import logging
from typing import Any
from uuid import uuid4

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import selector
from homeassistant.util import slugify

from .const import (
    CONF_BUTTON_ID,
    CONF_BUTTONS,
    CONF_CHANNEL,
    CONF_MELODY,
    CONF_NAME,
    CONF_PROTOCOL,
    CONF_RECEIVER_ID,
    DOMAIN,
    MATCH_ANY,
    SUPPORTED_PROTOCOLS,
)
from .protocol import generate_base64

_LOGGER = logging.getLogger(__name__)


class JPWirelessChimeConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for JP Wireless Chime."""

    VERSION = 1

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Handle the initial step."""
        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={CONF_NAME: user_input[CONF_NAME]},
                options={CONF_BUTTONS: []},
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME, default="JP Wireless Chime"): str,
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=schema,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> JPWirelessChimeOptionsFlow:
        """Create the options flow."""
        return JPWirelessChimeOptionsFlow()


class JPWirelessChimeOptionsFlow(config_entries.OptionsFlow):
    """Handle options for JP Wireless Chime."""

    def __init__(self) -> None:
        """Initialize options flow."""
        self._buttons: list[dict[str, Any]] = []

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""
        self._buttons = deepcopy(
            self.config_entry.options.get(CONF_BUTTONS, [])
        )

        if user_input is not None:
            action = user_input["action"]

            if action == "add":
                return await self.async_step_add()

            if action == "remove":
                return await self.async_step_remove()

            return self.async_create_entry(
                title="",
                data={CONF_BUTTONS: self._buttons},
            )

        schema = vol.Schema(
            {
                vol.Required("action", default="add"): selector(
                    {
                        "select": {
                            "options": [
                                {"value": "add", "label": "Add chime button"},
                                {"value": "remove", "label": "Remove chime button"},
                                {"value": "finish", "label": "Finish"},
                            ]
                        }
                    }
                )
            }
        )

        return self.async_show_form(
            step_id="init",
            data_schema=schema,
        )

    async def async_step_add(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Add a chime button."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = str(user_input[CONF_NAME])
            protocol = str(user_input[CONF_PROTOCOL])
            channel = _normalize_wildcard_value(user_input.get(CONF_CHANNEL))
            melody = _normalize_wildcard_value(user_input.get(CONF_MELODY))
            receiver_id = _normalize_wildcard_value(user_input.get(CONF_RECEIVER_ID))

            if channel != MATCH_ANY and melody != MATCH_ANY:
                try:
                    generate_base64(
                        protocol=protocol,
                        channel=channel,
                        melody=melody,
                    )
                except Exception as err:  # noqa: BLE001
                    _LOGGER.debug("Invalid chime button configuration: %s", err)
                    errors["base"] = "invalid_chime_button"

            if not errors:
                button_id = self._make_button_id(name)

                self._buttons.append(
                    {
                        CONF_BUTTON_ID: button_id,
                        CONF_NAME: name,
                        CONF_PROTOCOL: protocol,
                        CONF_CHANNEL: channel,
                        CONF_MELODY: melody,
                        CONF_RECEIVER_ID: receiver_id,
                    }
                )

                return self.async_create_entry(
                    title="",
                    data={CONF_BUTTONS: self._buttons},
                )

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_PROTOCOL): selector(
                    {
                        "select": {
                            "options": [
                                {"value": protocol, "label": protocol}
                                for protocol in SUPPORTED_PROTOCOLS
                            ]
                        }
                    }
                ),
                vol.Optional(CONF_CHANNEL, default=MATCH_ANY): str,
                vol.Optional(CONF_MELODY, default=MATCH_ANY): str,
                vol.Optional(CONF_RECEIVER_ID, default=MATCH_ANY): str,
            }
        )

        return self.async_show_form(
            step_id="add",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_remove(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Remove a chime button."""
        if not self._buttons:
            return self.async_show_form(
                step_id="remove",
                data_schema=vol.Schema({}),
                errors={"base": "no_buttons"},
            )

        if user_input is not None:
            remove_button_id = str(user_input[CONF_BUTTON_ID])

            self._buttons = [
                button
                for button in self._buttons
                if button.get(CONF_BUTTON_ID) != remove_button_id
            ]

            return self.async_create_entry(
                title="",
                data={CONF_BUTTONS: self._buttons},
            )

        schema = vol.Schema(
            {
                vol.Required(CONF_BUTTON_ID): selector(
                    {
                        "select": {
                            "options": [
                                {
                                    "value": button[CONF_BUTTON_ID],
                                    "label": button[CONF_NAME],
                                }
                                for button in self._buttons
                            ]
                        }
                    }
                )
            }
        )

        return self.async_show_form(
            step_id="remove",
            data_schema=schema,
        )

    def _make_button_id(self, name: str) -> str:
        """Create unique button ID."""
        base_id = slugify(name) or "chime_button"
        existing_ids = {
            str(button.get(CONF_BUTTON_ID))
            for button in self._buttons
        }

        if base_id not in existing_ids:
            return base_id

        return f"{base_id}_{uuid4().hex[:8]}"


def _normalize_wildcard_value(value: Any) -> str:
    """Normalize optional match value.

    Empty value means wildcard.
    """
    if value is None:
        return MATCH_ANY

    value_str = str(value).strip()

    if value_str == "":
        return MATCH_ANY

    return value_str