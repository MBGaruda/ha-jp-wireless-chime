"""Receiver event bridge for JP Wireless Chime."""

from __future__ import annotations

import logging

from homeassistant.core import Event, HomeAssistant, callback

from .const import EVENT_CHIME_RECEIVED, EVENT_ESPHOME_RAW_RECEIVED
from .protocol import decode_received

_LOGGER = logging.getLogger(__name__)


def async_setup_receiver(hass: HomeAssistant) -> None:
    """Set up ESPHome raw event receiver."""

    @callback
    def handle_raw_received(event: Event) -> None:
        """Handle ESPHome raw chime event and fire normalized event."""
        data = event.data

        protocol_hint = data.get("protocol_hint")
        bits = data.get("bits")
        raw_hex = data.get("raw_hex")
        source = data.get("source")
        receiver_id = data.get("device_id")

        if not protocol_hint or not bits:
            _LOGGER.warning("Invalid chime raw event: %s", data)
            return

        try:
            decoded = decode_received(
                protocol_hint=str(protocol_hint),
                bits=str(bits),
                raw_hex=str(raw_hex) if raw_hex is not None else None,
            )
        except ValueError as err:
            _LOGGER.warning("Failed to decode chime event: %s", err)
            return

        if decoded is None:
            _LOGGER.debug(
                "Unsupported or undecodable chime raw event: protocol_hint=%s data=%s",
                protocol_hint,
                data,
            )
            return

        event_data = {
            **decoded,
            "source": source,
            "receiver_id": receiver_id,
        }

        hass.bus.async_fire(EVENT_CHIME_RECEIVED, event_data)

        _LOGGER.debug(
            "JP Wireless Chime normalized event fired: %s",
            event_data,
        )

    hass.bus.async_listen(EVENT_ESPHOME_RAW_RECEIVED, handle_raw_received)
    _LOGGER.info("JP Wireless Chime receiver event bridge initialized")