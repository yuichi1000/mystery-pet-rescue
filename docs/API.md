# ミステリー・ペット・レスキュー API ドキュメント

## 概要

このドキュメントは、ミステリー・ペット・レスキューゲームの主要クラスとメソッドのAPIリファレンスです。

## コアクラス

### GameSettings

ゲームの設定を管理するクラス。

#### メソッド

- `__init__()`: 設定を初期化
- `load_from_file(config_file: Path)`: 設定ファイルから読み込み
- `save_to_file(config_file: Path)`: 設定をファイルに保存
- `validate_settings()`: 設定値の妥当性をチェック

#### プロパティ

- `screen_width: int`: 画面幅
- `screen_height: int`: 画面高さ
- `fps: int`: フレームレート
- `language: str`: 言語設定

### GameLoop

メインゲームループを管理するクラス。

#### メソッド

- `__init__(settings: GameSettings)`: ゲームループを初期化
- `run()`: メインループを実行
- `quit()`: ゲームを終了

## エンティティクラス

### Player

プレイヤーキャラクターを管理するクラス。

#### メソッド

- `__init__(x: int, y: int)`: プレイヤーを初期化
- `update(input_handler)`: プレイヤーを更新
- `render(screen: pygame.Surface)`: プレイヤーを描画
- `get_position() -> Tuple[int, int]`: 位置を取得
- `set_position(x: int, y: int)`: 位置を設定
- `add_to_inventory(item) -> bool`: アイテムをインベントリに追加
- `heal(amount: int)`: 体力を回復
- `rescue_pet()`: ペット救助数を増加

#### プロパティ

- `x: int`: X座標
- `y: int`: Y座標
- `health: int`: 体力
- `energy: int`: エネルギー
- `pets_rescued: int`: 救助したペット数

### Pet

ペットを管理するクラス。

#### メソッド

- `__init__(pet_type: str, x: int, y: int, pet_id: str = None)`: ペットを初期化
- `update(player_pos: Tuple[int, int])`: ペットを更新
- `render(screen: pygame.Surface)`: ペットを描画
- `interact_with_player(interaction_type: str)`: プレイヤーとの相互作用
- `can_be_rescued() -> bool`: 救助可能かチェック
- `rescue() -> bool`: ペットを救助
- `get_info() -> dict`: ペット情報を取得

#### プロパティ

- `pet_type: str`: ペットの種類
- `state: str`: ペットの状態
- `trust_level: int`: 信頼度
- `fear_level: int`: 恐怖度

### NPC

NPCを管理するクラス。

#### メソッド

- `__init__(npc_type: str, x: int, y: int, name: str = None)`: NPCを初期化
- `update(player_pos: Tuple[int, int])`: NPCを更新
- `render(screen: pygame.Surface)`: NPCを描画
- `talk() -> Optional[str]`: 対話を開始
- `set_patrol_route(points: List[Tuple[int, int]])`: パトロールルートを設定

## システムクラス

### SaveSystem

セーブシステムを管理するクラス。

#### メソッド

- `__init__(settings: GameSettings)`: セーブシステムを初期化
- `save_game(slot_number: int, game_data: Dict[str, Any]) -> bool`: ゲームデータを保存
- `load_game(slot_number: int) -> Optional[Dict[str, Any]]`: ゲームデータを読み込み
- `delete_save(slot_number: int) -> bool`: セーブデータを削除
- `get_save_info(slot_number: int) -> Optional[Dict[str, Any]]`: セーブデータ情報を取得
- `list_saves() -> List[Dict[str, Any]]`: 全セーブスロット情報を取得

### Inventory

インベントリシステムを管理するクラス。

#### メソッド

- `__init__(max_slots: int = 30)`: インベントリを初期化
- `add_item(item_id: str, quantity: int = 1) -> bool`: アイテムを追加
- `remove_item(item_id: str, quantity: int = 1) -> bool`: アイテムを削除
- `has_item(item_id: str, quantity: int = 1) -> bool`: アイテム所持チェック
- `use_item(item_id: str, target=None) -> Dict[str, Any]`: アイテムを使用
- `get_item_count(item_id: str) -> int`: アイテム所持数を取得

### PetCollection

ペット図鑑システムを管理するクラス。

#### メソッド

- `__init__(data_path: Path)`: ペット図鑑を初期化
- `discover_pet(pet_info: Dict[str, Any]) -> bool`: ペットを発見記録
- `rescue_pet(pet_id: str, rescue_info: Dict[str, Any]) -> bool`: ペット救助記録
- `return_pet(pet_id: str, return_info: Dict[str, Any]) -> bool`: ペット返却記録
- `get_collection_summary() -> Dict[str, Any]`: 図鑑概要を取得
- `search_pets(query: str) -> List[Dict[str, Any]]`: ペットを検索

## UIクラス

### MenuSystem

メニューシステムを管理するクラス。

#### メソッド

