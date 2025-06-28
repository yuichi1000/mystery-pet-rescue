# スプライト画像作成指示書

## 📋 概要
ミステリー・ペット・レスキューゲーム用の画像アセット作成指示です。
ChatGPTのDALL-E 3を使用して、統一感のある可愛らしいピクセルアート風の画像を作成してください。

## 🎨 全体的なアートスタイル
- **スタイル**: 16-bit ピクセルアート風、可愛らしいアニメ調
- **色調**: 明るく温かみのある色合い、子供向けゲームらしい親しみやすさ
- **解像度**: 256x256ピクセル（高解像度で作成後、ゲーム内で自動リサイズ）
- **背景**: 透明背景（PNG形式）
- **対象年齢**: 10-14歳向けの健全で可愛らしいデザイン

---

## 🐾 ペット画像（不足分）

### うさぎ（Rabbit）
**ファイル名**: `pet_rabbit_001_[direction].png`
**配置場所**: `assets/images/pets/`
**必要な向き**: front, back, left, right

**作成指示**:
```
Create a cute 16-bit pixel art style white rabbit character for a children's pet rescue game. The rabbit should be:
- Fluffy white fur with pink inner ears
- Large expressive eyes
- Small pink nose
- Sitting/standing pose suitable for [DIRECTION] view
- Friendly and approachable appearance
- 256x256 pixels with transparent background
- Suitable for ages 10-14

Direction variations:
- front: facing forward, showing both ears and face
- back: showing back with ears visible from behind
- left: side profile facing left
- right: side profile facing right
```

### 鳥（Bird）
**ファイル名**: `pet_bird_001_[direction].png`
**配置場所**: `assets/images/pets/`
**必要な向き**: front, back, left, right

**作成指示**:
```
Create a cute 16-bit pixel art style colorful parrot/parakeet character for a children's pet rescue game. The bird should be:
- Bright colorful feathers (green, blue, yellow, red accents)
- Small curved beak
- Round friendly eyes
- Perched or standing pose suitable for [DIRECTION] view
- Cheerful and energetic appearance
- 256x256 pixels with transparent background
- Suitable for ages 10-14

Direction variations:
- front: facing forward, showing chest and face
- back: showing back and wing details
- left: side profile facing left, showing wing and tail
- right: side profile facing right, showing wing and tail
```

---

## 🏠 背景画像（不足分）

### ゲーム背景
**ファイル名**: `game_background.png`
**配置場所**: `assets/images/backgrounds/`

**作成指示**:
```
Create a 16-bit pixel art style residential neighborhood background for a pet rescue game. The scene should include:
- Suburban houses with gardens
- Tree-lined streets
- Sidewalks and pathways
- Warm, welcoming atmosphere
- Soft pastel colors suitable for children
- 1280x720 pixels resolution
- Areas where pets might hide (bushes, behind trees, etc.)
- Daytime lighting with gentle shadows
```

### 結果画面背景
**ファイル名**: `result_background.png`
**配置場所**: `assets/images/backgrounds/`

**作成指示**:
```
Create a celebratory 16-bit pixel art background for a game results screen. The image should feature:
- Starry night sky with gentle gradients
- Celebration elements (confetti, sparkles)
- Warm, congratulatory atmosphere
- Suitable for displaying text overlays
- 1280x720 pixels resolution
- Colors that work well with white text
- Child-friendly and uplifting mood
```

---

## 🎮 UI要素

### アイコン類
**ファイル名**: `[icon_name].png`
**配置場所**: `assets/images/ui/`

#### 必要なアイコン:

**ペット救出アイコン**
**ファイル名**: `pet_rescue_icon.png`
```
Create a 16-bit pixel art icon showing a heart with paw prints for a pet rescue game UI. The icon should be:
- 64x64 pixels with transparent background
- Bright, cheerful colors (pink/red heart, brown/orange paw prints)
- Clear and recognizable at small sizes
- Suitable for UI buttons and notifications
```

**時間アイコン**
**ファイル名**: `time_icon.png`
```
Create a 16-bit pixel art clock icon for a game UI. The icon should be:
- 64x64 pixels with transparent background
- Simple clock face with clear hands
- Bright, readable colors
- Suitable for displaying game time/timer
```

**スコアアイコン**
**ファイル名**: `score_icon.png`
```
Create a 16-bit pixel art star icon for a game score display. The icon should be:
- 64x64 pixels with transparent background
- Golden yellow star with sparkle effects
- Clear and eye-catching design
- Suitable for score/points display
```

**設定アイコン**
**ファイル名**: `settings_icon.png`
```
Create a 16-bit pixel art gear/cog icon for a game settings menu. The icon should be:
- 64x64 pixels with transparent background
- Metallic gray/silver color
- Clear mechanical gear design
- Suitable for settings/options button
```

**音量アイコン**
**ファイル名**: `volume_icon.png`
```
Create a 16-bit pixel art speaker icon for audio settings. The icon should be:
- 64x64 pixels with transparent background
- Speaker with sound waves
- Clear, simple design
- Suitable for volume controls
```

---

## 🏘️ 建物・環境要素

### 家屋
**ファイル名**: `house_[type].png`
**配置場所**: `assets/images/buildings/`

