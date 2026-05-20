# JP Wireless Chime

日本国内で広く流通している315MHzワイヤレスチャイムを、Home Assistant と Broadlink RM4 Pro / ESPHome を用いて統合するためのカスタムインテグレーションです。

本インテグレーションは以下の2つの機能を提供します。

- Broadlink を使用したワイヤレスチャイム送信
- ESPHome受信機と連携したチャイム受信イベント

現在、以下のシリーズに対応しています。

- REVEX Xシリーズ
- REVEX XPシリーズ
- OHM 07シリーズ(品番が07で始まるワイヤレスチャイムシリーズ)

---

# 主な機能

## 送信機能

Home Assistant 上にボタンEntityを作成し、Broadlink RM4 Pro を通じて315MHz RF信号を送信します。

以下の情報を指定可能です。

- プロトコル
- チャンネル
- 音色
- Broadlink Remote Entity

送信ボタンは Home Assistant の Button Entity として作成されます。

---

## 受信機能

ESPHome 側で受信した315MHz RF信号を、Home Assistant の Event Entity として扱います。

以下の条件でマッチ可能です。

- protocol
- channel
- melody
- receiver

ワイルドカード (`*`) に対応しています。

例:

```text
protocol = revex_x
channel = G15
melody = *
receiver = *
```

この場合:

- REVEX X
- G15
- 任意音色
- 任意受信機

でイベントが発火します。

---

## クールタイム機能

受信Entityごとにクールタイム秒数を設定可能です。

これは以下を防止するための機能です。

- 同一ボタン連打
- 複数ESPHome受信機による重複受信
- 電波反射による二重受信

例:

```text
cooldown = 2
```

2秒以内の再受信を無視します。

---

## 自己送信無視機能

本インテグレーションから送信したRF信号に、自分自身の受信Entityが反応しないようになっています。

以下のようなループを防止できます。

```text
送信
↓
ESPHome受信
↓
Automation発火
↓
再送信
```

---

# システム構成

## 受信側

```text
物理チャイム送信機
↓
ESPHome RF受信機
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

## 送信側

```text
Button Entity
↓
JP Wireless Chime
↓
Broadlink RM4 Pro / RM2 Pro
↓
315MHz RF送信
↓
物理受信機
```

---

# 必要環境

## Home Assistant

以下で動作確認済み:

- Home Assistant 2026.x

---

## Broadlink

送信機能には以下が必要です。

- Broadlink RM4 Pro

Broadlink Integration が設定済みである必要があります。

---

## ESPHome受信機

受信機能には以下が必要です。

- ESP32
- 315MHz RF受信モジュール
- esphome-jp-wireless-chime

ESPHome側で以下イベントを発火する必要があります。

```text
esphome.jp_wireless_chime_raw_received
```

イベント例:

```yaml
event_type: esphome.jp_wireless_chime_raw_received

data:
  protocol_hint: revex_x
  bits: "110101111111111100000001"
  raw_hex: D7FF01
  source: living_room_receiver
```

---

# インストール

## HACS

### カスタムリポジトリ追加

HACS → Integrations → ︙ → Custom repositories

Repository:

```text
https://github.com/MBGaruda/ha-jp-wireless-chime
```

Category:

```text
Integration
```

追加後:

```text
JP Wireless Chime
```

をインストールしてください。

Home Assistant を再起動後、インテグレーション追加から設定可能になります。

---

## 手動インストール

`custom_components/jp_wireless_chime` を以下へ配置:

```text
config/custom_components/jp_wireless_chime
```

その後 Home Assistant を再起動してください。

---

# 初期設定

## インテグレーション追加

設定 → デバイスとサービス → 統合を追加

```text
JP Wireless Chime
```

を選択します。

---

# 受信ボタン追加

Options →

```text
Add receive button
```

---

## 設定項目

|項目|説明|
|---|---|
|Name|表示名|
|Protocol|プロトコル|
|Channel|チャンネル|
|Melody|音色|
|Receiver|ESPHome受信機名|
|Cooldown|クールタイム秒数|

---

## ワイルドカード

以下はワイルドカードとして扱われます。

```text
*
空欄
```

例:

```text
Melody = *
```

任意音色に一致します。

---

# 送信ボタン追加

Options →

```text
Add send button
```

---

## 設定項目

|項目|説明|
|---|---|
|Name|表示名|
|Protocol|プロトコル|
|Channel|チャンネル|
|Melody|音色|
|Broadlink remote entity|Broadlink Remote Entity|

---

# オートメーション例

## Event Entity をトリガーに使用

```yaml
alias: 玄関チャイム

triggers:
  - trigger: state_changed
    entity_id: event.genkan_button

conditions: []

actions:
  - action: light.turn_on
    target:
      entity_id: light.living_room
```

---

## jp_wireless_chime.received を直接利用

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
      message: "チャイム受信"
```

---

# Event Entity属性

受信Entityには以下属性が付きます。

|属性|説明|
|---|---|
|protocol|プロトコル|
|channel|チャンネル|
|melody|音色|
|receiver|受信機名|
|cooldown|クールタイム|
|match_rule|一致条件|
|direction|receive|

