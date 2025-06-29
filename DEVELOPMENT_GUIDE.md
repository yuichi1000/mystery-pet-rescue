# Mystery Pet Rescue - 開発ガイド

## 🚨 緊急修正事項

### 多言語対応バグ修正（高優先度）

**問題**: ゲームクリア画面で英語モードでも日本語テキストが表示される

**修正箇所**:
1. **src/scenes/result.py 329-333行**: 操作説明が日本語固定
   ```python
   # 現在（問題）
   help_texts = [
       "←→/AD: 選択移動",
       "ENTER/SPACE: 決定", 
       "R: もう一度, ESC: メニュー, Q: 終了"
   ]
   
   # 修正後
   help_texts = [
       get_text("controls_select"),
       get_text("controls_confirm"),
       get_text("controls_restart_menu_quit")
   ]
   ```

2. **src/scenes/result.py 295行**: 感嘆符が日本語固定
   ```python
   # 現在（問題）
   congrats_text = get_text("congratulations") + "！" + get_text("all_pets_rescued")
   
   # 修正後
   congrats_text = get_text("congratulations") + get_text("exclamation") + get_text("all_pets_rescued")
   ```

3. **src/scenes/game.py**: ゲーム中の表示も多言語対応
   ```python
   # 行953: ゲームクリア表示
   clear_text = font_large.render(get_text("game_clear"), True, (255, 215, 0))
   
   # 行904: ポーズ表示
   pause_text = font.render(get_text("paused"), True, (255, 255, 255))
   
   # 行910: ポーズ時操作説明
   help_text = help_font.render(get_text("pause_instructions"), True, (200, 200, 200))
   ```

4. **src/utils/language_manager.py**: 不足している翻訳キーを追加
   ```python
   # 英語に追加
   "controls_select": "←→/AD: Move Selection",
   "controls_confirm": "ENTER/SPACE: Confirm", 
   "controls_restart_menu_quit": "R: Restart, ESC: Menu, Q: Quit",
   "exclamation": "! ",
   "game_clear": "Game Clear!",
   "paused": "PAUSED",
   "pause_instructions": "P: Resume, ESC: Return to Menu",
   
   # 日本語に追加
   "controls_select": "←→/AD: 選択移動",
   "controls_confirm": "ENTER/SPACE: 決定",
   "controls_restart_menu_quit": "R: もう一度, ESC: メニュー, Q: 終了", 
   "exclamation": "！",
   "game_clear": "ゲームクリア！",
   "paused": "一時停止",
   "pause_instructions": "P: 再開, ESC: メニューに戻る",
   ```

**修正完了後の効果**: 英語モードで完全に英語表示、日本語モードで完全に日本語表示が実現されます。

## 🎯 プロジェクト概要

住宅街で迷子になったペットを5分以内に救出するアドベンチャーゲーム

### ゲーム仕様
- **ゲーム時間**: 5分制限
- **ペット数**: 4種類（犬・猫・うさぎ・鳥）
- **勝利条件**: 全ペット救出
- **難易度**: 時間経過でヒント表示
- **マップ**: リアル都市マップ（建物配置・地形）

## 🏗️ アーキテクチャ

### システム構成

```
Core Systems:
├── GameMain            # メインゲームループ・エントリーポイント
├── GameFlow            # ゲーム進行制御
├── SceneManager        # シーン管理システム
├── AnimationSystem     # アニメーション制御
├── TimerSystem         # 時間制限・ヒント管理
├── MapSystem           # マップ・衝突判定・建物システム
├── AudioSystem         # 音響管理・動的音楽生成
└── UI System           # ゲームUI・メニューシステム

Game Objects:
├── Player              # プレイヤーキャラクター（4方向移動）
├── Pet                 # ペットAI（4種類、状態管理）
└── Building            # 建物インタラクション

Utilities:
├── AssetManager        # リソース管理・最適化
├── LanguageManager     # 多言語対応（日英）
├── SaveLoadSystem      # 暗号化セーブ/ロード
├── PerformanceOptimizer # パフォーマンス最適化
├── DrawOptimizer       # 描画最適化
└── ErrorHandler        # エラーハンドリング
```

