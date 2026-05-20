# JP Wireless Chime

A custom Home Assistant integration for Japanese 315MHz wireless chimes using Broadlink RM4 Pro / ESPHome.

This integration provides the following features:

- Wireless chime transmission using Broadlink
- Wireless chime receive events using ESPHome RF receivers

Currently supported series:

- REVEX X Series
- REVEX XP Series
- OHM 07 Series (wireless chime series with model numbers starting with 07)

Related repositories:

- ha-jp-wireless-chime  
  https://github.com/MBGaruda/ha-jp-wireless-chime

- esphome-jp-wireless-chime  
  https://github.com/MBGaruda/esphome-jp-wireless-chime

---

# Main Features

## Transmission Function

Creates Button Entities in Home Assistant and transmits 315MHz RF signals using Broadlink RM4 Pro.

The following parameters can be configured:

- Protocol
- Channel
- Melody
- Broadlink Remote Entity

Transmit buttons are created as Home Assistant Button Entities.

---

## Receive Function

315MHz RF signals received by ESPHome are exposed as Home Assistant Event Entities.

Matching conditions:

- protocol
- channel
- melody
- receiver

Wildcard (`*`) is supported.

Example:

```text
protocol = revex_x
channel = G15
melody = *
receiver = *
```

This matches:

- REVEX X
- G15
- Any melody
- Any receiver

and fires the event.

---

## Cooldown Function

A cooldown period can be configured for each receive entity.

This prevents:

- Repeated button presses
- Duplicate reception from multiple ESPHome receivers
- Double reception caused by RF reflections

Example:

```text
cooldown = 2
```

Ignores repeated reception within 2 seconds.

---

## Self-Transmission Ignore Function

RF signals transmitted by this integration can be ignored by its own receive entities.

This prevents loops such as:

```text
Transmit
↓
ESPHome receives signal
↓
Automation triggered
↓
Retransmit
```

---

# System Architecture

## Receive Side

```text
Physical Chime Transmitter
↓
ESPHome RF Receiver
↓
esphome.jp_wireless_chime_raw_received
↓
JP Wireless Chime
↓
jp_wireless_chime.received
↓
Event Entity
↓
Automation
```

## Transmit Side

```text
Button Entity
↓
JP Wireless Chime
↓
Broadlink RM4 Pro
↓
315MHz RF Transmission
↓
Physical Receiver
```

---

# Requirements

## Home Assistant

Tested with:

- Home Assistant 2026.x

---

## Broadlink

The transmit function requires:

- Broadlink RM4 Pro

Broadlink Integration must already be configured.

---

## ESPHome Receiver

The receive function requires:

- ESP32
- 315MHz RF receiver module
- esphome-jp-wireless-chime

ESPHome must fire the following event:

```text
esphome.jp_wireless_chime_raw_received
```

Example event:

```yaml
event_type: esphome.jp_wireless_chime_raw_received

data:
  protocol_hint: revex_x
  bits: "110101111111111100000001"
  raw_hex: D7FF01
  source: living_room_receiver
```

---

# Installation

## HACS

### Add Custom Repository

HACS → Integrations → ︙ → Custom repositories

Repository:

```text
https://github.com/MBGaruda/ha-jp-wireless-chime
```

Category:

```text
Integration
```

Then install:

```text
JP Wireless Chime
```

Restart Home Assistant after installation.

---

## Manual Installation

Place `custom_components/jp_wireless_chime` into:

```text
config/custom_components/jp_wireless_chime
```

Then restart Home Assistant.

---

# Initial Setup

## Add Integration

Settings → Devices & Services → Add Integration

Select:

```text
JP Wireless Chime
```

---

# Add Receive Button

Options →

```text
Add receive button
```

---

## Configuration Items

| Item | Description |
|---|---|
| Name | Display name |
| Protocol | Protocol |
| Channel | Channel |
| Melody | Melody |
| Receiver | ESPHome receiver name |
| Cooldown | Cooldown seconds |

---

## Wildcards

The following values are treated as wildcards:

```text
*
empty
```

Example:

```text
Melody = *
```

Matches any melody.

---

# Add Send Button

Options →

```text
Add send button
```

---

## Configuration Items

| Item | Description |
|---|---|
| Name | Display name |
| Protocol | Protocol |
| Channel | Channel |
| Melody | Melody |
| Broadlink remote entity | Broadlink Remote Entity |

---

# Automation Examples

## Using Event Entity as Trigger

```yaml
alias: Front Door Chime

triggers:
  - trigger: state_changed
    entity_id: event.front_door_button

conditions: []

actions:
  - action: light.turn_on
    target:
      entity_id: light.living_room
```

---

## Using jp_wireless_chime.received Directly

```yaml
alias: REVEX G15

triggers:
  - trigger: event
    event_type: jp_wireless_chime.received
    event_data:
      protocol: revex_x
      channel: G15
      melody: 1

conditions: []

actions:
  - action: notify.mobile_app
    data:
      message: "Chime received"
```

---

# Event Entity Attributes

Receive entities include the following attributes:

