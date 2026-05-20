"""Event entities for JP Wireless Chime."""

from __future__ import annotations

from time import monotonic
from typing import Any

from homeassistant.components.event import EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_BUTTON_ID,
    CONF_CHANNEL,
    CONF_COOLDOWN,
    CONF_MELODY,
    CONF_NAME,
    CONF_PROTOCOL,
    CONF_RECEIVE_BUTTONS,
    CONF_RECEIVER,
    DATA_EVENT_ENTITIES,
    DEFAULT_COOLDOWN_SECONDS,
    DEVICE_KIND_RECEIVE,
    DOMAIN,
    EVENT_TYPE_PRESSED,
    MATCH_ANY,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JP Wireless Chime event entities."""
    buttons = entry.options.get(CONF_RECEIVE_BUTTONS, [])

    entities = [
        JPWirelessChimeReceiveEventEntity(entry, button)
        for button in buttons
    ]

    async_add_entities(entities)


class JPWirelessChimeReceiveEventEntity(EventEntity):
    """Event entity for a registered wireless chime receive button."""

    _attr_event_types = [EVENT_TYPE_PRESSED]
    _attr_has_entity_name = True
    _attr_icon = "mdi:bell-ring-outline"

    def __init__(
        self,
        entry: ConfigEntry,
        button: dict[str, Any],
    ) -> None:
        """Initialize the event entity."""
        self._entry = entry
        self._button = button

        self._button_id = str(button[CONF_BUTTON_ID])
        self._name = str(button[CONF_NAME])
        self._protocol = str(button[CONF_PROTOCOL])
        self._channel = _normalize_match_value(button.get(CONF_CHANNEL))
        self._melody = _normalize_match_value(button.get(CONF_MELODY))
        self._receiver = _normalize_match_value(button.get(CONF_RECEIVER))
        self._cooldown = _normalize_cooldown(button.get(CONF_COOLDOWN))

        self._last_triggered_at: float | None = None

        self._attr_unique_id = (
            f"{entry.entry_id}_{DEVICE_KIND_RECEIVE}_{self._button_id}"
        )
        self._attr_name = None
        self._attr_device_info = {
            "identifiers": {
                (DOMAIN, f"{entry.entry_id}_{DEVICE_KIND_RECEIVE}_{self._button_id}")
            },
            "name": self._name,
            "manufacturer": "JP Wireless Chime",
            "model": "Wireless Chime Receive Button",
        }

    async def async_added_to_hass(self) -> None:
        """Register entity for receiver matching."""
        domain_data = self.hass.data.setdefault(DOMAIN, {})
        entities = domain_data.setdefault(DATA_EVENT_ENTITIES, {})
        entities[self.entity_id] = self

    async def async_will_remove_from_hass(self) -> None:
        """Unregister entity from receiver matching."""
        entities = self.hass.data.get(DOMAIN, {}).get(DATA_EVENT_ENTITIES, {})
        entities.pop(self.entity_id, None)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity attributes."""
        return {
            "button_id": self._button_id,
            "direction": "receive",
            "protocol": self._protocol,
            "channel": self._channel,
            "melody": self._melody,
            "receiver": self._receiver,
            "cooldown": self._cooldown,
            "match_rule": self._match_rule,
        }

    @property
    def _match_rule(self) -> str:
        """Return human-readable match rule."""
        return (
            f"protocol={self._protocol}, "
            f"channel={self._channel}, "
            f"melody={self._melody}, "
            f"receiver={self._receiver}"
        )

    def matches(self, event_data: dict[str, Any]) -> bool:
        """Return true if normalized chime event matches this button."""
        return (
            str(event_data.get("protocol")) == self._protocol
            and _match_field(self._channel, event_data.get("channel"))
            and _match_field(self._melody, event_data.get("melody"))
            and _match_field(self._receiver, event_data.get("receiver"))
        )

    def trigger_pressed(self, event_data: dict[str, Any]) -> None:
        """Trigger pressed event."""
        if self._is_in_cooldown():
            return

        self._last_triggered_at = monotonic()

        self._trigger_event(
            EVENT_TYPE_PRESSED,
            {
                "protocol": event_data.get("protocol"),
                "channel": event_data.get("channel"),
                "melody": event_data.get("melody"),
                "receiver": event_data.get("receiver"),
                "match_rule": self._match_rule,
            },
        )

        self.async_write_ha_state()

    def _is_in_cooldown(self) -> bool:
        """Return true if the entity is still in cooldown."""
        if self._cooldown <= 0:
            return False

        if self._last_triggered_at is None:
            return False

        return monotonic() - self._last_triggered_at < self._cooldown


def _normalize_match_value(value: Any) -> str:
    """Normalize a match field value."""
    if value is None:
        return MATCH_ANY

    value_str = str(value).strip()

    if value_str == "":
        return MATCH_ANY

    return value_str


def _normalize_cooldown(value: Any) -> int:
    """Normalize cooldown value."""
    if value is None:
        return DEFAULT_COOLDOWN_SECONDS

    try:
        cooldown = int(value)
    except (TypeError, ValueError):
        return DEFAULT_COOLDOWN_SECONDS

    if cooldown < 0:
        return DEFAULT_COOLDOWN_SECONDS

    return cooldown


def _match_field(expected: str, actual: Any) -> bool:
    """Match a field with wildcard support."""
    if expected == MATCH_ANY:
        return True

    if actual is None:
        return False

    return expected == str(actual)