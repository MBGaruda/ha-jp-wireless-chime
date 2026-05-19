"""Receiver event bridge for JP Wireless Chime."""

from __future__ import annotations

import logging
from typing import Any, Callable

from homeassistant.core import Event, HomeAssistant, callback

from .const import (
    DATA_EVENT_ENTITIES,
    DOMAIN,
    EVENT_CHIME_RECEIVED,
    EVENT_ESPHOME_RAW_RECEIVED,
)
from .protocol import decode_received

_LOGGER = logging.getLogger(__name__)


def async_setup_receiver(hass: HomeAssistant) -> Callable[[], None]:
    """Set up ESPHome raw event receiver."""

    @callback
    def handle_raw_received(event: Event) -> None:
        """Handle ESPHome raw chime event and fire normalized event."""
        data = event.data

        protocol_hint = data.get("protocol_hint")
        bits = data.get("bits")
        raw_hex = data.get("raw_hex")
        receiver = data.get("source")

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
            "receiver": str(receiver) if receiver is not None else None,
        }

        hass.bus.async_fire(EVENT_CHIME_RECEIVED, event_data)

        _LOGGER.debug(
            "JP Wireless Chime normalized event fired: %s",
            event_data,
        )

        _trigger_matching_event_entities(hass, event_data)

    unsub = hass.bus.async_listen(EVENT_ESPHOME_RAW_RECEIVED, handle_raw_received)
    _LOGGER.info("JP Wireless Chime receiver event bridge initialized")

    return unsub


def _trigger_matching_event_entities(
    hass: HomeAssistant,
    event_data: dict[str, Any],
) -> None:
    """Trigger registered event entities matching normalized chime event."""
    entities = hass.data.get(DOMAIN, {}).get(DATA_EVENT_ENTITIES, {})

    for entity in list(entities.values()):
        if entity.matches(event_data):
            entity.trigger_pressed(event_data)