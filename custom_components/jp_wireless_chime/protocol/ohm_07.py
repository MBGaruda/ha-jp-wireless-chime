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
    channel: str,
    tone: str,
) -> str:
    if len(channel) != 6:
        raise ValueError("channel must be 6 bits")

    if len(tone) != 3:
        raise ValueError("tone must be 3 bits")

    ch_bits = "".join(
        encode_dip_bit(b)
        for b in channel
    )

    tone_bits = "".join(
        encode_dip_bit(b)
        for b in tone
    )

    return ch_bits + "1111" + tone_bits + "00"


def build_payload(
    channel: str,
    tone: str,
) -> bytes:
    frame = build_frame(channel, tone)

    packet = bytearray()

    packet += HEADER

    for bit in frame:
        packet += PULSE_0 if bit == "0" else PULSE_1

    packet += SYNC
    packet += PADDING

    return bytes(packet)


def generate_base64(
    channel: str,
    tone: str,
) -> str:
    payload = build_payload(channel, tone)

    return base64.b64encode(payload).decode()
