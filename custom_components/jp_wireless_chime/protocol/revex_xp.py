"""REVEX XP protocol implementation.

This module implements Base64 packet generation for REVEX XP series using the
validated logic from revex_xp_gen.py.
"""

from __future__ import annotations

import base64
from typing import Any

from .revex_x import GROUP_TO_INDEX, ID_CODE, INDEX_TO_GROUP, MELODY_CODE

CODE_TO_INDEX = {value: key for key, value in ID_CODE.items()}
CODE_TO_MELODY_IN_PAGE = {value: key for key, value in MELODY_CODE.items()}

XP_EXT_CODE_TO_OFFSET = {
    "00": 0,
    "40": 16,
    "10": 32,
    "50": 48,
}

HEADER_HEX = "78068403"
SUFFIX_HEX = "05dc00000000"

FRAME_SYNCS = [
    0x95,
    0x95,
    0x95,
    0x94,
    0x96,
    0x96,
    0x95,
    0x95,
    0x95,
    0x96,
    0x94,
    0x95,
]

FRAME_GAPS = [
    0x0A,
    0x0A,
    0x0A,
    0x0A,
    0x0A,
    0x0B,
    0x0B,
    0x0A,
    0x0A,
    0x0A,
    0x0A,
    None,
]

# XP学習波形から見た代表値
BIT_1 = (0x1E, 0x09)  # long, short
BIT_0 = (0x0A, 0x1D)  # short, long

BITS_PER_FRAME = 34
PULSES_PER_FRAME = 68
LEADING_LEN = 59
EXPECTED_PACKET_BYTES = 908


def hex_to_bits(hexstr: str) -> str:
    """Convert hex string to bit string."""
    return "".join(
        f"{int(hexstr[i:i + 2], 16):08b}"
        for i in range(0, len(hexstr), 2)
    )


def bits_to_hex(bits: str) -> str:
    """Convert REVEX XP 34-bit frame to uppercase 8-digit hex string."""
    if len(bits) != BITS_PER_FRAME:
        raise ValueError("REVEX XP bits length must be 34")

    payload_bits = bits[:32]
    padding_bits = bits[32:34]

    if padding_bits != "00":
        raise ValueError("REVEX XP trailing padding bits must be 00")

    return f"{int(payload_bits, 2):08X}"


def xp_ext_code(melody: int) -> str:
    """Return REVEX XP extension code for melody."""
    if melody <= 17:
        return "00"
    if melody <= 33:
        return "40"
    if melody <= 49:
        return "10"
    return "50"


def build_xp_hex(group: str, number: int, melody: int) -> str:
    """Build REVEX XP command hex."""
    group = group.upper()

    if group not in GROUP_TO_INDEX:
        raise ValueError("group must be A-P")
    if number not in ID_CODE:
        raise ValueError("number must be 1-16")
    if melody < 1 or melody > 64:
        raise ValueError("melody must be 1-64")

    melody_in_page = ((melody - 1) % 16) + 1

    return (
        ID_CODE[GROUP_TO_INDEX[group]]
        + ID_CODE[number]
        + MELODY_CODE[melody_in_page]
        + xp_ext_code(melody)
    )


def encode_bits(target_bits: str) -> bytes:
    """Encode REVEX XP bits to Broadlink pulse bytes."""
    if len(target_bits) != BITS_PER_FRAME:
        raise ValueError(f"target bits length is invalid: {len(target_bits)}")

    out = bytearray()

    for bit in target_bits:
        if bit == "1":
            out.extend(BIT_1)
        elif bit == "0":
            out.extend(BIT_0)
        else:
            raise ValueError("target bits must contain only 0 or 1")

    if len(out) != PULSES_PER_FRAME:
        raise ValueError(f"encoded frame length is invalid: {len(out)}")

    return bytes(out)


def build_packet(group: str, number: int, melody: int) -> bytes:
    """Build Broadlink packet for REVEX XP."""
    target_hex = build_xp_hex(group, number, melody)
    target_bits = hex_to_bits(target_hex) + "00"

    frame = encode_bits(target_bits)
    leading = frame[-LEADING_LEN:]

    out = bytearray()
    out.extend(bytes.fromhex(HEADER_HEX))
    out.extend(leading)

    for sync, gap in zip(FRAME_SYNCS, FRAME_GAPS):
        out.append(sync)
        out.extend(frame)
        if gap is not None:
            out.append(gap)

    out.extend(bytes.fromhex(SUFFIX_HEX))

    packet = bytes(out)

    if len(packet) != EXPECTED_PACKET_BYTES:
        raise ValueError(
            f"packet length mismatch: {len(packet)} != {EXPECTED_PACKET_BYTES}"
        )

    return packet


def generate_base64(channel: str, melody: int) -> str:
    """Generate Base64 code for REVEX XP protocol.

    Channel format: letter A-P plus number 1-16, e.g. "G13".
    Melody: 1-64.
    """
    if not isinstance(channel, str) or len(channel) < 2:
        raise ValueError("channel must be in format like 'G13' (letter + number)")

    group = channel[0].upper()

    try:
        number = int(channel[1:])
    except ValueError as err:
        raise ValueError(
            "channel must be in format like 'G13' (letter + number)"
        ) from err

    if group not in GROUP_TO_INDEX:
        raise ValueError("group must be A-P")
    if number not in ID_CODE:
        raise ValueError("number must be 1-16")
    if not 1 <= melody <= 64:
        raise ValueError("melody must be 1-64")

    packet = build_packet(group, number, melody)
    return base64.b64encode(packet).decode()


def decode_received(bits: str, raw_hex: str | None = None) -> dict[str, Any] | None:
    """Decode received REVEX XP raw bits."""
    if len(bits) != BITS_PER_FRAME:
        return None

    try:
        code_hex = raw_hex.upper() if raw_hex else bits_to_hex(bits)
    except ValueError:
        return None

    if len(code_hex) != 8:
        return None

    group_code = code_hex[0:2]
    number_code = code_hex[2:4]
    melody_code = code_hex[4:6]
    ext_code = code_hex[6:8]

    group_index = CODE_TO_INDEX.get(group_code)
    number = CODE_TO_INDEX.get(number_code)
    melody_in_page = CODE_TO_MELODY_IN_PAGE.get(melody_code)
    melody_offset = XP_EXT_CODE_TO_OFFSET.get(ext_code)

    if (
        group_index is None
        or number is None
        or melody_in_page is None
        or melody_offset is None
    ):
        return None

    group = INDEX_TO_GROUP[group_index]
    melody = melody_offset + melody_in_page
    channel = f"{group}{number}"

    return {
        "protocol": "revex_xp",
        "manufacturer": "revex",
        "series": "xp",
        "channel": channel,
        "group": group,
        "number": number,
        "melody": melody,
    }