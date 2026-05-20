"""JP Wireless Chime integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_BUTTONS,
    CONF_BUTTON_ID,
    CONF_CHANNEL,
    CONF_MELODY,
    CONF_PROTOCOL,
    CONF_REMOTE_ENTITY_ID,
    DATA_RECEIVER_SETUP_DONE,
    DATA_RECEIVER_UNSUB,
    DATA_SERVICES_SETUP_DONE,
    DOMAIN,
    SERVICE_SEND_CHIME,
    SUPPORTED_PROTOCOLS,
)
from .protocol import generate_base64, normalize_command
from .receiver import async_setup_receiver
from .self_send import register_self_send_ignore

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.EVENT]

SEND_CHIME_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PROTOCOL): vol.In(SUPPORTED_PROTOCOLS),
        vol.Required(CONF_CHANNEL): vol.Any(cv.positive_int, cv.string),
        vol.Required(CONF_MELODY): vol.Any(cv.positive_int, cv.string),
        vol.Required(CONF_REMOTE_ENTITY_ID): cv.entity_id,
    }
)


async def async_setup_services(hass: HomeAssistant) -> bool:
    """Register services and receiver for JP Wireless Chime."""
    domain_data = hass.data.setdefault(DOMAIN, {})

    if not domain_data.get(DATA_SERVICES_SETUP_DONE):

        async def handle_send_chime(call: ServiceCall) -> None:
            """Handle the send_chime service call."""
            protocol = call.data[CONF_PROTOCOL]
            channel = call.data[CONF_CHANNEL]
            melody = call.data[CONF_MELODY]
            remote_entity_id = call.data[CONF_REMOTE_ENTITY_ID]

            _LOGGER.info(
                "JP Wireless Chime send requested: protocol=%s, channel=%s, melody=%s, remote=%s",
                protocol,
                channel,
                melody,
                remote_entity_id,
            )

            try:
                base64_code = generate_base64(
                    protocol=str(protocol),
                    channel=channel,
                    melody=melody,
                )

                normalized_command = normalize_command(
                    protocol=str(protocol),
                    channel=channel,
                    melody=melody,
                )

                register_self_send_ignore(hass, normalized_command)

                _LOGGER.debug("JP Wireless Chime base64 payload: %s", base64_code)

                await hass.services.async_call(
                    "remote",
                    "send_command",
                    {
                        "entity_id": remote_entity_id,
                        "command": f"b64:{base64_code}",
                    },
                    blocking=True,
                )

                _LOGGER.info("JP Wireless Chime command sent successfully")

            except Exception as err:  # noqa: BLE001
                _LOGGER.error("Error sending JP Wireless Chime command: %s", err)

        hass.services.async_register(
            DOMAIN,
            SERVICE_SEND_CHIME,
            handle_send_chime,
            schema=SEND_CHIME_SCHEMA,
        )

        domain_data[DATA_SERVICES_SETUP_DONE] = True

    if not domain_data.get(DATA_RECEIVER_SETUP_DONE):
        domain_data[DATA_RECEIVER_UNSUB] = async_setup_receiver(hass)
        domain_data[DATA_RECEIVER_SETUP_DONE] = True

    return True


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up JP Wireless Chime from YAML configuration."""
    await async_setup_services(hass)
    _LOGGER.info("JP Wireless Chime initialized")
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up JP Wireless Chime from a config entry."""
    await async_setup_services(hass)

    entry.async_on_unload(entry.add_update_listener(async_update_listener))

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    _LOGGER.info("JP Wireless Chime config entry initialized")
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a JP Wireless Chime config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload JP Wireless Chime when options are updated."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_remove_config_entry_device(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device_entry: dr.DeviceEntry,
) -> bool:
    """Remove a chime button device from the config entry.

    This is called by Home Assistant when the user removes a device from the UI.
    """
    button_id = _get_button_id_from_device_entry(entry, device_entry)

    if button_id is None:
        _LOGGER.debug(
            "Device is not a JP Wireless Chime button device: %s",
            device_entry.id,
        )
        return False

    buttons = list(entry.options.get(CONF_BUTTONS, []))
    remaining_buttons = [
        button
        for button in buttons
        if str(button.get(CONF_BUTTON_ID)) != button_id
    ]

    if len(remaining_buttons) == len(buttons):
        _LOGGER.debug(
            "No matching JP Wireless Chime button found for device removal: button_id=%s",
            button_id,
        )
        return False

    _remove_button_entity(hass, entry, button_id)

    new_options = dict(entry.options)
    new_options[CONF_BUTTONS] = remaining_buttons
    hass.config_entries.async_update_entry(entry, options=new_options)

    _LOGGER.info(
        "Removed JP Wireless Chime button via device removal: button_id=%s",
        button_id,
    )

    return True


def _get_button_id_from_device_entry(
    entry: ConfigEntry,
    device_entry: dr.DeviceEntry,
) -> str | None:
    """Extract button ID from a JP Wireless Chime button device entry."""
    expected_prefix = f"{entry.entry_id}_"

    for domain, identifier in device_entry.identifiers:
        if domain != DOMAIN:
            continue

        identifier_str = str(identifier)

        if not identifier_str.startswith(expected_prefix):
            continue

        button_id = identifier_str[len(expected_prefix):]

        if button_id:
            return button_id

    return None


def _remove_button_entity(
    hass: HomeAssistant,
    entry: ConfigEntry,
    button_id: str,
) -> None:
    """Remove event entity for a registered chime button."""
    entity_registry = er.async_get(hass)

    unique_id = f"{entry.entry_id}_{button_id}"

    entity_id = entity_registry.async_get_entity_id(
        "event",
        DOMAIN,
        unique_id,
    )

    if entity_id:
        _LOGGER.info(
            "Removing JP Wireless Chime entity: %s",
            entity_id,
        )
        entity_registry.async_remove(entity_id)