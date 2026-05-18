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
  - REVEX XP: Number 1-64 or alias (full alias list available)
  - OHM-07: 3-bit binary string or alias
- **remote_entity_id**: Broadlink remote entity ID

### Melodies

#### REVEX X (1-16)

1. `chime_pingpong` - Ping Pong Ping Pong (Chime)
2. `westminster_chime` - Westminster Chime
3. `fur_elise` - Für Elise
4. `childhood_remembered` - Childhood Remembered
5. `green_sleeves` - Greensleeves (English folk tune)
6. `oh_susanna` - Oh Susanna
7. `busker` - Busker
8. `music_box` - Love's Music Box
9. `home_sweet_home` - Home Sweet Home
10. `jingle_bell` - Jingle Bell
11. `happy_birthday` - Happy Birthday
12. `bird` - Bird Song
13. `dog` - Dog Barking
14. `buzzer` - Buzzer
15. `siren_1` - Siren 1 (30 seconds)
16. `siren_2` - Siren 2 (30 seconds)

#### REVEX XP (1-64)

1. `dingdong_a` - DingDongA
2. `dingdong_g` - DingDongG
3. `school_bell` - SchoolBell
4. `emergency_alert` - EmergencyAlert
5. `train_door_close_a` - TrainDoorCloseA
6. `fur_elise` - FurElise
7. `jupiter` - Jupiter
8. `sakura` - Sakura
9. `calling_female` - CallingFemale
10. `visitor_female` - VisitorFemale
11. `welcome` - Welcome
12. `sensor_triggered` - SensorTriggered
13. `intruder_alert` - IntruderAlert
14. `dog_bark` - DogBark
15. `alarm_a` - AlarmA
16. `siren_c` - SirenC
17. `dingdong_b` - DingDongB
18. `dingdong_c` - DingDongC
19. `dingdong_d` - DingDongD
20. `dingdong_e` - DingDongE
21. `dingdong_f` - DingDongF
22. `chime_announcement_a` - ChimeAnnouncementA
23. `koto_melody` - KotoMelody
24. `bell_chime` - BellChime
25. `chime_announcement_b` - ChimeAnnouncementB
26. `train_door_close_b` - TrainDoorCloseB
27. `chord_a` - ChordA
28. `chord_b` - ChordB
29. `chinese_melody` - ChineseMelody
30. `waltz_of_flowers` - WaltzOfFlowers
31. `blue_danube` - BlueDanube
32. `dance_of_sugar_plum_fairy` - DanceOfSugarPlumFairy
33. `nutcracker_bird` - NutcrackerBird
34. `coppelia_waltz` - CoppeliaWaltz
35. `gamelan` - Gamelan
36. `puppy_waltz` - PuppyWaltz
37. `shenandoah_tune` - ShenandoahTune
38. `liebestraum_no_3` - LiebestraumNo3
39. `kitri` - Kitri
40. `twinkle_twinkle` - TwinkleTwinkle
41. `furusato` - Furusato
42. `silent_night` - SilentNight
43. `joy_to_the_world` - JoyToTheWorld
44. `happy_birthday` - HappyBirthday
45. `calling_male` - CallingMale
46. `please_come_here` - PleaseComeHere
47. `please_come_quickly` - PleaseComeQuickly
48. `visitor_male` - VisitorMale
49. `entrance_call` - EntranceCall
50. `bath_call` - BathCall
51. `toilet_call` - ToiletCall
52. `living_room_call` - LivingRoomCall
53. `door_opened` - DoorOpened
54. `puppy` - Puppy
55. `cat_meow` - CatMeow
56. `kitten` - Kitten
57. `bird_chirping` - BirdChirping
58. `seagull` - Seagull
59. `cricket` - Cricket
60. `bella_ciao` - BellaCiao
61. `alarm_b` - AlarmB
62. `alarm_c` - AlarmC
63. `siren_a` - SirenA
64. `siren_b` - SirenB

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
