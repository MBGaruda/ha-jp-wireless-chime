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
  channel: 1
  melody: 1
  remote_entity_id: remote.rm4_pro
```

---

## Development Status

This integration is currently under development.

The first milestone is service-based transmission.

UI entities such as selectors and buttons will be added later.

---

## Disclaimer

This project is not affiliated with REVEX, OHM, Broadlink, or Home Assistant.
