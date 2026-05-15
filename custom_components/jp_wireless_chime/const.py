"""Constants for the JP Wireless Chime integration."""

DOMAIN = "jp_wireless_chime"

SERVICE_SEND_CHIME = "send_chime"

CONF_PROTOCOL = "protocol"
CONF_CHANNEL = "channel"
CONF_MELODY = "melody"
CONF_REMOTE_ENTITY_ID = "remote_entity_id"

PROTOCOL_REVEX_X = "revex_x"
PROTOCOL_OHM_07 = "ohm_07"

SUPPORTED_PROTOCOLS = [
    PROTOCOL_REVEX_X,
    PROTOCOL_OHM_07,
]
