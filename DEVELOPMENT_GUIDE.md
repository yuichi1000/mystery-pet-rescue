# Mystery Pet Rescue - 開発ガイド

## 🎯 プロジェクト概要

住宅街で迷子になったペットを5分以内に救出するアドベンチャーゲーム

### ゲーム仕様
- **ゲーム時間**: 5分制限
- **ペット数**: 4種類（犬・猫・うさぎ・鳥）
- **勝利条件**: 全ペット救出
- **難易度**: 時間経過でヒント表示

## 🏗️ アーキテクチャ

### システム構成

```
Core Systems:
├── GameScene          # メインゲームループ
├── TimerSystem         # 時間制限・ヒント管理
├── MapSystem           # マップ・衝突判定
├── AudioSystem         # 音響管理
└── UI System           # ユーザーインターフェース

Game Objects:
├── Player              # プレイヤーキャラクター
├── Pet                 # ペットAI
└── Camera              # カメラシステム

Utilities:
├── AssetManager        # リソース管理
├── LanguageManager     # 多言語対応
└── SaveLoadSystem      # セーブ/ロード
```

## 📁 プロジェクト構造

```
mystery-pet-rescue/
├── main.py                      # ゲーム起動ポイント
├── .env                         # 環境変数（API設定）
├── requirements.txt             # Python依存関係
├── src/
│   ├── core/
│   │   ├── __init__.py
│   │   ├── scene.py            # シーン基底クラス
│   │   ├── game.py             # メインゲームクラス
│   │   └── menu_system.py      # メニューシステム
│   ├── scenes/
│   │   ├── __init__.py
│   │   ├── game.py             # ゲームシーン
│   │   ├── menu.py             # メニューシーン
│   │   └── result.py           # 結果画面
│   ├── entities/
│   │   ├── __init__.py
│   │   ├── player.py           # プレイヤー
│   │   └── pet.py              # ペット
│   ├── systems/
│   │   ├── __init__.py
│   │   ├── timer_system.py     # 時間制限システム
│   │   ├── map_system.py       # マップシステム
│   │   ├── building_system.py  # 建物システム
│   │   ├── audio_system.py     # 音響システム
│   │   ├── save_load_system.py # セーブ/ロード
│   │   ├── map_data_loader.py  # マップデータ
│   │   └── pet_data_loader.py  # ペットデータ
│   ├── ui/
│   │   ├── __init__.py
│   │   └── game_ui.py          # ゲームUI
│   └── utils/
│       ├── __init__.py
│       ├── asset_manager.py    # アセット管理
│       ├── font_manager.py     # フォント管理
│       ├── language_manager.py # 多言語対応
│       ├── audio_generator.py  # 音響生成
│       └── error_handler.py    # エラーハンドリング
├── assets/
│   ├── images/
│   │   ├── characters/         # プレイヤースプライト
│   │   ├── pets/              # ペットスプライト
│   │   ├── tiles/             # タイル画像
│   │   ├── buildings/         # 建物画像
│   │   ├── backgrounds/       # 背景画像
│   │   └── ui/                # UI画像
│   ├── sounds/                # 効果音
│   └── music/                 # BGM
└── data/
    └── maps/                  # マップファイル
```

## 🎮 実装済みシステム

### ✅ 時間制限システム
- **実装ファイル**: `src/systems/timer_system.py`
- **機能**:
  - 5分の制限時間管理
  - 段階的ヒント表示（2分、3分、4分経過時）
  - 30秒以下で警告表示
  - タイムボーナス計算（残り秒数×10点）
  - 一時停止/再開機能

### ✅ 多言語対応システム
- **実装ファイル**: `src/utils/language_manager.py`
- **対応言語**: 日本語、英語
- **機能**:
  - UI要素の翻訳
  - ペット名の言語別表示
  - 動的言語切り替え

### ✅ マップシステム
- **実装ファイル**: `src/systems/map_system.py`
- **機能**:
  - タイルベースマップ（64×64ピクセル）
  - 7種類のタイル対応
  - カメラ追従システム
  - 衝突判定（建物・障害物）
  - 建物システム統合

### ✅ 音響システム
- **実装ファイル**: `src/systems/audio_system.py`
- **機能**:
  - BGM管理（再生、停止、フェード）
  - 効果音再生（重複防止）
  - 音量設定（マスター、BGM、効果音別）
  - 16チャンネル管理
  - 対応形式: MP3、OGG、WAV

