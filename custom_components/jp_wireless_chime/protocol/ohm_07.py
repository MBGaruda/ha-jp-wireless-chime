"""OHM 07 protocol implementation."""

from __future__ import annotations

import base64
from typing import Any

HEADER_HEX = "78068403"
SUFFIX_HEX = "05dc00000000"

PULSE_0 = bytes([0x08, 0x14])
PULSE_1 = bytes([0x15, 0x07])
OHM_SYNC = bytes([0x08, 0x8A])

DEFAULT_LEADING_LEN = 44
DEFAULT_REPEAT = 23


def encode_dip_bit(bit: str) -> str:
    """Encode OHM DIP bit to protocol pair."""
    if bit == "0":
        return "01"
    if bit == "1":
        return "00"
    raise ValueError("DIP bit must be 0 or 1")


def decode_dip_pair(pair: str) -> str:
    """Decode OHM protocol pair to DIP bit."""
    if pair == "01":
        return "0"
    if pair == "00":
        return "1"
    raise ValueError(f"invalid OHM DIP pair: {pair}")


def build_frame_bits(channel_bits: str, tone_bits: str) -> str:
    """Build OHM 07 frame bits."""
    if len(channel_bits) != 6 or any(c not in "01" for c in channel_bits):
        raise ValueError("channel must be a 6-bit binary string")

    if len(tone_bits) != 3 or any(c not in "01" for c in tone_bits):
        raise ValueError("tone must be a 3-bit binary string")

    ch_bits = "".join(encode_dip_bit(b) for b in channel_bits)
    tone_bits_encoded = "".join(encode_dip_bit(b) for b in tone_bits)

    frame = ch_bits + "1111" + tone_bits_encoded + "00"

    if len(frame) != 24:
        raise ValueError("internal frame length error")

    return frame


def encode_bits(bits: str) -> bytes:
    """Encode OHM 07 bits to Broadlink pulse bytes."""
    out = bytearray()

    for bit in bits:
        if bit == "0":
            out.extend(PULSE_0)
        elif bit == "1":
            out.extend(PULSE_1)
        else:
            raise ValueError("bits must contain only 0 or 1")

    return bytes(out)


def build_ohm_frame(channel_bits: str, tone_bits: str) -> bytes:
    """Build one OHM 07 RF frame."""
    bits = build_frame_bits(channel_bits, tone_bits)
    frame = encode_bits(bits) + OHM_SYNC

    if len(frame) != 50:
        raise ValueError("OHM frame length mismatch")

    return frame


def build_packet(channel_bits: str, tone_bits: str) -> bytes:
    """Build Broadlink packet for OHM 07."""
    frame = build_ohm_frame(channel_bits, tone_bits)

    packet = bytearray()
    packet.extend(bytes.fromhex(HEADER_HEX))
    packet.extend(frame[-DEFAULT_LEADING_LEN:])

    for _ in range(DEFAULT_REPEAT):
        packet.extend(frame)

    packet.extend(bytes.fromhex(SUFFIX_HEX))

    return bytes(packet)


def generate_base64(channel_bits: str, tone_bits: str) -> str:
    """Generate Base64 code for OHM 07 protocol."""
    payload = build_packet(channel_bits, tone_bits)
    return base64.b64encode(payload).decode()


def decode_received(bits: str, raw_hex: str | None = None) -> dict[str, Any] | None:
    """Decode received OHM 07 raw bits."""
    if len(bits) != 24:
        return None

    if bits[12:16] != "1111":
        return None

    if bits[22:24] != "00":
        return None

    channel_pairs = [
        bits[0:2],
        bits[2:4],
        bits[4:6],
        bits[6:8],
        bits[8:10],
        bits[10:12],
    ]

    tone_pairs = [
        bits[16:18],
        bits[18:20],
        bits[20:22],
    ]

    try:
        channel = "".join(decode_dip_pair(pair) for pair in channel_pairs)
        melody = "".join(decode_dip_pair(pair) for pair in tone_pairs)
    except ValueError:
        return None

    return {
        "protocol": "ohm_07",
        "manufacturer": "ohm",
        "series": "07",
        "channel": channel,
        "melody": melody,
    }