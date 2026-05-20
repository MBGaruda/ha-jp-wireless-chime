# JP Wireless Chime

Home Assistant 用のカスタム統合。Broadlink RF デバイスを使用して日本の無線チャイムを制御します。

この統合は日本の無線ドアチャイム製品用の RF チャイム信号を生成・送信します。

---

## 対応プロトコル

現在対応しているプロトコル：

- REVEX X シリーズ
- REVEX XP シリーズ
- OHM 07 シリーズ

---

## 機能

- Broadlink 互換 Base64 RF コード生成
- Home Assistant の `remote.send_command` 経由でチャイム信号送信
- 複数プロトコル対応
- Home Assistant 自動化での使用を想定設計

---

## インストール

### 手動インストール

このリポジトリを Home Assistant の設定ディレクトリにコピーします：

```text
/config/custom_components/jp_wireless_chime/
```

その後、Home Assistant を再起動してください。

### HACS

HACS でこのリポジトリを登録し、ダウンロードしてください。

---

## 使い方

### 基本的な使用例

```yaml
action: jp_wireless_chime.send_chime
data:
  protocol: revex_xp
  channel: G13
  melody: jinglebell
  remote_entity_id: remote.rm4_pro
```

### パラメータ説明

- **protocol**: `revex_x` または `ohm_07`
- **channel**: 
  - REVEX X: `G13` のような形式（アルファベット A-P ＋ 数字 1-16）
  - OHM-07: 6 ビットチャンネル文字列、例 `101101`
- **melody**: 音色名または 3 ビット tone 文字列
  - REVEX X: 数字 1-16またはエイリアス
  - REVEX XP: 数字 1-64 またはエイリアス（1-64 のエイリアスをサポート）
  - OHM-07: 3 ビット二進数文字列またはエイリアス
- **remote_entity_id**: Broadlink リモートエンティティ ID

### 音色一覧

#### REVEX X（1-16）

1. `chime_pingpong` - ピンポン ピンポン（チャイム音）
2. `westminster_chime` - ウェストミンスターの鐘
3. `fur_elise` - エリーゼのために
4. `childhood_remembered` - チャイルドフッド リメンバード
5. `green_sleeves` - グリーンスリーブス（イングランド民謡）
6. `oh_susanna` - おおスザンナ
7. `busker` - バスカー
8. `music_box` - 愛のオルゴール
9. `home_sweet_home` - ホームスウィートホーム
10. `jingle_bell` - ジングルベル
11. `happy_birthday` - ハッピーバースディ
12. `bird` - 小鳥の鳴き声
13. `dog` - 犬の鳴き声
14. `buzzer` - ブザー音
15. `siren_1` - サイレン音1（30秒）
16. `siren_2` - サイレン音2（30秒）

#### REVEX XP（1-64）

1. `dingdong_a` - ピンポンA
2. `dingdong_g` - ピンポンG
3. `school_bell` - キンコンカンコン
4. `emergency_alert` - 緊急音
5. `train_door_close_a` - 電車のドアが閉まる音A
6. `fur_elise` - エリーゼのために
7. `jupiter` - 木星
8. `sakura` - さくら
9. `calling_female` - 呼んでいます【女性】
10. `visitor_female` - 来客です【女性】
11. `welcome` - いらっしゃいませ
12. `sensor_triggered` - センサーが反応しました
13. `intruder_alert` - 侵入者です
14. `dog_bark` - 犬
15. `alarm_a` - アラーム音A
16. `siren_c` - サイレン音C
17. `dingdong_b` - ピンポンB
18. `dingdong_c` - ピンポンC
19. `dingdong_d` - ピンポンD
20. `dingdong_e` - ピンポンE
21. `dingdong_f` - ピンポンF
22. `chime_announcement_a` - ピンポンパンポンA
23. `koto_melody` - 琴の音
24. `bell_chime` - 鐘の音
25. `chime_announcement_b` - ピンポンパンポンB
26. `train_door_close_b` - 電車のドアが閉まる音B
27. `chord_a` - 和音A
28. `chord_b` - 和音B
29. `chinese_melody` - 中国音
30. `waltz_of_flowers` - 花のワルツ
31. `blue_danube` - 青色の頭巾
32. `dance_of_sugar_plum_fairy` - 金平糖の精の踊り
33. `nutcracker_bird` - 小鳥（くるみ割り人形）
34. `coppelia_waltz` - ワルツ（コンペリア）
35. `gamelan` - ガムラン
36. `puppy_waltz` - 子犬のワルツ
37. `shenandoah_tune` - シェンタノーティナー
38. `liebestraum_no_3` - 愛の夢 第3番
39. `kitri` - キトリ
40. `twinkle_twinkle` - きらきら星
41. `furusato` - ふるさと
42. `silent_night` - きよしこの夜
43. `joy_to_the_world` - もろびとこぞりて
44. `happy_birthday` - ハッピーバースディ
45. `calling_male` - 呼んでいます【男性】
46. `please_come_here` - ちょっと来てください
47. `please_come_quickly` - すぐ来てください
48. `visitor_male` - 来客です【男性】
49. `entrance_call` - 支度で呼んでいます
50. `bath_call` - お風呂で呼んでいます
51. `toilet_call` - トイレで呼んでいます
52. `living_room_call` - リビングで呼んでいます
53. `door_opened` - ドアが開きました
54. `puppy` - 子犬
55. `cat_meow` - 猫
56. `kitten` - 子猫
57. `bird_chirping` - 鳥のさえずり
58. `seagull` - ウミネコ
59. `cricket` - スズムシ
60. `bella_ciao` - ベラ
61. `alarm_b` - アラーム音B
62. `alarm_c` - アラーム音C
63. `siren_a` - サイレン音A
64. `siren_b` - サイレン音B

#### OHM-07

1. `000` - テキサスの黄色いバラ
2. `001` - ウエストミンスター（チャイム音）
3. `010` - ケンタッキーの我が家
4. `011` - ウエストミンスター（電子音）
5. `100` - メヌエット
6. `101` - ピンポン（チャイム音）
7. `110` - ピンポンポン
8. `111` - ピンポン（連続2回）

### 自動化の例

```yaml
automation:
  - alias: "ドアチャイム"
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

## 開発状況

この統合は開発中です。

最初のマイルストーンはサービスベースの送信です。

---

## 免責事項

このプロジェクトは REVEX、OHM、Broadlink、Home Assistant とは何ら関係はありません。

