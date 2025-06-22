"""
スプライト管理システム（256x256ハイブリッド対応）
個別ファイルからスプライトを読み込み・管理し、用途に応じてサイズを調整
"""

import pygame
import os
from typing import Dict, Optional, Tuple
from enum import Enum

class SpriteSize(Enum):
    """スプライトサイズ種別（最小64x64）"""
    ORIGINAL = "original"    # 256x256（オリジナル）
    LARGE = "large"         # 128x128（図鑑・詳細表示用）
    MEDIUM = "medium"       # 64x64（ゲーム内表示用・最小サイズ）

class Direction(Enum):
    """方向列挙型"""
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"

class SpriteManager:
    """スプライト管理クラス（ハイブリッド対応）"""
    
    def __init__(self):
        self.sprite_cache: Dict[str, Dict[str, pygame.Surface]] = {}
        self.pet_sprites: Dict[str, Dict[str, Dict[str, pygame.Surface]]] = {}
        self.player_sprites: Dict[str, Dict[str, pygame.Surface]] = {}
        self.building_sprites: Dict[str, Dict[str, pygame.Surface]] = {}
        self.tile_sprites: Dict[str, Dict[str, pygame.Surface]] = {}
        
        # サイズマッピング（最小64x64）
        self.size_mapping = {
            SpriteSize.ORIGINAL: (256, 256),
            SpriteSize.LARGE: (128, 128),
            SpriteSize.MEDIUM: (64, 64)  # 最小サイズ
        }
    
    def load_sprite_with_variants(self, file_path: str, sprite_id: str) -> Dict[str, pygame.Surface]:
        """256x256画像を読み込み、複数サイズのバリエーションを生成"""
        if sprite_id in self.sprite_cache:
            return self.sprite_cache[sprite_id]
        
        if not os.path.exists(file_path):
            print(f"警告: スプライトファイルが見つかりません: {file_path}")
            return self._create_default_sprite_variants()
        
        try:
            # オリジナル画像読み込み（256x256想定）
            original_sprite = pygame.image.load(file_path).convert_alpha()
            
            # 各サイズのバリエーションを生成
            variants = {}
            for size_type, dimensions in self.size_mapping.items():
                if size_type == SpriteSize.ORIGINAL:
                    variants[size_type.value] = original_sprite
                else:
                    # 高品質スケーリング
                    scaled_sprite = pygame.transform.smoothscale(original_sprite, dimensions)
                    variants[size_type.value] = scaled_sprite
            
            self.sprite_cache[sprite_id] = variants
            return variants
            
        except pygame.error as e:
            print(f"エラー: スプライト読み込みに失敗しました: {file_path} - {e}")
            return self._create_default_sprite_variants()
    
    def _create_default_sprite_variants(self) -> Dict[str, pygame.Surface]:
        """デフォルトスプライトのバリエーションを作成"""
        variants = {}
        for size_type, dimensions in self.size_mapping.items():
            sprite = pygame.Surface(dimensions, pygame.SRCALPHA)
            sprite.fill((100, 100, 100, 128))
            pygame.draw.rect(sprite, (255, 255, 255), sprite.get_rect(), 2)
            variants[size_type.value] = sprite
        return variants
    
    def get_pet_sprite(self, pet_id: str, direction: str, size: SpriteSize = SpriteSize.MEDIUM) -> Optional[pygame.Surface]:
        """ペットスプライトを取得"""
        if pet_id not in self.pet_sprites:
            return None
        
        if direction not in self.pet_sprites[pet_id]:
            return None
        
        return self.pet_sprites[pet_id][direction].get(size.value)
    
    def get_player_sprite(self, direction: str, size: SpriteSize = SpriteSize.MEDIUM) -> Optional[pygame.Surface]:
        """プレイヤースプライトを取得"""
        if not self.player_sprites:
            self.load_player_sprites()
        
        if direction not in self.player_sprites:
            return None
        
        return self.player_sprites[direction].get(size.value)
    
    def load_player_sprites(self) -> Dict[str, Dict[str, pygame.Surface]]:
        """プレイヤーの全方向スプライトを読み込み"""
        if self.player_sprites:
            return self.player_sprites
        
        sprite_paths = {
            Direction.FRONT.value: "assets/images/characters/player_front.png",
            Direction.BACK.value: "assets/images/characters/player_back.png",
            Direction.LEFT.value: "assets/images/characters/player_left.png",
            Direction.RIGHT.value: "assets/images/characters/player_right.png"
        }
        
        for direction, path in sprite_paths.items():
            sprite_id = f"player_{direction}"
            variants = self.load_sprite_with_variants(path, sprite_id)
            self.player_sprites[direction] = variants
        
        return self.player_sprites
    
    def get_tile_sprite(self, tile_type: str, size: SpriteSize = SpriteSize.MEDIUM) -> Optional[pygame.Surface]:
        """タイルスプライトを取得（デフォルトは64x64）"""
        if not self.tile_sprites:
            self.load_tile_sprites()
        
        if tile_type not in self.tile_sprites:
            return None
        
        return self.tile_sprites[tile_type].get(size.value)
    
    def load_tile_sprites(self) -> Dict[str, Dict[str, pygame.Surface]]:
        """タイルスプライトを読み込み"""
        if self.tile_sprites:
            return self.tile_sprites
        
        tile_files = {
            "grass": "assets/images/tiles/grass_tile.png",
            "ground": "assets/images/tiles/ground_tile.png",
            "stone_wall": "assets/images/tiles/stone_wall_tile.png",
            "water": "assets/images/tiles/water_tile.png",
            "tree": "assets/images/tiles/tree_tile.png",
            "rock": "assets/images/tiles/rock_tile.png",
            "concrete": "assets/images/tiles/concrete_tile.png"
        }
        
        for tile_type, path in tile_files.items():
            sprite_id = f"tile_{tile_type}"
            variants = self.load_sprite_with_variants(path, sprite_id)
            self.tile_sprites[tile_type] = variants
        
        return self.tile_sprites
    
    def clear_cache(self) -> None:
        """スプライトキャッシュをクリア"""
        self.sprite_cache.clear()
        self.pet_sprites.clear()
        self.player_sprites.clear()
        self.tile_sprites.clear()
    
    def get_sprite_info(self) -> Dict:
        """スプライト情報を取得"""
        return {
            'cached_sprites': len(self.sprite_cache),
            'pet_sprites': len(self.pet_sprites),
            'player_sprites': len(self.player_sprites),
            'tile_sprites': len(self.tile_sprites),
            'available_sizes': [size.value for size in SpriteSize]
        }
