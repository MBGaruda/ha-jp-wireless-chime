"""Receiver event bridge for JP Wireless Chime."""

from __future__ import annotations

import logging
from typing import Any, Callable

from homeassistant.core import Event, HomeAssistant, callback

from .const import EVENT_CHIME_RECEIVED, EVENT_ESPHOME_RAW_RECEIVED
from .protocol import ohm_07, revex_x, revex_xp

_LOGGER = logging.getLogger(__name__)

Decoder = Callable[[str, str | None], dict[str, Any] | None]

DECODERS: dict[str, Decoder] = {
    "revex_x": revex_x.decode_received,
    "revex_xp": revex_xp.decode_received,
    "ohm_07": ohm_07.decode_received,
}


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

        decoder = DECODERS.get(str(protocol_hint))
        if decoder is None:
            _LOGGER.debug("Unsupported chime protocol hint: %s", protocol_hint)
            return

        try:
            decoded = decoder(str(bits), str(raw_hex) if raw_hex is not None else None)
        except ValueError as err:
            _LOGGER.warning("Failed to decode chime event: %s", err)
            return

        if decoded is None:
            _LOGGER.debug("Chime decoder returned no match: %s", data)
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