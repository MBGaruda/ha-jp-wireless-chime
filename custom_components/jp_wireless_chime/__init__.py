"""JP Wireless Chime integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import entity_registry as er
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_BUTTON_ID,
    CONF_CHANNEL,
    CONF_MELODY,
    CONF_PROTOCOL,
    CONF_RECEIVE_BUTTONS,
    CONF_REMOTE_ENTITY_ID,
    CONF_SEND_BUTTONS,
    DATA_RECEIVER_SETUP_DONE,
    DATA_RECEIVER_UNSUB,
    DATA_SERVICES_SETUP_DONE,
    DEVICE_KIND_RECEIVE,
    DEVICE_KIND_SEND,
    DOMAIN,
    SERVICE_SEND_CHIME,
    SUPPORTED_PROTOCOLS,
)
from .protocol import generate_base64, normalize_command
from .receiver import async_setup_receiver
from .self_send import register_self_send_ignore

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.EVENT, Platform.BUTTON]

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
    """Remove a chime device from the config entry."""
    parsed = _parse_chime_device_identifier(entry, device_entry)

    if parsed is None:
        return False

    device_kind, button_id = parsed

    if device_kind == DEVICE_KIND_RECEIVE:
        options_key = CONF_RECEIVE_BUTTONS
    elif device_kind == DEVICE_KIND_SEND:
        options_key = CONF_SEND_BUTTONS
    else:
        return False

    buttons = list(entry.options.get(options_key, []))
    remaining_buttons = [
        button
        for button in buttons
        if str(button.get(CONF_BUTTON_ID)) != button_id
    ]

    if len(remaining_buttons) == len(buttons):
        return False

    _remove_chime_entity(hass, entry, device_kind, button_id)

    new_options = dict(entry.options)
    new_options[options_key] = remaining_buttons
    hass.config_entries.async_update_entry(entry, options=new_options)

    _LOGGER.info(
        "Removed JP Wireless Chime %s device via device removal: button_id=%s",
        device_kind,
        button_id,
    )

    return True


def _parse_chime_device_identifier(
    entry: ConfigEntry,
    device_entry: dr.DeviceEntry,
) -> tuple[str, str] | None:
    """Extract device kind and button ID from a chime device entry."""
    receive_prefix = f"{entry.entry_id}_{DEVICE_KIND_RECEIVE}_"
    send_prefix = f"{entry.entry_id}_{DEVICE_KIND_SEND}_"

    for domain, identifier in device_entry.identifiers:
        if domain != DOMAIN:
            continue

        identifier_str = str(identifier)

        if identifier_str.startswith(receive_prefix):
            return DEVICE_KIND_RECEIVE, identifier_str[len(receive_prefix):]

        if identifier_str.startswith(send_prefix):
            return DEVICE_KIND_SEND, identifier_str[len(send_prefix):]

    return None


def _remove_chime_entity(
    hass: HomeAssistant,
    entry: ConfigEntry,
    device_kind: str,
    button_id: str,
) -> None:
    """Remove entity for a registered chime device."""
    entity_registry = er.async_get(hass)

    unique_id = f"{entry.entry_id}_{device_kind}_{button_id}"

    platform = "event" if device_kind == DEVICE_KIND_RECEIVE else "button"

    entity_id = entity_registry.async_get_entity_id(
        platform,
        DOMAIN,
        unique_id,
    )

    if entity_id:
        _LOGGER.info("Removing JP Wireless Chime entity: %s", entity_id)
        entity_registry.async_remove(entity_id)