### ✅ セーブ/ロードシステム
- **実装ファイル**: `src/systems/save_load_system.py`
- **機能**:
  - 3スロットセーブ
  - オートセーブ機能
  - JSON形式での保存
  - 自動バックアップ
  - エラーハンドリング

### ✅ UIシステム
- **実装ファイル**: `src/ui/game_ui.py`
- **機能**:
  - 通知システム（5種類のタイプ）
  - ミニマップ（プレイヤー・オブジェクト表示）
  - タイマー表示（残り時間・警告色）
  - 救出ペット表示（クイックスロット形式）
  - 多言語対応UI

## 🎨 アセット仕様

### 画像アセット
- **プレイヤー**: 4方向スプライト（front, back, left, right）
- **ペット**: 各種4方向スプライト
- **タイル**: 64×64ピクセル、11種類
- **UI**: アイコン、背景画像
- **サイズ**: 各スプライト64×64ピクセル基準

### 音響アセット
- **BGM**: 住宅街、勝利、メニュー
- **効果音**: ペット救出、ヒント、警告、ゲームオーバー
- **形式**: MP3、OGG、WAV対応

## 🔧 開発設定

### 環境変数（.env）
```
# Beatoven.ai API設定
BEATOVEN_API_KEY=your_api_key
BEATOVEN_API_URL=https://public-api.beatoven.ai/api/v1
BEATOVEN_TIMEOUT=60

# デバッグ設定
DEBUG_MODE=False
USE_MOCK_API=False

# ゲーム設定
AUDIO_CACHE_ENABLED=True
AUDIO_CACHE_DIR=cache/audio

# ログレベル
LOG_LEVEL=INFO
```

### 技術仕様
- **Python**: 3.8以上
- **Pygame**: 2.0以上
- **画面解像度**: 1280×720（HD）
- **フレームレート**: 60FPS
- **タイルサイズ**: 64×64ピクセル

### 依存関係
```
pygame>=2.0.0
requests>=2.25.0
python-dotenv>=0.19.0
cryptography>=3.4.0
```

## 🎯 ゲーム仕様詳細

### プレイヤーシステム
- **移動**: WASD/矢印キー
- **相互作用**: Eキーでペット救出
- **衝突判定**: 矩形ベース、足元重視
- **カメラ**: プレイヤー中心追従、境界制限

### ペットAI
- **行動状態**: IDLE、WANDERING、SCARED、FOLLOWING、RESCUED
- **移動パターン**: ランダム歩行、境界制限
- **発見難易度**: 犬（易）→ 猫 → うさぎ → 鳥（難）

### タイマー・ヒントシステム
- **2分経過**: 「ペットの鳴き声が聞こえます」
- **3分経過**: 「足跡を発見しました」
- **4分経過**: 「ペットが近くにいます」
- **30秒以下**: 赤色警告表示

## 🚀 ビルド・デプロイ

### 開発実行
```bash
python main.py
```

### 音楽生成
```bash
python generate_real_audio.py
```

### テスト実行
```bash
python -m pytest tests/
```

## 📊 パフォーマンス最適化

### 実装済み最適化
- **マップ事前描画**: 全体を`map_surface`に描画、部分切り取り表示
- **スプライトキャッシュ**: 画像の事前読み込み・再利用
- **音響チャンネル管理**: 重複音再生防止
- **UI階層化**: 固定UI・動的UI分離

### モニタリング
- **FPS表示**: デバッグモード時
- **衝突判定可視化**: F6キーで切り替え
- **位置情報出力**: F5キーでコンソール出力

## 🎉 完成状況

### ✅ 実装完了
- ゲームコアループ
- 全システム統合
- 多言語対応
- セーブ/ロード
- UI/UX
- 音響システム基盤

### 🚧 部分実装
- **音源ファイル**: 生成可能、手動実行が必要

### ❌ 未実装
- 設定画面UI（システムは実装済み）

## 📝 開発メモ

### 開発効率
- **総開発時間**: 約17時間
- **コミット数**: 91回
- **開発期間**: 6日間（実質4日）

### 技術的特徴
- Pygame 2Dエンジン使用
- タイルベースマップシステム
- コンポーネント指向設計
- 多言語対応アーキテクチャ
- 外部API統合（Beatoven.ai）

このプロジェクトは短期間で完成した本格的な2Dアドベンチャーゲームとして、Pythonゲーム開発のベストプラクティスを実装しています。