"""Constants for the JP Wireless Chime integration."""

DOMAIN = "jp_wireless_chime"

SERVICE_SEND_CHIME = "send_chime"

CONF_PROTOCOL = "protocol"
CONF_CHANNEL = "channel"
CONF_MELODY = "melody"
CONF_REMOTE_ENTITY_ID = "remote_entity_id"
CONF_NAME = "name"
CONF_BUTTONS = "buttons"
CONF_BUTTON_ID = "id"
CONF_RECEIVER_ID = "receiver_id"

MATCH_ANY = "*"

PROTOCOL_REVEX_X = "revex_x"
PROTOCOL_OHM_07 = "ohm_07"
PROTOCOL_REVEX_XP = "revex_xp"

SUPPORTED_PROTOCOLS = [
    PROTOCOL_REVEX_X,
    PROTOCOL_REVEX_XP,
    PROTOCOL_OHM_07,
]

EVENT_ESPHOME_RAW_RECEIVED = "esphome.jp_wireless_chime_raw_received"
EVENT_CHIME_RECEIVED = "jp_wireless_chime.received"

EVENT_TYPE_PRESSED = "pressed"

DATA_RECEIVER_SETUP_DONE = "receiver_setup_done"
DATA_RECEIVER_UNSUB = "receiver_unsub"
DATA_SERVICES_SETUP_DONE = "services_setup_done"
DATA_EVENT_ENTITIES = "event_entities"

MELODY_ALIASES = {
    PROTOCOL_REVEX_X: {
        "chime_pingpong": 1,
        "westminster_chime": 2,
        "fur_elise": 3,
        "childhood_remembered": 4,
        "green_sleeves": 5,
        "oh_susanna": 6,
        "busker": 7,
        "music_box": 8,
        "home_sweet_home": 9,
        "jingle_bell": 10,
        "happy_birthday": 11,
        "bird": 12,
        "dog": 13,
        "buzzer": 14,
        "siren_1": 15,
        "siren_2": 16,
    },
    PROTOCOL_REVEX_XP: {
        "dingdong_a": 1,
        "dingdong_g": 2,
        "school_bell": 3,
        "emergency_alert": 4,
        "train_door_close_a": 5,
        "fur_elise": 6,
        "jupiter": 7,
        "sakura": 8,
        "calling_female": 9,
        "visitor_female": 10,
        "welcome": 11,
        "sensor_triggered": 12,
        "intruder_alert": 13,
        "dog_bark": 14,
        "alarm_a": 15,
        "siren_c": 16,
        "dingdong_b": 17,
        "dingdong_c": 18,
        "dingdong_d": 19,
        "dingdong_e": 20,
        "dingdong_f": 21,
        "chime_announcement_a": 22,
        "koto_melody": 23,
        "bell_chime": 24,
        "chime_announcement_b": 25,
        "train_door_close_b": 26,
        "chord_a": 27,
        "chord_b": 28,
        "chinese_melody": 29,
        "waltz_of_flowers": 30,
        "blue_danube": 31,
        "dance_of_sugar_plum_fairy": 32,
        "nutcracker_bird": 33,
        "coppelia_waltz": 34,
        "gamelan": 35,
        "puppy_waltz": 36,
        "shenandoah_tune": 37,
        "liebestraum_no_3": 38,
        "kitri": 39,
        "twinkle_twinkle": 40,
        "furusato": 41,
        "silent_night": 42,
        "joy_to_the_world": 43,
        "happy_birthday": 44,
        "calling_male": 45,
        "please_come_here": 46,
        "please_come_quickly": 47,
        "visitor_male": 48,
        "entrance_call": 49,
        "bath_call": 50,
        "toilet_call": 51,
        "living_room_call": 52,
        "door_opened": 53,
        "puppy": 54,
        "cat_meow": 55,
        "kitten": 56,
        "bird_chirping": 57,
        "seagull": 58,
        "cricket": 59,
        "bella_ciao": 60,
        "alarm_b": 61,
        "alarm_c": 62,
        "siren_a": 63,
        "siren_b": 64,
    },
    PROTOCOL_OHM_07: {
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