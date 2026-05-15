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

        melody_bits = None
        melody_value = None
        if protocol == PROTOCOL_OHM_07:
            # OHM-07: melody can be 3-bit string "001", integer 0-7, or alias name
            if isinstance(melody_input, str):
                melody_str = melody_input.lower()
                if len(melody_str) == 3 and set(melody_str) <= {"0", "1"}:
                    melody_bits = melody_str
                else:
                    melody_bits = MELODY_ALIASES.get(PROTOCOL_OHM_07, {}).get(melody_str)
            elif isinstance(melody_input, int):
                if 0 <= melody_input <= 7:
                    melody_bits = format(melody_input, "03b")
                else:
                    # Try interpreting as 3-bit string (e.g., 10 -> "010")
                    melody_str = str(melody_input).zfill(3)
                    if len(melody_str) == 3 and set(melody_str) <= {"0", "1"}:
                        melody_bits = melody_str
            else:
                melody_str = str(melody_input).lower()
                melody_bits = MELODY_ALIASES.get(PROTOCOL_OHM_07, {}).get(melody_str)

            if melody_bits is None:
                _LOGGER.error("Invalid OHM-07 melody value: %s", melody_input)
                return
        else:
            if isinstance(melody_input, int):
                melody_value = melody_input
            else:
                try:
                    melody_value = int(str(melody_input))
                except Exception:
                    aliases = MELODY_ALIASES.get(protocol, {})
                    melody_value = aliases.get(str(melody_input).lower())

            if melody_value is None:
                _LOGGER.error("Invalid melody value: %s", melody_input)
                return

        remote_entity_id = call.data[CONF_REMOTE_ENTITY_ID]

        _LOGGER.info(
            "JP Wireless Chime send requested: protocol=%s, channel=%s, melody=%s, remote=%s",
            protocol,
            channel,
            melody_input,
            remote_entity_id,
        )

        try:
            # Generate Base64 code based on protocol
            if protocol == PROTOCOL_OHM_07:
                channel_bits = None
                if isinstance(channel, str):
                    if len(channel) == 6 and set(channel) <= {"0", "1"}:
                        channel_bits = channel
                    elif channel.isdigit() and set(channel) <= {"0", "1"} and len(channel) <= 6:
                        channel_bits = channel.zfill(6)
                    else:
                        try:
                            channel_int = int(channel)
                        except ValueError:
                            _LOGGER.error("OHM-07 channel must be a 6-bit string or number, got: %s", channel)
                            return
                        if 0 <= channel_int <= 0b111111:
                            channel_bits = format(channel_int, "06b")
                        else:
                            channel_str = str(channel_int)
                            if len(channel_str) == 6 and set(channel_str) <= {"0", "1"}:
                                channel_bits = channel_str
                            else:
                                _LOGGER.error("OHM-07 channel must be a 6-bit string or number, got: %s", channel)
                                return
                elif isinstance(channel, int):
                    if 0 <= channel <= 0b111111:
                        channel_bits = format(channel, "06b")
                    else:
                        channel_str = str(channel)
                        if len(channel_str) == 6 and set(channel_str) <= {"0", "1"}:
                            channel_bits = channel_str
                        else:
                            _LOGGER.error("OHM-07 channel must be a 6-bit string or number, got: %s", channel)
                            return
                else:
                    _LOGGER.error("OHM-07 channel must be a 6-bit string or number, got: %s", channel)
                    return

                _LOGGER.debug("OHM-07 channel_bits=%s melody_bits=%s", channel_bits, melody_bits)
                base64_code = ohm_07.generate_base64(channel_bits, melody_bits)
            elif protocol == PROTOCOL_REVEX_X:
                base64_code = revex_x.generate_base64(channel, melody_value)
            else:
                _LOGGER.error("Unsupported protocol: %s", protocol)
                return

            _LOGGER.debug("JP Wireless Chime base64 payload: %s", base64_code)

            # Send the command via Broadlink remote
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
    