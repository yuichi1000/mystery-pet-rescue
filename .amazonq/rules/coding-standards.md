# コーディング標準

## Python コーディング規約

### 基本規則
- **PEP 8** 完全準拠
- Python 3.9+ の機能を積極的に活用
- 型ヒント（Type Hints）必須

### 命名規則
```python
# クラス名：PascalCase（英語）
class PlayerCharacter:
    pass

# 関数名：snake_case（英語）
def calculate_damage(base_damage: int, multiplier: float) -> int:
    return int(base_damage * multiplier)

# 定数：UPPER_SNAKE_CASE（英語）
MAX_INVENTORY_SIZE = 20
DEFAULT_SAVE_PATH = "saves/"

# 変数名：snake_case（英語）
player_health = 100
current_scene = "residential_area"
```

### 型ヒント規則
```python
from typing import List, Dict, Optional, Union, Tuple
from dataclasses import dataclass

# 必須：すべての関数に型ヒント
def find_item(item_id: str, inventory: List[Dict[str, any]]) -> Optional[Dict[str, any]]:
    """アイテムをインベントリから検索"""
    for item in inventory:
        if item["id"] == item_id:
            return item
    return None

# データクラスの活用
@dataclass
class GameState:
    current_scene: str
    player_position: Tuple[int, int]
    inventory: List[str]
    flags: Dict[str, bool]
```

### コメント規則
```python
# 日本語コメントOK（実装の説明）
def apply_damage(entity: Entity, damage: int) -> None:
    """
    エンティティにダメージを適用する
    
    Args:
        entity: ダメージを受けるエンティティ
        damage: 適用するダメージ量
    """
    # 防御力を考慮したダメージ計算
    actual_damage = max(0, damage - entity.defense)
    entity.health -= actual_damage
    
    # ダメージエフェクトの表示
    if actual_damage > 0:
        show_damage_effect(entity.position, actual_damage)
```

## ファイル構成規約

### ディレクトリ構造
```
mystery-pet-rescue/
├── src/
│   ├── __init__.py
│   ├── main.py              # エントリーポイント
│   ├── core/                # コアシステム
│   │   ├── __init__.py
│   │   ├── game.py         # ゲームループ
│   │   ├── scene.py        # シーン管理
│   │   └── events.py       # イベント処理
│   ├── entities/            # ゲームエンティティ
│   │   ├── __init__.py
│   │   ├── player.py
│   │   ├── npc.py
│   │   └── pet.py
│   ├── systems/             # ゲームシステム
│   │   ├── __init__.py
│   │   ├── inventory.py
│   │   ├── dialogue.py
│   │   ├── puzzle.py
│   │   └── save.py
│   ├── scenes/              # ゲームシーン
│   │   ├── __init__.py
│   │   ├── menu.py
│   │   ├── residential.py
│   │   └── forest.py
│   ├── ui/                  # UI コンポーネント
│   │   ├── __init__.py
│   │   ├── widgets.py
│   │   └── dialogs.py
│   └── utils/               # ユーティリティ
│       ├── __init__.py
│       ├── audio.py
│       ├── i18n.py
│       └── config.py
├── assets/                  # ゲームアセット
│   ├── images/
│   ├── sounds/
│   ├── music/
│   └── locales/
├── tests/                   # テストコード
│   ├── unit/
│   ├── integration/
│   └── e2e/
├── docs/                    # ドキュメント
└── config/                  # 設定ファイル
```

### モジュール設計原則
1. **単一責任の原則**
   - 1モジュール1機能
   - 明確な責任範囲

2. **依存関係**
   - 循環参照の禁止
   - 依存性注入の活用

3. **インポート順序**
```python
# 1. 標準ライブラリ
import os
import sys
from typing import List, Dict

# 2. サードパーティライブラリ
import pygame
import pygame_gui

# 3. プロジェクト内モジュール
from src.core import Scene
from src.entities import Player
from src.utils.config import Config
```

## エラー処理