#### 必要な建物タイプ:

**一般住宅**
**ファイル名**: `house_residential.png`
```
Create a 16-bit pixel art suburban house for a pet rescue game map. The house should be:
- 128x128 pixels with transparent background
- Two-story family home with garden
- Warm, welcoming appearance
- Windows, door, and roof clearly defined
- Places where pets might hide (porch, garden)
- Child-friendly, non-threatening design
```

**ペットショップ**
**ファイル名**: `house_petshop.png`
```
Create a 16-bit pixel art pet shop building. The building should be:
- 128x128 pixels with transparent background
- Storefront with large windows
- Pet-themed signage or decorations
- Bright, inviting colors
- Clear entrance and display areas
```

**公園施設**
**ファイル名**: `park_facility.png`
```
Create a 16-bit pixel art park pavilion or playground structure. The structure should be:
- 128x128 pixels with transparent background
- Child-friendly playground equipment or gazebo
- Natural colors (wood, green)
- Safe, welcoming appearance
- Areas where pets might play or hide
```

---

## 🌳 追加タイル要素（不足分）

### 花・植物
**ファイル名**: `[plant_type]_tile.png`
**配置場所**: `assets/images/tiles/`

**花壇タイル**
**ファイル名**: `flower_bed_tile.png`
```
Create a 16-bit pixel art flower bed tile for a game map. The tile should be:
- 64x64 pixels with transparent background
- Colorful flowers in a garden bed
- Bright, cheerful colors
- Suitable for tiling/repeating
- Child-friendly garden design
```

**茂みタイル**
**ファイル名**: `bush_tile.png`
```
Create a 16-bit pixel art bush/shrub tile for a game map. The tile should be:
- 64x64 pixels with transparent background
- Dense green foliage
- Natural, organic shape
- Suitable for pets to hide behind
- Seamlessly tileable if needed
```

### 道路要素
**ファイル名**: `[road_type]_tile.png`
**配置場所**: `assets/images/tiles/`

**歩道タイル**
**ファイル名**: `sidewalk_tile.png`
```
Create a 16-bit pixel art sidewalk tile for a residential area. The tile should be:
- 64x64 pixels with transparent background
- Light gray concrete texture
- Subtle crack or texture details
- Suitable for character walking
- Seamlessly tileable
```

**道路タイル**
**ファイル名**: `road_tile.png`
```
Create a 16-bit pixel art road/street tile. The tile should be:
- 64x64 pixels with transparent background
- Dark asphalt texture
- Subtle road markings or texture
- Suitable for neighborhood streets
- Seamlessly tileable
```

---

## 📁 ディレクトリ構造

作成後の配置場所:
```
assets/images/
├── pets/
│   ├── pet_rabbit_001_front.png
│   ├── pet_rabbit_001_back.png
│   ├── pet_rabbit_001_left.png
│   ├── pet_rabbit_001_right.png
│   ├── pet_bird_001_front.png
│   ├── pet_bird_001_back.png
│   ├── pet_bird_001_left.png
│   └── pet_bird_001_right.png
├── backgrounds/
│   ├── game_background.png
│   └── result_background.png
├── ui/
│   ├── pet_rescue_icon.png
│   ├── time_icon.png
│   ├── score_icon.png
│   ├── settings_icon.png
│   └── volume_icon.png
├── buildings/
│   ├── house_residential.png
│   ├── house_petshop.png
│   └── park_facility.png
├── tiles/
│   ├── flower_bed_tile.png
│   ├── bush_tile.png
│   ├── sidewalk_tile.png
│   └── road_tile.png
└── effects/
    ├── sparkle_effect.png
    └── heart_effect.png
```

## 🎨 カラーパレット推奨

**メインカラー**:
- 草地: #7CB342 (明るい緑)
- 空: #42A5F5 (明るい青)
- 建物: #8D6E63 (温かい茶色)
- UI: #FFA726 (温かいオレンジ)

**アクセントカラー**:
- 成功: #66BB6A (明るい緑)
- 警告: #FFCA28 (黄色)
- エラー: #EF5350 (優しい赤)
- 情報: #42A5F5 (青)

## 📝 注意事項

1. **ファイル形式**: すべてPNG形式で透明背景
2. **命名規則**: 指定されたファイル名を厳密に守る
3. **サイズ**: 指定されたピクセルサイズを守る
4. **年齢適切性**: 10-14歳向けの健全なデザイン
5. **統一感**: 全体的なアートスタイルの一貫性を保つ
6. **可読性**: 小さいサイズでも認識できる明確なデザイン

## ✅ 既存アセット（作成不要）

以下のアセットは既に存在するため作成不要:
- プレイヤーキャラクター（4方向）
- 犬・猫のペット画像（4方向）
- 基本タイル（草、地面、コンクリート、岩、石壁、木、水）
- メニュー背景画像
- 一部の建物画像

---

**作成優先順位**:
1. 🐾 ペット画像（うさぎ・鳥）- ゲームプレイに必須
2. 🎮 UI要素 - ユーザビリティに重要
3. 🏠 建物・環境要素 - ゲーム世界の充実
4. 🎵 効果・装飾要素 - ゲーム体験の向上