## 📁 プロジェクト構造

```
mystery-pet-rescue/
├── main.py                      # ゲーム起動ポイント
├── .env                         # 環境変数（API設定）
├── requirements.txt             # Python依存関係
├── src/
│   ├── core/
│   │   ├── game_main.py        # メインゲームエンジン
│   │   ├── game.py             # ゲームロジック
│   │   ├── scene.py            # シーン基底クラス
│   │   ├── animation.py        # アニメーションシステム
│   │   ├── menu_system.py      # メニューシステム
│   │   └── game_flow.py        # ゲーム進行制御
│   ├── scenes/
│   │   ├── menu.py             # メニューシーン
│   │   ├── game.py             # ゲームシーン
│   │   └── result.py           # 結果画面
│   ├── entities/
│   │   ├── player.py           # プレイヤー（4方向移動）
│   │   └── pet.py              # ペット（4種類AI）
│   ├── systems/
│   │   ├── timer_system.py     # 時間制限システム
│   │   ├── map_system.py       # マップシステム（衝突判定）
│   │   ├── building_system.py  # 建物インタラクション
│   │   ├── audio_system.py     # 音響システム（動的生成）
│   │   ├── save_load_system.py # 暗号化セーブ/ロード
│   │   ├── map_data_loader.py  # マップデータローダー
│   │   └── pet_data_loader.py  # ペットデータベース
│   ├── ui/
│   │   └── game_ui.py          # ゲームUI（ミニマップ等）
│   └── utils/
│       ├── asset_manager.py    # アセット管理・最適化
│       ├── font_manager.py     # フォント管理
│       ├── language_manager.py # 多言語対応（日英IME対応）
│       ├── error_handler.py    # エラーハンドリング
│       ├── performance_optimizer.py # パフォーマンス最適化
│       ├── draw_optimizer.py   # 描画最適化
│       ├── audio_generator.py  # 音響生成（Beatoven.ai）
│       └── beatoven_audio_generator.py # AI音楽生成
├── assets/
│   ├── images/
│   │   ├── characters/         # プレイヤースプライト（4方向）
│   │   ├── pets/              # ペットスプライト（8種×4方向）
│   │   ├── buildings/         # 建物画像（住宅・店舗）
│   │   ├── tiles/             # タイル画像（11種類）
│   │   └── ui/                # UI画像・アイコン
│   ├── audio/
│   │   ├── bgm/               # BGM（メニュー・ゲーム・勝利）
│   │   └── sounds/            # 効果音
│   └── fonts/                 # フォント（日本語対応）
├── config/
│   ├── constants.py           # ゲーム定数
│   ├── game_settings.json     # ゲーム設定
│   └── audio_config.json      # 音響設定
├── data/
│   ├── pets_database.json     # ペットデータベース（4種類＋拡張用）
│   └── maps/
│       └── realistic_city_v1.json # 都市マップデータ
├── scripts/
│   └── generate_real_audio.py # 音楽生成スクリプト
├── tests/                     # テストファイル
└── docs/                      # ドキュメント
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
  - 暗号化保存（セキュリティ強化）
  - 自動バックアップ
  - エラーハンドリング
  - 完全性チェック

### ✅ UIシステム
- **実装ファイル**: `src/ui/game_ui.py`
- **機能**:
  - 通知システム（多種類のタイプ）
  - ミニマップ（プレイヤー・オブジェクト・建物表示）
  - タイマー表示（残り時間・警告色）
  - 救出ペット表示（4種類対応）
  - 多言語対応UI（日本語IME対応）
  - メニューシステム（設定・言語切替）

## 🎨 アセット仕様

### 画像アセット
- **プレイヤー**: 4方向スプライト（front, back, left, right）
- **ペット**: 4種類×4方向スプライト（計16アニメーション）
- **建物**: 住宅、ペットショップ、公園施設等
- **タイル**: 64×64ピクセル、11種類（道路、草地、水等）
- **UI**: 高品質PNGアイコン、インターフェース要素
- **サイズ**: 64×64ピクセル基準、高解像度対応

### 音響アセット
- **BGM**: メニュー、ゲーム、勝利、敗北（AI生成対応）
- **効果音**: ペット救出、足音、環境音、UI操作音
- **形式**: MP3、OGG、WAV対応
- **動的生成**: Beatoven.ai API統合

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
- **Python**: 3.8以上（3.13.3推奨）
- **Pygame**: 2.0以上
- **画面解像度**: 1280×720（HD、スケーリング対応）
- **フレームレート**: 60FPS（パフォーマンス最適化済み）
- **タイルサイズ**: 64×64ピクセル
- **多言語**: 日本語・英語完全対応

### 主要依存関係
```
pygame>=2.0.0          # ゲームエンジン
requests>=2.25.0       # HTTP通信（API）
python-dotenv>=0.19.0  # 環境変数管理
cryptography>=3.4.0    # 暗号化（セーブデータ）
```

## 🎯 ゲーム仕様詳細

### プレイヤーシステム
- **移動**: WASD/矢印キー
- **相互作用**: Eキーでペット救出
- **衝突判定**: 矩形ベース、足元重視
- **カメラ**: プレイヤー中心追従、境界制限

### ペットAI
- **行動状態**: IDLE、WANDERING、SCARED、FOLLOWING、RESCUED
- **移動パターン**: ランダム歩行、境界制限、建物回避
- **4種類のペット**: 各々固有の行動パターン（犬・猫・うさぎ・鳥）
- **発見難易度**: 段階的難易度設定
- **建物インタラクション**: 建物内外の移動

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

### 音楽生成（AI）
```bash
python scripts/generate_real_audio.py
```

### テスト実行
```bash
python -m pytest tests/
```

### 設定ファイル
- `config/game_settings.json`: ゲーム設定
- `config/audio_config.json`: 音響設定
- `.env`: API設定（Beatoven.ai等）

## 📊 パフォーマンス最適化

### 実装済み最適化
- **マップ事前描画**: 全体を`map_surface`に描画、部分切り取り表示
- **スプライトキャッシュ**: 画像の事前読み込み・再利用
- **音響チャンネル管理**: 重複音再生防止
- **UI階層化**: 固定UI・動的UI分離
- **描画最適化**: ダーティレクト検出・領域更新
- **メモリ管理**: アセットプーリング・ガベージコレクション

### モニタリング・デバッグ
- **FPS表示**: デバッグモード時
- **衝突判定可視化**: F6キーで切り替え
- **位置情報出力**: F5キーでコンソール出力
- **エラーハンドリング**: 包括的例外処理・ログ出力

## 🎉 実装状況

### ✅ 完全実装
- ゲームコアループ・エンジン
- 全システム統合（タイマー・マップ・音響・UI）
- 多言語対応（日本語IME対応含む）
- 暗号化セーブ/ロードシステム
- ゲームUI/UX（ミニマップ・通知システム）
- 音響システム（AI生成対応）
- 4種類のペットAIシステム
- 建物インタラクションシステム
- パフォーマンス最適化
- エラーハンドリングシステム

### 🚧 部分実装
- **AI音楽生成**: Beatoven.ai API統合済み、手動実行が必要

## 📝 技術的特徴

### アーキテクチャ
- **Pygame 2Dエンジン**: 高パフォーマンスゲームループ
- **タイルベースマップ**: 効率的なメモリ使用と描画
- **コンポーネント指向設計**: 保守性・拡張性の高いコード
- **多言語アーキテクチャ**: ロケール対応システム
- **外部API統合**: Beatoven.aiでのAI音楽生成
- **暗号化セキュリティ**: セーブデータ保護

### パフォーマンス最適化
- **描画最適化**: ダーティレクト・領域更新最適化
- **メモリ管理**: アセットプーリング・キャッシュシステム
- **リアルタイム処理**: 60FPS安定動作

このプロジェクトは本格的な2Dアドベンチャーゲームとして、Pythonゲーム開発のベストプラクティスを実装しています。