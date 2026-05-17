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
  - REVEX XP: 数字 1-64 またはエイリアス（1-16 のエイリアスが利用可能）
  - OHM-07: 3 ビット二進数文字列またはエイリアス
- **remote_entity_id**: Broadlink リモートエンティティ ID

### 音色一覧

#### REVEX X（1-16）

1. `chimepingpong` - ピンポン ピンポン（チャイム音）
2. `westminsterchime` - ウェストミンスターの鐘
3. `furelise` - エリーゼのために
4. `childhoodremembered` - チャイルドフッド リメンバード
5. `greensleeves` - グリーンスリーブス（イングランド民譜）
6. `ohsusanna` - おおスザンナ
7. `busker` - バスカー
8. `musicbox` - 愛のオルゴール
9. `homesweethome` - ホームスウィートホーム
10. `jinglebell` - ジングルベル
11. `happybirthday` - ハッピーバースディ
12. `bird` - 小鳥の鳴き声
13. `dog` - 犬の鳴き声
14. `buzzer` - ブザー音
15. `siren1` - サイレン音1（30秒）
16. `siren2` - サイレン音2（30秒）

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

