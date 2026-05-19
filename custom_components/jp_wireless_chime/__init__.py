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
from .protocol import generate_base64
from .receiver import async_setup_receiver

_LOGGER = logging.getLogger(__name__)

DATA_RECEIVER_SETUP_DONE = "receiver_setup_done"
DATA_SERVICES_SETUP_DONE = "services_setup_done"

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
        async_setup_receiver(hass)
        domain_data[DATA_RECEIVER_SETUP_DONE] = True

    _LOGGER.info("JP Wireless Chime initialized")
    return True


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Set up JP Wireless Chime from YAML configuration."""
    return await async_setup_services(hass)


async def async_setup_entry(hass: HomeAssistant, entry) -> bool:
    """Set up JP Wireless Chime from a config entry."""
    return await async_setup_services(hass)