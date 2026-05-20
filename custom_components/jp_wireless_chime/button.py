"""Button entities for JP Wireless Chime."""

from __future__ import annotations

from typing import Any

from homeassistant.components.button import ButtonEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import (
    CONF_BUTTON_ID,
    CONF_CHANNEL,
    CONF_MELODY,
    CONF_NAME,
    CONF_PROTOCOL,
    CONF_REMOTE_ENTITY_ID,
    CONF_SEND_BUTTONS,
    DEVICE_KIND_SEND,
    DOMAIN,
)
from .protocol import generate_base64, normalize_command
from .self_send import register_self_send_ignore


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up JP Wireless Chime send button entities."""
    buttons = entry.options.get(CONF_SEND_BUTTONS, [])

    entities = [
        JPWirelessChimeSendButtonEntity(entry, button)
        for button in buttons
    ]

    async_add_entities(entities)


class JPWirelessChimeSendButtonEntity(ButtonEntity):
    """Button entity for sending a wireless chime signal."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:radio-tower"

    def __init__(
        self,
        entry: ConfigEntry,
        button: dict[str, Any],
    ) -> None:
        """Initialize the send button entity."""
        self._entry = entry
        self._button = button

        self._button_id = str(button[CONF_BUTTON_ID])
        self._name = str(button[CONF_NAME])
        self._protocol = str(button[CONF_PROTOCOL])
        self._channel = str(button[CONF_CHANNEL])
        self._melody = str(button[CONF_MELODY])
        self._remote_entity_id = str(button[CONF_REMOTE_ENTITY_ID])

        self._attr_unique_id = (
            f"{entry.entry_id}_{DEVICE_KIND_SEND}_{self._button_id}"
        )
        self._attr_name = None
        self._attr_device_info = {
            "identifiers": {
                (DOMAIN, f"{entry.entry_id}_{DEVICE_KIND_SEND}_{self._button_id}")
            },
            "name": self._name,
            "manufacturer": "JP Wireless Chime",
            "model": "Wireless Chime Send Button",
        }

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return entity attributes."""
        return {
            "button_id": self._button_id,
            "direction": "send",
            "protocol": self._protocol,
            "channel": self._channel,
            "melody": self._melody,
            "remote_entity_id": self._remote_entity_id,
            "send_rule": self._send_rule,
        }

    @property
    def _send_rule(self) -> str:
        """Return human-readable send rule."""
        return (
            f"protocol={self._protocol}, "
            f"channel={self._channel}, "
            f"melody={self._melody}, "
            f"remote={self._remote_entity_id}"
        )

    async def async_press(self) -> None:
        """Send the configured wireless chime signal."""
        base64_code = generate_base64(
            protocol=self._protocol,
            channel=self._channel,
            melody=self._melody,
        )

        normalized_command = normalize_command(
            protocol=self._protocol,
            channel=self._channel,
            melody=self._melody,
        )

        register_self_send_ignore(self.hass, normalized_command)

        await self.hass.services.async_call(
            "remote",
            "send_command",
            {
                "entity_id": self._remote_entity_id,
                "command": f"b64:{base64_code}",
            },
            blocking=True,
        )