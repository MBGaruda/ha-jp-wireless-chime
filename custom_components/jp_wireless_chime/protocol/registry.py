"""Protocol registry for JP Wireless Chime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable

from ..const import (
    MELODY_ALIASES,
    PROTOCOL_OHM_07,
    PROTOCOL_REVEX_X,
    PROTOCOL_REVEX_XP,
)
from . import ohm_07, revex_x, revex_xp

GenerateFunction = Callable[[Any, Any], str]
DecodeFunction = Callable[[str, str | None], dict[str, Any] | None]


@dataclass(frozen=True)
class ChimeProtocol:
    """Protocol definition for a supported wireless chime protocol."""

    key: str
    manufacturer: str
    series: str
    generate_base64: GenerateFunction
    decode_received: DecodeFunction


def _normalize_ohm_07_channel(channel: int | str) -> str | None:
    """Normalize OHM-07 channel value to 6-bit binary string."""
    if isinstance(channel, str):
        if len(channel) == 6 and set(channel) <= {"0", "1"}:
            return channel

        if channel.isdigit() and set(channel) <= {"0", "1"} and len(channel) <= 6:
            return channel.zfill(6)

        try:
            channel_int = int(channel)
        except ValueError:
            return None

        if 0 <= channel_int <= 0b111111:
            return format(channel_int, "06b")

        return None

    if isinstance(channel, int):
        if 0 <= channel <= 0b111111:
            return format(channel, "06b")

        return None

    return None


def _normalize_ohm_07_melody(melody: int | str) -> str | None:
    """Normalize OHM-07 melody value to 3-bit binary string."""
    if isinstance(melody, str):
        melody_str = melody.lower()

        if len(melody_str) == 3 and set(melody_str) <= {"0", "1"}:
            return melody_str

        alias_value = MELODY_ALIASES.get(PROTOCOL_OHM_07, {}).get(melody_str)
        if alias_value is not None:
            return str(alias_value)

        if melody_str.isdigit():
            melody_int = int(melody_str)
            if 0 <= melody_int <= 7:
                return format(melody_int, "03b")

        return None

    if isinstance(melody, int):
        if 0 <= melody <= 7:
            return format(melody, "03b")

        return None

    return None


def _normalize_numeric_melody(protocol: str, melody: int | str) -> int | None:
    """Normalize REVEX melody value to integer."""
    if isinstance(melody, int):
        return melody

    try:
        return int(str(melody))
    except ValueError:
        alias_value = MELODY_ALIASES.get(protocol, {}).get(str(melody).lower())
        if isinstance(alias_value, int):
            return alias_value

    return None


def _generate_revex_x(channel: int | str, melody: int | str) -> str:
    """Generate REVEX X Base64 code."""
    melody_value = _normalize_numeric_melody(PROTOCOL_REVEX_X, melody)

    if melody_value is None:
        raise ValueError(f"Invalid REVEX X melody value: {melody}")

    return revex_x.generate_base64(str(channel), melody_value)


def _generate_revex_xp(channel: int | str, melody: int | str) -> str:
    """Generate REVEX XP Base64 code."""
    melody_value = _normalize_numeric_melody(PROTOCOL_REVEX_XP, melody)

    if melody_value is None:
        raise ValueError(f"Invalid REVEX XP melody value: {melody}")

    return revex_xp.generate_base64(str(channel), melody_value)


def _generate_ohm_07(channel: int | str, melody: int | str) -> str:
    """Generate OHM-07 Base64 code."""
    channel_bits = _normalize_ohm_07_channel(channel)
    melody_bits = _normalize_ohm_07_melody(melody)

    if channel_bits is None:
        raise ValueError(f"Invalid OHM-07 channel value: {channel}")

    if melody_bits is None:
        raise ValueError(f"Invalid OHM-07 melody value: {melody}")

    return ohm_07.generate_base64(channel_bits, melody_bits)


PROTOCOLS: dict[str, ChimeProtocol] = {
    PROTOCOL_REVEX_X: ChimeProtocol(
        key=PROTOCOL_REVEX_X,
        manufacturer="revex",
        series="x",
        generate_base64=_generate_revex_x,
        decode_received=revex_x.decode_received,
    ),
    PROTOCOL_REVEX_XP: ChimeProtocol(
        key=PROTOCOL_REVEX_XP,
        manufacturer="revex",
        series="xp",
        generate_base64=_generate_revex_xp,
        decode_received=revex_xp.decode_received,
    ),
    PROTOCOL_OHM_07: ChimeProtocol(
        key=PROTOCOL_OHM_07,
        manufacturer="ohm",
        series="07",
        generate_base64=_generate_ohm_07,
        decode_received=ohm_07.decode_received,
    ),
}


def get_protocol(protocol: str) -> ChimeProtocol | None:
    """Return protocol definition by key."""
    return PROTOCOLS.get(protocol)


def generate_base64(protocol: str, channel: int | str, melody: int | str) -> str:
    """Generate Broadlink Base64 code using registered protocol."""
    protocol_definition = get_protocol(protocol)

    if protocol_definition is None:
        raise ValueError(f"Unsupported protocol: {protocol}")

    return protocol_definition.generate_base64(channel, melody)


def normalize_command(
    protocol: str,
    channel: int | str,
    melody: int | str,
) -> dict[str, Any]:
    """Normalize a send command to the same shape as received decoded data."""
    if protocol == PROTOCOL_OHM_07:
        channel_bits = _normalize_ohm_07_channel(channel)
        melody_bits = _normalize_ohm_07_melody(melody)

        if channel_bits is None:
            raise ValueError(f"Invalid OHM-07 channel value: {channel}")

        if melody_bits is None:
            raise ValueError(f"Invalid OHM-07 melody value: {melody}")

        return {
            "protocol": PROTOCOL_OHM_07,
            "channel": channel_bits,
            "melody": melody_bits,
        }

    if protocol == PROTOCOL_REVEX_X:
        melody_value = _normalize_numeric_melody(protocol, melody)

        if melody_value is None:
            raise ValueError(f"Invalid REVEX X melody value: {melody}")

        return {
            "protocol": PROTOCOL_REVEX_X,
            "channel": str(channel),
            "melody": melody_value,
        }

    if protocol == PROTOCOL_REVEX_XP:
        melody_value = _normalize_numeric_melody(protocol, melody)

        if melody_value is None:
            raise ValueError(f"Invalid REVEX XP melody value: {melody}")

        return {
            "protocol": PROTOCOL_REVEX_XP,
            "channel": str(channel),
            "melody": melody_value,
        }

    raise ValueError(f"Unsupported protocol: {protocol}")


def decode_received(
    protocol_hint: str,
    bits: str,
    raw_hex: str | None = None,
) -> dict[str, Any] | None:
    """Decode received raw event using registered protocol."""
    protocol_definition = get_protocol(protocol_hint)

    if protocol_definition is None:
        return None

    return protocol_definition.decode_received(bits, raw_hex)