| Attribute | Description |
|---|---|
| protocol | Protocol |
| channel | Channel |
| melody | Melody |
| receiver | Receiver name |
| cooldown | Cooldown |
| match_rule | Match condition |
| direction | receive |

---

# Button Entity Attributes

Send entities include the following attributes:

| Attribute | Description |
|---|---|
| protocol | Protocol |
| channel | Channel |
| melody | Melody |
| remote_entity_id | Broadlink Entity |
| send_rule | Send condition |
| direction | send |

---

# REVEX X Melody List

| No. | Alias | English Name |
|---|---|---|
|1|chime_pingpong|Ping Pong Ping Pong (Chime)|
|2|westminster_chime|Westminster Chime|
|3|fur_elise|Für Elise|
|4|childhood_remembered|Childhood Remembered|
|5|green_sleeves|Greensleeves (English folk tune)|
|6|oh_susanna|Oh Susanna|
|7|busker|Busker|
|8|music_box|Love's Music Box|
|9|home_sweet_home|Home Sweet Home|
|10|jingle_bell|Jingle Bell|
|11|happy_birthday|Happy Birthday|
|12|bird|Bird Song|
|13|dog|Dog Barking|
|14|buzzer|Buzzer|
|15|siren_1|Siren 1 (30 seconds)|
|16|siren_2|Siren 2 (30 seconds)|

---

# REVEX XP Melody List

| No. | Alias | English Name |
|---|---|---|
|1|dingdong_a|DingDongA|
|2|dingdong_g|DingDongG|
|3|school_bell|SchoolBell|
|4|emergency_alert|EmergencyAlert|
|5|train_door_close_a|TrainDoorCloseA|
|6|fur_elise|FurElise|
|7|jupiter|Jupiter|
|8|sakura|Sakura|
|9|calling_female|CallingFemale|
|10|visitor_female|VisitorFemale|
|11|welcome|Welcome|
|12|sensor_triggered|SensorTriggered|
|13|intruder_alert|IntruderAlert|
|14|dog_bark|DogBark|
|15|alarm_a|AlarmA|
|16|siren_c|SirenC|
|17|dingdong_b|DingDongB|
|18|dingdong_c|DingDongC|
|19|dingdong_d|DingDongD|
|20|dingdong_e|DingDongE|
|21|dingdong_f|DingDongF|
|22|chime_announcement_a|ChimeAnnouncementA|
|23|koto_melody|KotoMelody|
|24|bell_chime|BellChime|
|25|chime_announcement_b|ChimeAnnouncementB|
|26|train_door_close_b|TrainDoorCloseB|
|27|chord_a|ChordA|
|28|chord_b|ChordB|
|29|chinese_melody|ChineseMelody|
|30|waltz_of_flowers|WaltzOfFlowers|
|31|blue_danube|BlueDanube|
|32|dance_of_sugar_plum_fairy|DanceOfSugarPlumFairy|
|33|nutcracker_bird|NutcrackerBird|
|34|coppelia_waltz|CoppeliaWaltz|
|35|gamelan|Gamelan|
|36|puppy_waltz|PuppyWaltz|
|37|shenandoah_tune|ShenandoahTune|
|38|liebestraum_no_3|LiebestraumNo3|
|39|kitri|Kitri|
|40|twinkle_twinkle|TwinkleTwinkle|
|41|furusato|Furusato|
|42|silent_night|SilentNight|
|43|joy_to_the_world|JoyToTheWorld|
|44|happy_birthday|HappyBirthday|
|45|calling_male|CallingMale|
|46|please_come_here|PleaseComeHere|
|47|please_come_quickly|PleaseComeQuickly|
|48|visitor_male|VisitorMale|
|49|entrance_call|EntranceCall|
|50|bath_call|BathCall|
|51|toilet_call|ToiletCall|
|52|living_room_call|LivingRoomCall|
|53|door_opened|DoorOpened|
|54|puppy|Puppy|
|55|cat_meow|CatMeow|
|56|kitten|Kitten|
|57|bird_chirping|BirdChirping|
|58|seagull|Seagull|
|59|cricket|Cricket|
|60|bella_ciao|BellaCiao|
|61|alarm_b|AlarmB|
|62|alarm_c|AlarmC|
|63|siren_a|SirenA|
|64|siren_b|SirenB|

---

# OHM 07 Melody List

| No. | Alias | English Name |
|---|---|---|
|1|000|Yellow Rose of Texas|
|2|001|Westminster (Chime)|
|3|010|Home Sweet Home|
|4|011|Westminster (Electronic)|
|5|100|Minuet|
|6|101|Ping Pong (Chime)|
|7|110|Ping Pong Pong|
|8|111|Ping Pong (2x)|

---

# Notes

## Broadlink Learning Codes Are Not Used

This integration does not use Broadlink learning codes.

RF waveforms are generated dynamically based on protocol analysis.

Therefore:

- No Broadlink learning required
- RM4 initialization only
- Can operate without original transmitters

---

## ESPHome Receiver

ESPHome receiver support is provided by a separate repository:

```text
esphome-jp-wireless-chime
```

---

# Known Limitations

- RF interference may cause false receptions depending on the environment

---

# License

MIT License