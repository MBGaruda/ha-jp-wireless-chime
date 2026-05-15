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
    SERVICE_SEND_CHIME,
    SUPPORTED_PROTOCOLS,
)

_LOGGER = logging.getLogger(__name__)

SEND_CHIME_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_PROTOCOL): vol.In(SUPPORTED_PROTOCOLS),
        vol.Required(CONF_CHANNEL): cv.positive_int,
        vol.Required(CONF_MELODY): cv.positive_int,
        vol.Required(CONF_REMOTE_ENTITY_ID): cv.entity_id,
    }
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up JP Wireless Chime."""

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

        # TODO:
        # 1. Generate Broadlink Base64 code from protocol/channel/melody.
        # 2. Call remote.send_command with command="b64:<generated_code>".

    hass.services.async_register(
        DOMAIN,
        SERVICE_SEND_CHIME,
        handle_send_chime,
        schema=SEND_CHIME_SCHEMA,
    )

    _LOGGER.info("JP Wireless Chime initialized")
    return True
    