### 例外処理規則
```python
# カスタム例外の定義
class GameError(Exception):
    """ゲーム関連の基底例外クラス"""
    pass

class SaveError(GameError):
    """セーブ関連のエラー"""
    pass

# 適切な例外処理
def save_game(save_slot: int) -> bool:
    """
    ゲームをセーブする
    
    Returns:
        bool: セーブ成功時True
        
    Raises:
        SaveError: セーブに失敗した場合
    """
    try:
        save_data = create_save_data()
        write_save_file(save_slot, save_data)
        return True
    except IOError as e:
        # ログ記録と再スロー
        logger.error(f"セーブファイル書き込みエラー: {e}")
        raise SaveError(f"セーブスロット{save_slot}への書き込みに失敗しました") from e
```

### ログ記録
```python
import logging

# ロガー設定
logger = logging.getLogger(__name__)

# ログレベルの使い分け
logger.debug("デバッグ情報：変数の値など")
logger.info("通常の処理フロー情報")
logger.warning("警告：想定内だが注意が必要")
logger.error("エラー：処理は継続可能")
logger.critical("致命的エラー：処理継続不可")
```

## テスト要件

### 単体テスト
```python
# tests/unit/test_inventory.py
import pytest
from src.systems.inventory import Inventory

class TestInventory:
    """インベントリシステムのテスト"""
    
    def test_add_item(self):
        """アイテム追加のテスト"""
        inventory = Inventory(capacity=10)
        item = {"id": "key_001", "name": "家の鍵"}
        
        assert inventory.add_item(item) is True
        assert len(inventory.items) == 1
        
    def test_inventory_full(self):
        """インベントリ満杯時のテスト"""
        inventory = Inventory(capacity=1)
        item1 = {"id": "item_001", "name": "アイテム1"}
        item2 = {"id": "item_002", "name": "アイテム2"}
        
        assert inventory.add_item(item1) is True
        assert inventory.add_item(item2) is False
```

### テストカバレッジ
- 単体テスト：80%以上
- 統合テスト：主要フロー網羅
- E2Eテスト：クリティカルパス

## パフォーマンス基準

### 最適化指針
```python
# Bad: 非効率なループ
items = []
for i in range(1000):
    items.append(process_item(i))

# Good: リスト内包表記
items = [process_item(i) for i in range(1000)]

# Better: ジェネレータ（メモリ効率）
items = (process_item(i) for i in range(1000))
```

### プロファイリング
- ボトルネックの特定
- cProfile使用
- 定期的な計測

## セキュリティ

### 環境変数と機密情報管理
```python
# .env ファイルの例
BEATOVEN_API_KEY=your_api_key_here
BEATOVEN_API_URL=https://api.beatoven.ai/v1
DEBUG_MODE=False
SECRET_KEY=your_secret_key_here

# Python での読み込み
import os
from dotenv import load_dotenv

# .env ファイルの読み込み
load_dotenv()

class AudioConfig:
    """音楽・効果音生成の設定"""
    BEATOVEN_API_KEY = os.getenv('BEATOVEN_API_KEY')
    BEATOVEN_API_URL = os.getenv('BEATOVEN_API_URL', 'https://api.beatoven.ai/v1')
    
    @classmethod
    def validate(cls):
        """API設定の検証"""
        if not cls.BEATOVEN_API_KEY:
            raise ValueError("BEATOVEN_API_KEY が設定されていません")
```

### .gitignore への追加必須
```
# 環境変数ファイル
.env
.env.local
.env.*.local

# APIキー関連
*_api_key*
*_secret*
```

### セーブデータ保護
```python
from cryptography.fernet import Fernet

class SecureSaveSystem:
    """暗号化セーブシステム"""
    
    def __init__(self):
        self.cipher = Fernet(self._get_or_create_key())
    
    def save_encrypted(self, data: dict) -> bytes:
        """データを暗号化して保存"""
        json_data = json.dumps(data)
        return self.cipher.encrypt(json_data.encode())
```

### 入力検証
- ユーザー入力は必ず検証
- SQLインジェクション対策（該当する場合）
- パストラバーサル対策
- APIキーの露出防止

## ドキュメント

### 必須ドキュメント
1. **README.md**：プロジェクト概要
2. **DEVELOPMENT_GUIDE.md**：開発ガイド
3. **API.md**：内部API仕様
4. **CHANGELOG.md**：変更履歴

### コード内ドキュメント
- すべてのパブリック関数にdocstring
- 複雑なロジックにはコメント
- TODO/FIXME の明記