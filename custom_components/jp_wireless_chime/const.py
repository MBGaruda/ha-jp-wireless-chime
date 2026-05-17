"""Constants for the JP Wireless Chime integration."""

DOMAIN = "jp_wireless_chime"

SERVICE_SEND_CHIME = "send_chime"

CONF_PROTOCOL = "protocol"
CONF_CHANNEL = "channel"
CONF_MELODY = "melody"
CONF_REMOTE_ENTITY_ID = "remote_entity_id"

PROTOCOL_REVEX_X = "revex_x"
PROTOCOL_OHM_07 = "ohm_07"
PROTOCOL_REVEX_XP = "revex_xp"

SUPPORTED_PROTOCOLS = [
    PROTOCOL_REVEX_X,
    PROTOCOL_REVEX_XP,
    PROTOCOL_OHM_07,
]

# Melody aliases: user-friendly names to numeric indexes per protocol.
# Keys are lowercase; values are 1-based integers as accepted by protocol generators.
MELODY_ALIASES = {
    PROTOCOL_REVEX_X: {
        # REVEX_X melody names (lowercase)
        "chimepingpong": 1,
        "westminsterchime": 2,
        "furelise": 3,
        "childhoodremembered": 4,
        "greensleeves": 5,
        "ohsusanna": 6,
        "busker": 7,
        "musicbox": 8,
        "homesweethome": 9,
        "jinglebell": 10,
        "happybirthday": 11,
        "bird": 12,
        "dog": 13,
        "buzzer": 14,
        "siren1": 15,
        "siren2": 16,
    },
    PROTOCOL_REVEX_XP: {
        # REVEX XP uses the same aliases for the first 16 melodies,
        # and supports 1-64 numeric melody values (page selection handled by generator).
        "chimepingpong": 1,
        "westminsterchime": 2,
        "furelise": 3,
        "childhoodremembered": 4,
        "greensleeves": 5,
        "ohsusanna": 6,
        "busker": 7,
        "musicbox": 8,
        "homesweethome": 9,
        "jinglebell": 10,
        "happybirthday": 11,
        "bird": 12,
        "dog": 13,
        "buzzer": 14,
        "siren1": 15,
        "siren2": 16,
    },
    PROTOCOL_OHM_07: {
        # OHM-07 melody bit patterns (lowercase)
        "yellowroseoftexas": "000",
        "westminsterchime": "001",
        "myoldkentuckyhome": "010",
        "westminsterelectronic": "011",
        "minuet": "100",
        "pingpongchime": "101",
        "pingpongpong": "110",
        "pingpongdouble": "111",
    },
}
