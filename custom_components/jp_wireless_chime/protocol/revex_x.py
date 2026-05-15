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

HEADER = bytes.fromhex("78863200")
BIT_1 = bytes.fromhex("1f08")
BIT_0 = bytes.fromhex("0c19")
FOOTER = bytes.fromhex("0c95000000000000")


def hex_to_bits(hexstr: str) -> str:
    return "".join(
        f"{int(hexstr[i:i+2], 16):08b}"
        for i in range(0, len(hexstr), 2)
    )


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

    bits = hex_to_bits(revex_hex)

    body = b"".join(
        BIT_1 if bit == "1" else BIT_0
        for bit in bits
    )

    return HEADER + body + FOOTER


def generate_base64(
    group: str,
    number: int,
    melody: int,
) -> str:
    packet = build_packet(group, number, melody)

    return base64.b64encode(packet).decode()