"""Self-send ignore support for JP Wireless Chime."""

from __future__ import annotations

import logging
from time import monotonic
from typing import Any

from homeassistant.core import HomeAssistant

from .const import (
    DATA_SELF_SEND_IGNORE,
    DOMAIN,
    SELF_SEND_IGNORE_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


def register_self_send_ignore(
    hass: HomeAssistant,
    command: dict[str, Any],
    ttl_seconds: int = SELF_SEND_IGNORE_SECONDS,
) -> None:
    """Register a sent command so its received echo can be ignored."""
    ignore_records = hass.data.setdefault(DOMAIN, {}).setdefault(
        DATA_SELF_SEND_IGNORE,
        [],
    )

    expires_at = monotonic() + ttl_seconds

    record = {
        "protocol": str(command["protocol"]),
        "channel": str(command["channel"]),
        "melody": str(command["melody"]),
        "expires_at": expires_at,
    }

    ignore_records.append(record)

    _LOGGER.debug("Registered self-send ignore record: %s", record)


def should_ignore_self_send(
    hass: HomeAssistant,
    event_data: dict[str, Any],
) -> bool:
    """Return true if a received event matches a recent self-send command."""
    domain_data = hass.data.setdefault(DOMAIN, {})
    ignore_records = domain_data.setdefault(DATA_SELF_SEND_IGNORE, [])

    now = monotonic()
    active_records = []

    should_ignore = False

    for record in ignore_records:
        if record.get("expires_at", 0) <= now:
            continue

        active_records.append(record)

        if (
            str(event_data.get("protocol")) == str(record.get("protocol"))
            and str(event_data.get("channel")) == str(record.get("channel"))
            and str(event_data.get("melody")) == str(record.get("melody"))
        ):
            should_ignore = True

    domain_data[DATA_SELF_SEND_IGNORE] = active_records

    if should_ignore:
        _LOGGER.debug("Ignoring self-send echo event: %s", event_data)

    return should_ignore