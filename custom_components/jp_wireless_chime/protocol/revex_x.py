import base64

ID_CODE = {
    1: "D5",
    2: "75",
    3: "F5",
    4: "77",
    5: "F7",
    6: "57",
    7: "D7",
    8: "5D",
    9: "DD",
    10: "7D",
    11: "FD",
    12: "7F",
    13: "FF",
    14: "5F",
    15: "DF",
    16: "55",
}

GROUP_TO_INDEX = {
    "A": 1, "B": 2, "C": 3, "D": 4,
    "E": 5, "F": 6, "G": 7, "H": 8,
    "I": 9, "J": 10, "K": 11, "L": 12,
    "M": 13, "N": 14, "O": 15, "P": 16,
}

MELODY_CODE = {
    1: "55",
    2: "00",
    3: "40",
    4: "10",
    5: "50",
    6: "04",
    7: "44",
    8: "14",
    9: "54",
    10: "01",
    11: "41",
    12: "11",
    13: "51",
    14: "05",
    15: "45",
    16: "15",
}

# Waveform-based constants (RM4 Pro compatible format)
HEADER_HEX = "78068403"
SUFFIX_HEX = "05dc00000000"

FRAME_SYNCS = [0x95, 0x95, 0x95, 0x94, 0x96, 0x96, 0x95, 0x95, 0x95, 0x96, 0x94, 0x95]
FRAME_GAPS = [0x0A, 0x0A, 0x0A, 0x0A, 0x0A, 0x0B, 0x0B, 0x0A, 0x0A, 0x0A, 0x0A, None]

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
    group = group.upper()

    if group not in GROUP_TO_INDEX:
        raise ValueError("group must be A-P")

    if number not in ID_CODE:
        raise ValueError("number must be 1-16")

    if melody not in MELODY_CODE:
        raise ValueError("melody must be 1-16")

    revex_hex = (
        ID_CODE[GROUP_TO_INDEX[group]]
        + ID_CODE[number]
        + MELODY_CODE[melody]
    )

    # revex_x generates 26 bits (24 + "00"), pad to 34 bits
    target_bits = hex_to_bits(revex_hex) + "00" + "00000000"

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


def generate_base64(
    channel: str,
    melody: int,
) -> str:
    """Generate Base64 code from channel and melody (RM4 Pro compatible waveform format).
    
    Args:
        channel: Channel in format like "G13" (letter A-P + number 1-16)
        melody: Melody number (1-16)
    
    Returns:
        Base64 encoded packet
    
    Raises:
        ValueError: If channel format is invalid or values are out of range
    """
    if not isinstance(channel, str) or len(channel) < 2:
        raise ValueError("channel must be in format like 'G13' (letter + number)")
    
    group = channel[0].upper()
    try:
        number = int(channel[1:])
    except ValueError:
        raise ValueError("channel must be in format like 'G13' (letter + number)")
    
    if melody not in MELODY_CODE:
        raise ValueError("melody must be 1-16")

    if group not in GROUP_TO_INDEX:
        raise ValueError("group must be A-P")

    if number not in ID_CODE:
        raise ValueError("number must be 1-16")

    packet = build_packet(group, number, melody)

    return base64.b64encode(packet).decode()
