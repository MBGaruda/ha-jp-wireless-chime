import base64

HEADER_HEX = "78068403"
SUFFIX_HEX = "05dc00000000"

PULSE_0 = bytes([0x08, 0x14])
PULSE_1 = bytes([0x15, 0x07])
OHM_SYNC = bytes([0x08, 0x8A])

DEFAULT_LEADING_LEN = 44
DEFAULT_REPEAT = 23


def encode_dip_bit(bit: str) -> str:
    if bit == "0":
        return "01"
    if bit == "1":
        return "00"
    raise ValueError("DIP bit must be 0 or 1")


def build_frame_bits(channel_bits: str, tone_bits: str) -> str:
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
    bits = build_frame_bits(channel_bits, tone_bits)
    frame = encode_bits(bits) + OHM_SYNC

    if len(frame) != 50:
        raise ValueError("OHM frame length mismatch")

    return frame


def build_packet(channel_bits: str, tone_bits: str) -> bytes:
    frame = build_ohm_frame(channel_bits, tone_bits)

    packet = bytearray()
    packet.extend(bytes.fromhex(HEADER_HEX))
    packet.extend(frame[-DEFAULT_LEADING_LEN:])
    for _ in range(DEFAULT_REPEAT):
        packet.extend(frame)
    packet.extend(bytes.fromhex(SUFFIX_HEX))

    return bytes(packet)


def generate_base64(channel_bits: str, tone_bits: str) -> str:
    payload = build_packet(channel_bits, tone_bits)
    return base64.b64encode(payload).decode()
