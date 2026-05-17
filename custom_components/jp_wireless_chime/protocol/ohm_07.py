import base64

# Legacy short format (kept for reference)
HEADER_LEGACY = bytes.fromhex("78643200")
PULSE_0_LEGACY = bytes([0x08, 0x14])
PULSE_1_LEGACY = bytes([0x15, 0x07])
SYNC_LEGACY = bytes([0x08, 0x8A])
PADDING_LEGACY = bytes([0x00] * 6)

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


def encode_dip_bit(bit: str) -> str:
    if bit == "0":
        return "01"
    if bit == "1":
        return "00"
    raise ValueError("DIP bit must be 0 or 1")


def build_frame_bits(
    channel_bits: str,
    tone_bits: str,
) -> str:
    """Build OHM-07 frame bit string."""
    if len(channel_bits) != 6:
        raise ValueError("channel must be 6 bits")
    if len(tone_bits) != 3:
        raise ValueError("tone must be 3 bits")

    ch_bits = "".join(encode_dip_bit(b) for b in channel_bits)
    tone_bits_encoded = "".join(encode_dip_bit(b) for b in tone_bits)
    
    return ch_bits + "1111" + tone_bits_encoded + "00"


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


def build_packet(
    channel_bits: str,
    tone_bits: str,
) -> bytes:
    """Build OHM-07 packet in waveform format (RM4 Pro compatible)."""
    if len(channel_bits) != 6 or any(c not in "01" for c in channel_bits):
        raise ValueError("channel must be a 6-bit binary string")
    if len(tone_bits) != 3 or any(c not in "01" for c in tone_bits):
        raise ValueError("tone must be a 3-bit binary string")

    frame_bits = build_frame_bits(channel_bits, tone_bits)
    
    # Pad frame_bits to 34 bits
    target_bits = frame_bits.ljust(BITS_PER_FRAME, "0")

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
    channel_bits: str,
    tone_bits: str,
) -> str:
    """Generate Base64 code for OHM-07 protocol (RM4 Pro compatible waveform format).
    
    Args:
        channel_bits: 6-bit binary string for channel (e.g., "101101")
        tone_bits: 3-bit binary string for melody (e.g., "001")
    
    Returns:
        Base64 encoded packet
    
    Raises:
        ValueError: If channel or tone format is invalid
    """
    if not isinstance(channel_bits, str) or len(channel_bits) != 6 or any(c not in "01" for c in channel_bits):
        raise ValueError("channel must be a 6-bit binary string")

    if not isinstance(tone_bits, str) or len(tone_bits) != 3 or any(c not in "01" for c in tone_bits):
        raise ValueError("tone must be a 3-bit binary string")

    packet = build_packet(channel_bits, tone_bits)

    return base64.b64encode(packet).decode()
