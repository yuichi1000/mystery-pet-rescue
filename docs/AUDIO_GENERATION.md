# 音声生成システム

Beatoven.ai APIを使用してゲーム用のBGMと効果音を生成するシステムです。

## セットアップ

### 1. Beatoven.ai APIキーの取得

1. [Beatoven.ai](https://beatoven.ai/) にアカウント登録
2. ダッシュボード → API Settings → Generate API Key
3. APIキーをコピー

### 2. 環境変数の設定

プロジェクトルートに `.env` ファイルを作成：

```bash
# 実際のAPIを使用する場合
BEATOVEN_API_KEY=your_api_key_here
USE_MOCK_API=False

# テスト用モックAPIを使用する場合
USE_MOCK_API=True
```

## 使用方法

### 全音声の一括生成

```bash
python scripts/generate_audio.py all
```

### 個別BGM生成

```bash
# 住宅街の平和なBGM（60秒）
python scripts/generate_audio.py bgm residential peaceful --duration 60

# パズル用の集中BGM（30秒）
python scripts/generate_audio.py bgm puzzle focused --duration 30
```

### 個別効果音生成

```bash
# ペット発見音（中程度の強度、1.5秒）
python scripts/generate_audio.py sfx pet_found --intensity medium --duration 1.5

# ボタンクリック音（弱い強度、0.3秒）
python scripts/generate_audio.py sfx button_click --intensity soft --duration 0.3
```

### キャッシュ管理

```bash
# キャッシュ情報表示
python scripts/generate_audio.py cache-info

# キャッシュクリア
python scripts/generate_audio.py clear-cache
```

### セットアップガイド表示

```bash
python scripts/generate_audio.py setup
```

## 生成される音声ファイル

### BGM（assets/music/）
- `menu_bgm.mp3` - メニュー画面
- `residential_bgm.mp3` - 住宅街エリア
- `forest_bgm.mp3` - 森エリア
- `puzzle_bgm.mp3` - パズル中
- `victory_bgm.mp3` - 勝利時
- `game_over_bgm.mp3` - ゲームオーバー

### 効果音（assets/sounds/）
- `pet_found.wav` - ペット発見時
- `pet_rescued.wav` - ペット救出成功時
- `button_click.wav` - ボタンクリック
- `footstep.wav` - 足音
- `notification.wav` - 通知音
- `error.wav` - エラー音
- `puzzle_solve.wav` - パズル解決時

## パラメータ詳細

### BGM生成パラメータ

- **scene_type**: シーンタイプ
  - `menu`, `residential`, `forest`, `puzzle`, `victory`, `game_over`
- **mood**: 雰囲気
  - `calm`, `peaceful`, `mysterious`, `focused`, `triumphant`, `dramatic`
- **duration**: 長さ（秒）
  - デフォルト: 60秒

### 効果音生成パラメータ

- **effect_type**: 効果音タイプ
  - `pet_found`, `pet_rescued`, `button_click`, `footstep`, `notification`, `error`, `puzzle_solve`
- **intensity**: 強度
  - `soft`, `medium`, `strong`
- **duration**: 長さ（秒）
  - デフォルト: 2.0秒

## モックAPI（テスト用）

APIキーがない場合や開発時のテストには、モックAPIを使用できます：

```bash
# .env ファイル
USE_MOCK_API=True
```

モックAPIは無音のテスト用ファイルを生成します。

## キャッシュシステム

- 生成された音声は `cache/audio/` にキャッシュされます
- 同じパラメータでの再生成時はキャッシュを使用
- キャッシュクリアで全削除可能

## トラブルシューティング

### APIキーエラー
```
❌ BEATOVEN_API_KEY が設定されていません
```
→ `.env` ファイルにAPIキーを設定してください

### 生成失敗
```
❌ 生成失敗
```
→ ネットワーク接続、APIキーの有効性、API制限を確認してください

### モックAPI使用時
```
🔧 モックAPIを使用します（テスト用無音ファイルを生成）
```
→ 正常です。テスト用の無音ファイルが生成されます

## 開発者向け

### 新しい音声タイプの追加

1. `src/utils/beatoven_generator.py` の設定を更新
2. `scripts/generate_audio.py` のコマンドライン引数を追加
3. `config/audio_config.json` に設定を追加

### カスタムパラメータ

```python
from src.utils.audio_generator import get_audio_generator

generator = get_audio_generator()
audio_data = generator.generate_bgm(
    scene_type="custom_scene",
    mood="epic",
    duration=90,
    style="orchestral",
    tempo="fast",
    instruments=["strings", "brass", "percussion"]
)
```
