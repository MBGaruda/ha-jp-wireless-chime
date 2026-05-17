# JP Wireless Chime

Home Assistant custom integration for controlling Japanese wireless chimes using Broadlink RF devices.

This integration generates and sends RF chime signals for Japanese wireless door chime products.

---

## Supported Protocols

Currently supported protocols:

- REVEX X series
- REVEX XP series
- OHM 07 series

---

## Features

- Generate Broadlink-compatible Base64 RF codes
- Send chime signals via Home Assistant `remote.send_command`
- Support multiple protocols
- Designed for use in Home Assistant automations

---

## Installation

### Manual Installation

Copy this repository to your Home Assistant configuration directory:

```text
/config/custom_components/jp_wireless_chime/
```

Then restart Home Assistant.

### HACS

Register this repository in HACS and download it.

---

## Usage

### Basic Example

```yaml
action: jp_wireless_chime.send_chime
data:
  protocol: revex_xp
  channel: G13
  melody: jinglebell
  remote_entity_id: remote.rm4_pro
```

### Parameters

- **protocol**: `revex_x` or `ohm_07`
- **channel**: 
  - REVEX X: Format like `G13` (letter A-P + digit 1-16)
  - OHM-07: 6-bit channel string, e.g., `101101`
- **melody**: Melody name or 3-bit tone string
  - REVEX X: Number 1-16 or alias
  - REVEX XP: Number 1-64 or alias (aliases 1-16 available)
  - OHM-07: 3-bit binary string or alias
- **remote_entity_id**: Broadlink remote entity ID

### Melodies

#### REVEX X (1-16)

1. `chimepingpong` - Ping Pong Ping Pong (Chime)
2. `westminsterchime` - Westminster Chime
3. `furelise` - Für Elise
4. `childhoodremembered` - Childhood Remembered
5. `greensleeves` - Greensleeves (English folk tune)
6. `ohsusanna` - Oh Susanna
7. `busker` - Busker
8. `musicbox` - Love's Music Box
9. `homesweethome` - Home Sweet Home
10. `jinglebell` - Jingle Bell
11. `happybirthday` - Happy Birthday
12. `bird` - Bird Song
13. `dog` - Dog Barking
14. `buzzer` - Buzzer
15. `siren1` - Siren 1 (30 seconds)
16. `siren2` - Siren 2 (30 seconds)

#### OHM-07

1. `000` - Yellow Rose of Texas
2. `001` - Westminster (Chime)
3. `010` - Home Sweet Home
4. `011` - Westminster (Electronic)
5. `100` - Minuet
6. `101` - Ping Pong (Chime)
7. `110` - Ping Pong Pong
8. `111` - Ping Pong (2x)

### Automation Example

```yaml
automation:
  - alias: "Door Chime"
    trigger:
      platform: state
      entity_id: binary_sensor.front_door
      to: 'on'
    action:
      service: jp_wireless_chime.send_chime
      data:
        protocol: ohm_07
        channel: "101101"
        melody: "001"
        remote_entity_id: remote.rm4_pro
```

---

## Development Status

This integration is currently under development.

The first milestone is service-based transmission.

---

## Disclaimer

This project is not affiliated with REVEX, OHM, Broadlink, or Home Assistant in any way.
