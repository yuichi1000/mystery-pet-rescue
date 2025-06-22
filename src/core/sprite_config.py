"""
スプライト設定・用途別サイズ定義
256x256ベース画像の用途別サイズ設定
"""

from enum import Enum
from typing import Dict, Tuple
from src.systems.sprite_manager import SpriteSize

class SpriteUsage(Enum):
    """スプライト用途"""
    # ゲーム内表示
    GAME_PLAYER = "game_player"           # ゲーム内プレイヤー
    GAME_PET = "game_pet"                 # ゲーム内ペット
    GAME_NPC = "game_npc"                 # ゲーム内NPC
    GAME_TILE = "game_tile"               # ゲーム内タイル
    
    # UI表示
    UI_ICON = "ui_icon"                   # UIアイコン
    UI_BUTTON = "ui_button"               # UIボタン
    UI_INVENTORY = "ui_inventory"         # インベントリスロット
    
    # 図鑑・詳細表示
    COLLECTION_DETAIL = "collection_detail"  # 図鑑詳細表示
    COLLECTION_LIST = "collection_list"      # 図鑑リスト表示
    
    # ミニゲーム
    MINIGAME_CARD = "minigame_card"       # 記憶ゲームカード
    MINIGAME_PLAYER = "minigame_player"   # ミニゲーム内プレイヤー
    
    # 建物・背景
    BUILDING_MAP = "building_map"         # マップ上の建物
    BUILDING_DETAIL = "building_detail"   # 建物詳細表示

class SpriteConfig:
    """スプライト設定管理"""
    
    # 用途別推奨サイズ設定（最小64x64）
    USAGE_SIZE_MAP: Dict[SpriteUsage, SpriteSize] = {
        # ゲーム内表示（64x64）
        SpriteUsage.GAME_PLAYER: SpriteSize.MEDIUM,
        SpriteUsage.GAME_PET: SpriteSize.MEDIUM,
        SpriteUsage.GAME_NPC: SpriteSize.MEDIUM,
        SpriteUsage.GAME_TILE: SpriteSize.MEDIUM,      # タイルも64x64
        
        # UI表示（64x64）
        SpriteUsage.UI_ICON: SpriteSize.MEDIUM,
        SpriteUsage.UI_BUTTON: SpriteSize.MEDIUM,
        SpriteUsage.UI_INVENTORY: SpriteSize.MEDIUM,
        
        # 図鑑・詳細表示（128x128 or 256x256）
        SpriteUsage.COLLECTION_DETAIL: SpriteSize.ORIGINAL,  # 最高品質
        SpriteUsage.COLLECTION_LIST: SpriteSize.LARGE,
        
        # ミニゲーム（用途に応じて）
        SpriteUsage.MINIGAME_CARD: SpriteSize.LARGE,     # カードは大きめ
        SpriteUsage.MINIGAME_PLAYER: SpriteSize.MEDIUM,
        
        # 建物・背景（128x128）
        SpriteUsage.BUILDING_MAP: SpriteSize.LARGE,
        SpriteUsage.BUILDING_DETAIL: SpriteSize.ORIGINAL,
    }
    
    @classmethod
    def get_recommended_size(cls, usage: SpriteUsage) -> SpriteSize:
        """用途に応じた推奨サイズを取得"""
        return cls.USAGE_SIZE_MAP.get(usage, SpriteSize.MEDIUM)
    
    @classmethod
    def get_size_dimensions(cls, size: SpriteSize) -> Tuple[int, int]:
        """サイズの実際の寸法を取得（最小64x64）"""
        size_map = {
            SpriteSize.ORIGINAL: (256, 256),
            SpriteSize.LARGE: (128, 128),
            SpriteSize.MEDIUM: (64, 64)  # 最小サイズ
        }
        return size_map.get(size, (64, 64))
    
    @classmethod
    def get_usage_info(cls) -> Dict[str, Dict]:
        """用途別設定情報を取得"""
        info = {}
        for usage, size in cls.USAGE_SIZE_MAP.items():
            dimensions = cls.get_size_dimensions(size)
            info[usage.value] = {
                'size': size.value,
                'dimensions': dimensions,
                'description': cls._get_usage_description(usage)
            }
        return info
    
    @classmethod
    def _get_usage_description(cls, usage: SpriteUsage) -> str:
        """用途の説明を取得"""
        descriptions = {
            SpriteUsage.GAME_PLAYER: "ゲーム内プレイヤーキャラクター",
            SpriteUsage.GAME_PET: "ゲーム内ペット表示",
            SpriteUsage.GAME_NPC: "ゲーム内NPC表示",
            SpriteUsage.GAME_TILE: "ゲーム内タイル表示（64x64）",
            SpriteUsage.UI_ICON: "UIアイコン表示（64x64）",
            SpriteUsage.UI_BUTTON: "UIボタン表示（64x64）",
            SpriteUsage.UI_INVENTORY: "インベントリスロット（64x64）",
            SpriteUsage.COLLECTION_DETAIL: "図鑑詳細表示（最高品質）",
            SpriteUsage.COLLECTION_LIST: "図鑑リスト表示",
            SpriteUsage.MINIGAME_CARD: "記憶ゲームカード",
            SpriteUsage.MINIGAME_PLAYER: "ミニゲーム内プレイヤー",
            SpriteUsage.BUILDING_MAP: "マップ上の建物",
            SpriteUsage.BUILDING_DETAIL: "建物詳細表示",
        }
        return descriptions.get(usage, "不明な用途")

# 便利関数
def get_sprite_for_usage(sprite_manager, sprite_type: str, sprite_id: str, usage: SpriteUsage):
    """用途に応じたスプライトを取得"""
    recommended_size = SpriteConfig.get_recommended_size(usage)
    
    if sprite_type == "pet":
        return sprite_manager.get_pet_sprite(sprite_id, "front", recommended_size)
    elif sprite_type == "player":
        return sprite_manager.get_player_sprite(sprite_id, recommended_size)
    elif sprite_type == "tile":
        return sprite_manager.get_tile_sprite(sprite_id, recommended_size)
    elif sprite_type == "building":
        return sprite_manager.get_building_sprite(sprite_id, recommended_size)
    
    return None
