"""REVEX XP protocol implementation.

This module implements Base64 packet generation for REVEX XP series
using the validated logic from `revex_xp_gen.py`.
"""
import base64

from .revex_x import ID_CODE, GROUP_TO_INDEX, MELODY_CODE

HEADER_HEX = "78068403"
SUFFIX_HEX = "05dc00000000"

FRAME_SYNCS = [0x95, 0x95, 0x95, 0x94, 0x96, 0x96, 0x95, 0x95, 0x95, 0x96, 0x94, 0x95]
FRAME_GAPS = [0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0B, 0x0B, 0x0A, 0x0A, 0x0A, 0x0A, None]

# XP学習波形から見た代表値
BIT_1 = (0x1E, 0x09)  # long, short
BIT_0 = (0x0A, 0x1D)  # short, long

BITS_PER_FRAME = 34
PULSES_PER_FRAME = 68
LEADING_LEN = 59
EXPECTED_PACKET_BYTES = 908


def hex_to_bits(hexstr: str) -> str:
    return "".join(
        f"{int(hexstr[i:i+2], 16):08b}"
        for i in range(0, len(hexstr), 2)
    )


def xp_ext_code(melody: int) -> str:
    if melody <= 17:
        return "00"
    if melody <= 33:
        return "40"
    if melody <= 49:
        return "10"
    return "50"


def build_xp_hex(group: str, number: int, melody: int) -> str:
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

    Channel format: letter A-P plus number 1-16 (e.g. 'G13')
    Melody: 1-64
    """
    if not isinstance(channel, str) or len(channel) < 2:
        raise ValueError("channel must be in format like 'G13' (letter + number)")

    group = channel[0].upper()
    try:
        number = int(channel[1:])
    except ValueError:
        raise ValueError("channel must be in format like 'G13' (letter + number)")

    if group not in GROUP_TO_INDEX:
        raise ValueError("group must be A-P")

    if number not in ID_CODE:
        raise ValueError("number must be 1-16")

    if not (1 <= melody <= 64):
        raise ValueError("melody must be 1-64")

    packet = build_packet(group, number, melody)

    return base64.b64encode(packet).decode()
