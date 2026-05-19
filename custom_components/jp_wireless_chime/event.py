"""Event entities for JP Wireless Chime."""

from __future__ import annotations

from typing import Any

from homeassistant.components.event import EventEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_BUTTON_ID,
    CONF_BUTTONS,
    CONF_CHANNEL,
    CONF_MELODY,
    CONF_NAME,
    CONF_PROTOCOL,
    CONF_RECEIVER,
    DATA_EVENT_ENTITIES,
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
    buttons = entry.options.get(CONF_BUTTONS, [])

    entities = [
        JPWirelessChimeButtonEventEntity(entry, button)
        for button in buttons
    ]

    async_add_entities(entities)


class JPWirelessChimeButtonEventEntity(EventEntity):
    """Event entity for a registered wireless chime button."""

    _attr_event_types = [EVENT_TYPE_PRESSED]
    _attr_has_entity_name = True

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

        self._attr_unique_id = f"{entry.entry_id}_{self._button_id}"
        self._attr_name = self._name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title,
            "manufacturer": "JP Wireless Chime",
            "model": "Wireless Chime Receiver",
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
            "protocol": self._protocol,
            "channel": self._channel,
            "melody": self._melody,
            "receiver": self._receiver,
        }

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
        self._trigger_event(
            EVENT_TYPE_PRESSED,
            {
                "protocol": event_data.get("protocol"),
                "channel": event_data.get("channel"),
                "melody": event_data.get("melody"),
                "receiver": event_data.get("receiver"),
            },
        )
        self.async_write_ha_state()


def _normalize_match_value(value: Any) -> str:
    """Normalize a match field value."""
    if value is None:
        return MATCH_ANY

    value_str = str(value).strip()

    if value_str == "":
        return MATCH_ANY

    return value_str


def _match_field(expected: str, actual: Any) -> bool:
    """Match a field with wildcard support."""
    if expected == MATCH_ANY:
        return True

    if actual is None:
        return False

    return expected == str(actual)