- `__init__()`: メニューシステムを初期化
- `show_main_menu()`: メインメニューを表示
- `show_pause_menu()`: ポーズメニューを表示
- `update(input_handler)`: メニューを更新
- `render(screen: pygame.Surface)`: メニューを描画
- `hide()`: メニューを非表示

### HUD

ゲーム中のHUDを管理するクラス。

#### メソッド

- `__init__()`: HUDを初期化
- `update(game_data: Dict[str, Any])`: HUDを更新
- `render(screen: pygame.Surface)`: HUDを描画
- `add_notification(text: str, color: tuple = COLOR_WHITE)`: 通知を追加
- `show()`: HUDを表示
- `hide()`: HUDを非表示

### DialogSystem

ダイアログシステムを管理するクラス。

#### メソッド

- `__init__()`: ダイアログシステムを初期化
- `show_message(title: str, message: str, callback: Callable = None)`: メッセージダイアログを表示
- `show_confirm(title: str, message: str, on_yes: Callable = None, on_no: Callable = None)`: 確認ダイアログを表示
- `show_conversation(speaker_name: str, dialogue_lines: List[str])`: 会話ダイアログを表示
- `update(input_handler)`: ダイアログシステムを更新
- `render(screen: pygame.Surface)`: ダイアログシステムを描画

## ミニゲームクラス

### MiniGameManager

ミニゲームを管理するクラス。

#### メソッド

- `__init__()`: ミニゲーム管理システムを初期化
- `start_game(game_type: str, pet_type: str, difficulty: int = 1) -> bool`: ミニゲームを開始
- `update(input_handler)`: ミニゲームを更新
- `render(screen: pygame.Surface)`: ミニゲームを描画
- `get_game_result() -> Optional[Dict[str, Any]]`: ゲーム結果を取得
- `get_recommended_game(pet_type: str, trust_level: int) -> str`: おすすめゲームを取得

## 多言語対応クラス

### LanguageManager

多言語対応を管理するクラス。

#### メソッド

- `__init__(locale_path: Path)`: 言語管理システムを初期化
- `set_language(language_code: str) -> bool`: 現在の言語を設定
- `get_text(key: str, **kwargs) -> str`: 指定キーのテキストを取得
- `get_current_language() -> str`: 現在の言語コードを取得
- `get_available_languages() -> Dict[str, str]`: 利用可能な言語一覧を取得

## 定数

### 画面設定

- `SCREEN_WIDTH: int = 1024`: 画面幅
- `SCREEN_HEIGHT: int = 768`: 画面高さ
- `TARGET_FPS: int = 60`: 目標フレームレート

### 色定義

- `COLOR_WHITE: tuple = (255, 255, 255)`: 白色
- `COLOR_BLACK: tuple = (0, 0, 0)`: 黒色
- `COLOR_RED: tuple = (255, 0, 0)`: 赤色
- `COLOR_GREEN: tuple = (0, 255, 0)`: 緑色
- `COLOR_BLUE: tuple = (0, 0, 255)`: 青色

### ゲーム定数

- `PLAYER_SPEED: int = 5`: プレイヤー移動速度
- `PET_SPEED: int = 3`: ペット移動速度
- `TILE_SIZE: int = 32`: タイルサイズ

### ペット関連

- `PET_TYPES: List[str]`: ペットの種類一覧
- `PET_STATE_LOST: str = "lost"`: 迷子状態
- `PET_STATE_RESCUED: str = "rescued"`: 救助済み状態

## 使用例

### 基本的なゲーム開始

```python
from config.settings import GameSettings
from src.game_engine.game_loop import GameLoop

# 設定を作成
settings = GameSettings()
settings.debug_mode = True

# ゲームループを開始
game = GameLoop(settings)
game.run()
```

### プレイヤーの作成と操作

```python
from src.entities.player import Player

# プレイヤーを作成
player = Player(100, 100)

# アイテムを追加
player.add_to_inventory("dog_food")

# 体力を回復
player.heal(20)
```

### ペットとの相互作用

```python
from src.entities.pet import Pet

# ペットを作成
pet = Pet("dog", 200, 150)

# プレイヤーとの相互作用
pet.interact_with_player("feed")

# 救助可能かチェック
if pet.can_be_rescued():
    pet.rescue()
```

### セーブ・ロード

```python
from src.systems.save_system import SaveSystem

# セーブシステムを作成
save_system = SaveSystem(settings)

# ゲームデータを保存
game_data = {"player": {"x": 100, "y": 200}}
save_system.save_game(1, game_data)

# ゲームデータを読み込み
loaded_data = save_system.load_game(1)
```

## エラーハンドリング

各メソッドは適切なエラーハンドリングを行い、失敗時には`False`やNoneを返します。
デバッグモードが有効な場合、詳細なエラー情報がコンソールに出力されます。

## パフォーマンス考慮事項

- ゲームループは60FPSで動作するよう最適化されています
- 大量のオブジェクトを扱う場合は、適切な更新頻度の調整が必要です
- メモリ使用量を抑えるため、不要なオブジェクトは適切に削除してください
