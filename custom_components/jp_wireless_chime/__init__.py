"""JP Wireless Chime integration."""

from __future__ import annotations

import logging

import voluptuous as vol

from homeassistant.core import HomeAssistant, ServiceCall
import homeassistant.helpers.config_validation as cv

from .const import (
    CONF_CHANNEL,
    CONF_MELODY,
    CONF_PROTOCOL,
    CONF_REMOTE_ENTITY_ID,
    DOMAIN,
    PROTOCOL_OHM_07,
    PROTOCOL_REVEX_X,
    SERVICE_SEND_CHIME,
    SUPPORTED_PROTOCOLS,
    MELODY_ALIASES,
)
from .protocol import ohm_07, revex_x

_LOGGER = logging.getLogger(__name__)

SEND_CHIME_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PROTOCOL): vol.In(SUPPORTED_PROTOCOLS),
        vol.Required(CONF_CHANNEL): vol.Any(cv.positive_int, cv.string),
        vol.Required(CONF_MELODY): vol.Any(cv.positive_int, cv.string),
        vol.Required(CONF_REMOTE_ENTITY_ID): cv.entity_id,
    }
)


async def async_setup_services(hass: HomeAssistant) -> bool:
    """Register services for JP Wireless Chime."""

    async def handle_send_chime(call: ServiceCall) -> None:
        """Handle the send_chime service call."""
        protocol = call.data[CONF_PROTOCOL]
        channel = call.data[CONF_CHANNEL]
        melody_input = call.data[CONF_MELODY]
        # Normalize melody: accept int, numeric string, or alias
        melody = None
        if isinstance(melody_input, int):
            melody = melody_input
        else:
            try:
                melody = int(str(melody_input))
            except Exception:
                # lookup alias (case-insensitive)
                aliases = MELODY_ALIASES.get(protocol, {})
                melody = aliases.get(str(melody_input).lower())

        if melody is None:
            _LOGGER.error("Invalid melody value: %s", melody_input)
            return
        remote_entity_id = call.data[CONF_REMOTE_ENTITY_ID]

        _LOGGER.info(
            "JP Wireless Chime send requested: protocol=%s, channel=%s, melody=%s, remote=%s",
            protocol,
            channel,
            melody,
            remote_entity_id,
        )

        try:
            # Generate Base64 code based on protocol
            if protocol == PROTOCOL_OHM_07:
                # Convert channel string to integer
                try:
                    channel_int = int(channel)
                except ValueError:
                    _LOGGER.error("OHM-07 channel must be a number (1-64), got: %s", channel)
                    return
                base64_code = ohm_07.generate_base64(channel_int, melody)
            elif protocol == PROTOCOL_REVEX_X:
                # Channel should be in format like "G13"
                base64_code = revex_x.generate_base64(channel, melody)
            else:
                _LOGGER.error("Unsupported protocol: %s", protocol)
                return

            # Send the command via Broadlink remote
            await hass.services.async_call(
                "remote",
                "send_command",
                {
                    "entity_id": remote_entity_id,
                    "command": f"b64:{base64_code}",
                },
            )

            _LOGGER.info("JP Wireless Chime command sent successfully")

        except Exception as err:
            _LOGGER.error("Error sending JP Wireless Chime command: %s", err)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_CHIME,
        handle_send_chime,
        schema=SEND_CHIME_SCHEMA,
    )

    _LOGGER.info("JP Wireless Chime initialized")
    return True


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up JP Wireless Chime from YAML configuration."""
    return await async_setup_services(hass)


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up JP Wireless Chime from a config entry."""
    return await async_setup_services(hass)
    