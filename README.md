# JP Wireless Chime

Home Assistant custom integration for Japanese wireless chimes using Broadlink RF devices.

This integration generates and sends RF chime signals for Japanese wireless door chime products.

---

## Supported Protocols

Initial supported protocols:

- REVEX X series
- OHM 07 series

Additional Japanese wireless chime protocols may be added in the future.

---

## Features

- Generate Broadlink-compatible Base64 RF codes
- Send chime signals via Home Assistant `remote.send_command`
- Support multiple chime protocols
- Designed for Home Assistant automation use

---

## Installation

### Manual Installation

Copy this repository into your Home Assistant configuration directory:

```text
/config/custom_components/jp_wireless_chime/
```

Then restart Home Assistant.

### HACS

HACS support is planned.

---

## Usage

Initial development target:

```yaml
action: jp_wireless_chime.send_chime
data:
  protocol: revex_x
  channel: G13
  melody: jinglebell
  remote_entity_id: remote.rm4_pro
```

### Parameters

- **protocol**: `revex_x` or `ohm_07`
- **channel**: 
  - REVEX X: Format like `G13` (letter A-P + number 1-16)
  - OHM-07: Numeric channel (1-64)
- **melody**: Melody name or number
  - REVEX X: See list below
  - OHM-07: See list below
- **remote_entity_id**: Broadlink remote entity ID

### Melody List

#### REVEX X (1-16)

1. `chimepingpong` - Ping-Pong Ping-Pong (Chime)
2. `westminsterchime` - Westminster Chime
3. `furelise` - Für Elise
4. `childhoodremembered` - Childhood Remembered
5. `greensleeves` - Greensleeves (English folk song)
6. `ohsusanna` - Oh Susanna
7. `busker` - Busker
8. `musicbox` - Music Box
9. `homesweethome` - Home Sweet Home
10. `jinglebell` - Jingle Bell
11. `happybirthday` - Happy Birthday
12. `bird` - Bird Song
13. `dog` - Dog Barking
14. `buzzer` - Buzzer Sound
15. `siren1` - Siren 1 (30 sec)
16. `siren2` - Siren 2 (30 sec)

#### OHM-07 (1-8)

1. `yellowroseoftexas` - Yellow Rose of Texas
2. `westminsterchime` - Westminster (Chime sound)
3. `myoldkentuckyhome` - My Old Kentucky Home
4. `westminsterelectronic` - Westminster (Electronic)
5. `minuet` - Minuet
6. `pingpongchime` - Ping-Pong (Chime)
7. `pingpongpong` - Ping-Pong-Pong
8. `pingpongdouble` - Ping-Pong (Double)

---

## Development Status

This integration is currently under development.

The first milestone is service-based transmission.

UI entities such as selectors and buttons will be added later.

---

## Disclaimer

This project is not affiliated with REVEX, OHM, Broadlink, or Home Assistant.