---

# Button Entity属性

送信Entityには以下属性が付きます。

|属性|説明|
|---|---|
|protocol|プロトコル|
|channel|チャンネル|
|melody|音色|
|remote_entity_id|Broadlink Entity|
|send_rule|送信条件|
|direction|send|

---

# REVEX X 音色一覧

|番号|エイリアス名|日本語名|
|---|---|---|
|1|chime_pingpong|ピンポン チャイム|
|2|westminster_chime|ウェストミンスター|
|3|fur_elise|エリーゼのために|
|4|childhood_remembered|故郷の人々|
|5|green_sleeves|グリーンスリーブス|
|6|oh_susanna|オースザンナ|
|7|busker|大道芸人|
|8|music_box|オルゴール|
|9|home_sweet_home|埴生の宿|
|10|jingle_bell|ジングルベル|
|11|happy_birthday|ハッピーバースデー|
|12|bird|小鳥|
|13|dog|犬|
|14|buzzer|ブザー|
|15|siren_1|サイレン1|
|16|siren_2|サイレン2|

---

# REVEX XP 音色一覧

|番号|エイリアス名|日本語名|
|---|---|---|
|1|dingdong_a|ピンポン|
|2|dingdong_g|ピンポーン|
|3|school_bell|学校のチャイム|
|4|emergency_alert|非常ベル|
|5|train_door_close_a|電車のドア閉め|
|6|fur_elise|エリーゼのために|
|7|jupiter|ジュピター|
|8|sakura|さくら|
|9|calling_female|女性呼び出し|
|10|visitor_female|女性来客|
|11|welcome|いらっしゃいませ|
|12|sensor_triggered|センサー反応|
|13|intruder_alert|侵入警報|
|14|dog_bark|犬|
|15|alarm_a|アラーム1|
|16|siren_c|サイレン1|
|17|dingdong_b|ピンポン2|
|18|dingdong_c|ピンポン3|
|19|dingdong_d|ピンポン4|
|20|dingdong_e|ピンポン5|
|21|dingdong_f|ピンポン6|
|22|chime_announcement_a|チャイム案内1|
|23|koto_melody|琴|
|24|bell_chime|ベル|
|25|chime_announcement_b|チャイム案内2|
|26|train_door_close_b|電車のドア閉め2|
|27|chord_a|和音1|
|28|chord_b|和音2|
|29|chinese_melody|中国風|
|30|waltz_of_flowers|花のワルツ|
|31|blue_danube|美しき青きドナウ|
|32|dance_of_sugar_plum_fairy|こんぺいとうの踊り|
|33|nutcracker_bird|くるみ割り|
|34|coppelia_waltz|コッペリア|
|35|gamelan|ガムラン|
|36|puppy_waltz|子犬のワルツ|
|37|shenandoah_tune|シェナンドー|
|38|liebestraum_no_3|愛の夢|
|39|kitri|キトリ|
|40|twinkle_twinkle|きらきら星|
|41|furusato|ふるさと|
|42|silent_night|きよしこの夜|
|43|joy_to_the_world|もろびとこぞりて|
|44|happy_birthday|ハッピーバースデー|
|45|calling_male|男性呼び出し|
|46|please_come_here|こちらへどうぞ|
|47|please_come_quickly|至急お越しください|
|48|visitor_male|男性来客|
|49|entrance_call|玄関です|
|50|bath_call|お風呂です|
|51|toilet_call|トイレです|
|52|living_room_call|リビングです|
|53|door_opened|ドアが開きました|
|54|puppy|子犬|
|55|cat_meow|猫|
|56|kitten|子猫|
|57|bird_chirping|小鳥|
|58|seagull|カモメ|
|59|cricket|コオロギ|
|60|bella_ciao|ベラチャオ|
|61|alarm_b|アラーム2|
|62|alarm_c|アラーム3|
|63|siren_a|サイレン2|
|64|siren_b|サイレン3|

---

# OHM 07 音色一覧

|値|エイリアス名|日本語名|
|---|---|---|
|000|yellowroseoftexas|黄色いバラ|
|001|westminsterchime|ウェストミンスター|
|010|myoldkentuckyhome|ケンタッキーの我が家|
|011|westminsterelectronic|電子ウェストミンスター|
|100|minuet|メヌエット|
|101|pingpongchime|ピンポン|
|110|pingpongpong|ピンポンポン|
|111|pingpongdouble|ダブルチャイム|

---

# 注意事項

## Broadlink学習コード非互換

本インテグレーションは Broadlink の学習コードを利用していません。

プロトコル解析に基づいて RF波形を動的生成しています。

そのため:

- Broadlink学習不要
- RM4初期化のみで利用可能
- 送信機が無くても運用可能

---

## ESPHome受信機について

ESPHome側は別リポジトリです。

```text
esphome-jp-wireless-chime
```

---

# 既知の制限

- 315MHz RF環境によっては誤受信の可能性があります

---

# ライセンス

MIT License