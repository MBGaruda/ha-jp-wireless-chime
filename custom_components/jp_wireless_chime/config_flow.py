"""Config flow for JP Wireless Chime."""

from __future__ import annotations

from copy import deepcopy
import logging
from typing import Any
from uuid import uuid4

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.selector import selector
from homeassistant.util import slugify

from .const import (
    CONF_BUTTON_ID,
    CONF_CHANNEL,
    CONF_COOLDOWN,
    CONF_MELODY,
    CONF_NAME,
    CONF_PROTOCOL,
    CONF_RECEIVE_BUTTONS,
    CONF_RECEIVER,
    CONF_REMOTE_ENTITY_ID,
    CONF_SEND_BUTTONS,
    DEFAULT_COOLDOWN_SECONDS,
    DEVICE_KIND_RECEIVE,
    DEVICE_KIND_SEND,
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
        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        await self.async_set_unique_id(DOMAIN)
        self._abort_if_unique_id_configured()

        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_NAME],
                data={CONF_NAME: user_input[CONF_NAME]},
                options={
                    CONF_RECEIVE_BUTTONS: [],
                    CONF_SEND_BUTTONS: [],
                },
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
        self._receive_buttons: list[dict[str, Any]] = []
        self._send_buttons: list[dict[str, Any]] = []

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Manage options."""
        self._load_buttons()

        if user_input is not None:
            action = user_input["action"]

            if action == "add_receive":
                return await self.async_step_add_receive()

            if action == "remove_receive":
                return await self.async_step_remove_receive()

            if action == "add_send":
                return await self.async_step_add_send()

            if action == "remove_send":
                return await self.async_step_remove_send()

        schema = vol.Schema(
            {
                vol.Required("action", default="add_receive"): selector(
                    {
                        "select": {
                            "options": [
                                {
                                    "value": "add_receive",
                                    "label": "Add receive button",
                                },
                                {
                                    "value": "remove_receive",
                                    "label": "Remove receive button/device",
                                },
                                {
                                    "value": "add_send",
                                    "label": "Add send button",
                                },
                                {
                                    "value": "remove_send",
                                    "label": "Remove send button/device",
                                },
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

    async def async_step_add_receive(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Add a receive chime button."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = str(user_input[CONF_NAME])
            protocol = str(user_input[CONF_PROTOCOL])
            channel = _normalize_wildcard_value(user_input.get(CONF_CHANNEL))
            melody = _normalize_wildcard_value(user_input.get(CONF_MELODY))
            receiver = _normalize_wildcard_value(user_input.get(CONF_RECEIVER))
            cooldown = _normalize_cooldown(user_input.get(CONF_COOLDOWN))

            if channel != MATCH_ANY and melody != MATCH_ANY:
                try:
                    generate_base64(
                        protocol=protocol,
                        channel=channel,
                        melody=melody,
                    )
                except Exception as err:  # noqa: BLE001
                    _LOGGER.debug("Invalid receive button configuration: %s", err)
                    errors["base"] = "invalid_chime_button"

            if not errors:
                button_id = self._make_button_id(name, self._receive_buttons)

                self._receive_buttons.append(
                    {
                        CONF_BUTTON_ID: button_id,
                        CONF_NAME: name,
                        CONF_PROTOCOL: protocol,
                        CONF_CHANNEL: channel,
                        CONF_MELODY: melody,
                        CONF_RECEIVER: receiver,
                        CONF_COOLDOWN: cooldown,
                    }
                )

                return self._create_options_entry()

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_PROTOCOL): _protocol_selector(),
                vol.Optional(CONF_CHANNEL, default=MATCH_ANY): str,
                vol.Optional(CONF_MELODY, default=MATCH_ANY): str,
                vol.Optional(CONF_RECEIVER, default=MATCH_ANY): str,
                vol.Optional(
                    CONF_COOLDOWN,
                    default=DEFAULT_COOLDOWN_SECONDS,
                ): _cooldown_selector(),
            }
        )

        return self.async_show_form(
            step_id="add_receive",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_remove_receive(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Remove a receive chime button."""
        if not self._receive_buttons:
            return self.async_show_form(
                step_id="remove_receive",
                data_schema=vol.Schema({}),
                errors={"base": "no_receive_buttons"},
            )

        if user_input is not None:
            remove_button_id = str(user_input[CONF_BUTTON_ID])

            self._remove_chime_entity(DEVICE_KIND_RECEIVE, remove_button_id)
            self._remove_chime_device(DEVICE_KIND_RECEIVE, remove_button_id)

            self._receive_buttons = [
                button
                for button in self._receive_buttons
                if button.get(CONF_BUTTON_ID) != remove_button_id
            ]

            return self._create_options_entry()

        schema = vol.Schema(
            {
                vol.Required(CONF_BUTTON_ID): _button_selector(
                    self._receive_buttons
                )
            }
        )

        return self.async_show_form(
            step_id="remove_receive",
            data_schema=schema,
        )

    async def async_step_add_send(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Add a send chime button."""
        errors: dict[str, str] = {}

        if user_input is not None:
            name = str(user_input[CONF_NAME])
            protocol = str(user_input[CONF_PROTOCOL])
            channel = str(user_input[CONF_CHANNEL]).strip()
            melody = str(user_input[CONF_MELODY]).strip()
            remote_entity_id = str(user_input[CONF_REMOTE_ENTITY_ID]).strip()

            try:
                generate_base64(
                    protocol=protocol,
                    channel=channel,
                    melody=melody,
                )
            except Exception as err:  # noqa: BLE001
                _LOGGER.debug("Invalid send button configuration: %s", err)
                errors["base"] = "invalid_chime_button"

            if not remote_entity_id:
                errors["base"] = "invalid_remote_entity"

            if not errors:
                button_id = self._make_button_id(name, self._send_buttons)

                self._send_buttons.append(
                    {
                        CONF_BUTTON_ID: button_id,
                        CONF_NAME: name,
                        CONF_PROTOCOL: protocol,
                        CONF_CHANNEL: channel,
                        CONF_MELODY: melody,
                        CONF_REMOTE_ENTITY_ID: remote_entity_id,
                    }
                )

                return self._create_options_entry()

        schema = vol.Schema(
            {
                vol.Required(CONF_NAME): str,
                vol.Required(CONF_PROTOCOL): _protocol_selector(),
                vol.Required(CONF_CHANNEL): str,
                vol.Required(CONF_MELODY): str,
                vol.Required(CONF_REMOTE_ENTITY_ID): selector(
                    {
                        "entity": {
                            "domain": "remote",
                        }
                    }
                ),
            }
        )

        return self.async_show_form(
            step_id="add_send",
            data_schema=schema,
            errors=errors,
        )

    async def async_step_remove_send(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> config_entries.ConfigFlowResult:
        """Remove a send chime button."""
        if not self._send_buttons:
            return self.async_show_form(
                step_id="remove_send",
                data_schema=vol.Schema({}),
                errors={"base": "no_send_buttons"},
            )

        if user_input is not None:
            remove_button_id = str(user_input[CONF_BUTTON_ID])

            self._remove_chime_entity(DEVICE_KIND_SEND, remove_button_id)
            self._remove_chime_device(DEVICE_KIND_SEND, remove_button_id)

            self._send_buttons = [
                button
                for button in self._send_buttons
                if button.get(CONF_BUTTON_ID) != remove_button_id
            ]

            return self._create_options_entry()

        schema = vol.Schema(
            {
                vol.Required(CONF_BUTTON_ID): _button_selector(
                    self._send_buttons
                )
            }
        )

        return self.async_show_form(
            step_id="remove_send",
            data_schema=schema,
        )

    def _load_buttons(self) -> None:
        """Load buttons from options.

        Legacy buttons are treated as receive buttons.
        """
        legacy_buttons = deepcopy(self.config_entry.options.get("buttons", []))
        receive_buttons = deepcopy(
            self.config_entry.options.get(CONF_RECEIVE_BUTTONS, [])
        )

        if not receive_buttons and legacy_buttons:
            receive_buttons = legacy_buttons

        self._receive_buttons = receive_buttons
        self._send_buttons = deepcopy(
            self.config_entry.options.get(CONF_SEND_BUTTONS, [])
        )

    def _create_options_entry(self) -> config_entries.ConfigFlowResult:
        """Create options entry."""
        return self.async_create_entry(
            title="",
            data={
                CONF_RECEIVE_BUTTONS: self._receive_buttons,
                CONF_SEND_BUTTONS: self._send_buttons,
            },
        )

    def _make_button_id(
        self,
        name: str,
        buttons: list[dict[str, Any]],
    ) -> str:
        """Create unique button ID."""
        base_id = slugify(name) or "chime_button"
        existing_ids = {
            str(button.get(CONF_BUTTON_ID))
            for button in buttons
        }

        if base_id not in existing_ids:
            return base_id

        return f"{base_id}_{uuid4().hex[:8]}"

    def _remove_chime_entity(self, device_kind: str, button_id: str) -> None:
        """Remove entity for a registered chime button."""
        entity_registry = er.async_get(self.hass)

        unique_id = f"{self.config_entry.entry_id}_{device_kind}_{button_id}"
        platform = "event" if device_kind == DEVICE_KIND_RECEIVE else "button"

        entity_id = entity_registry.async_get_entity_id(
            platform,
            DOMAIN,
            unique_id,
        )

        if entity_id:
            entity_registry.async_remove(entity_id)

    def _remove_chime_device(self, device_kind: str, button_id: str) -> None:
        """Remove device for a registered chime button."""
        device_registry = dr.async_get(self.hass)

        device = device_registry.async_get_device(
            identifiers={
                (DOMAIN, f"{self.config_entry.entry_id}_{device_kind}_{button_id}")
            }
        )

        if device is None:
            return

        device_registry.async_update_device(
            device_id=device.id,
            remove_config_entry_id=self.config_entry.entry_id,
        )


def _protocol_selector() -> Any:
    """Return protocol selector."""
    return selector(
        {
            "select": {
                "options": [
                    {"value": protocol, "label": protocol}
                    for protocol in SUPPORTED_PROTOCOLS
                ]
            }
        }
    )


def _button_selector(buttons: list[dict[str, Any]]) -> Any:
    """Return button selector."""
    return selector(
        {
            "select": {
                "options": [
                    {
                        "value": button[CONF_BUTTON_ID],
                        "label": button[CONF_NAME],
                    }
                    for button in buttons
                ]
            }
        }
    )


def _cooldown_selector() -> Any:
    """Return cooldown selector."""
    return selector(
        {
            "number": {
                "min": 0,
                "max": 3600,
                "step": 1,
                "mode": "box",
                "unit_of_measurement": "s",
            }
        }
    )


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


def _normalize_cooldown(value: Any) -> int:
    """Normalize cooldown value."""
    if value is None:
        return DEFAULT_COOLDOWN_SECONDS

    try:
        cooldown = int(value)
    except (TypeError, ValueError):
        return DEFAULT_COOLDOWN_SECONDS

    if cooldown < 0:
        return DEFAULT_COOLDOWN_SECONDS

    return cooldown