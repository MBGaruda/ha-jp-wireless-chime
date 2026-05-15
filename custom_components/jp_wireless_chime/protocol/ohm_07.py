import base64

HEADER = bytes.fromhex("78643200")

PULSE_0 = bytes([0x08, 0x14])
PULSE_1 = bytes([0x15, 0x07])

SYNC = bytes([0x08, 0x8A])

PADDING = bytes([0x00] * 6)


def encode_dip_bit(bit: str) -> str:
    if bit == "0":
        return "01"

    if bit == "1":
        return "00"

    raise ValueError("DIP bit must be 0 or 1")


def build_frame(
    channel_bits: str,
    tone_bits: str,
) -> str:
    if len(channel_bits) != 6:
        raise ValueError("channel must be 6 bits")

    if len(tone_bits) != 3:
        raise ValueError("tone must be 3 bits")

    ch_bits = "".join(
        encode_dip_bit(b)
        for b in channel_bits
    )

    tone_bits_encoded = "".join(
        encode_dip_bit(b)
        for b in tone_bits
    )

    return ch_bits + "1111" + tone_bits_encoded + "00"


def build_payload(
    channel_bits: str,
    tone_bits: str,
) -> bytes:
    frame = build_frame(channel_bits, tone_bits)

    packet = bytearray()

    packet += HEADER

    for bit in frame:
        packet += PULSE_0 if bit == "0" else PULSE_1

    packet += SYNC
    packet += PADDING

    return bytes(packet)


def generate_base64(
    channel: int,
    tone: int,
) -> str:
    if not (1 <= channel <= 64):
        raise ValueError("channel must be between 1 and 64")

    if not (1 <= tone <= 8):
        raise ValueError("tone must be between 1 and 8")

    # Convert channel and tone directly to 6-bit and 3-bit binary DIP patterns
    channel_bits = format(channel, "06b")
    tone_bits = format(tone, "03b")

    payload = build_payload(channel_bits, tone_bits)

    return base64.b64encode(payload).decode()
