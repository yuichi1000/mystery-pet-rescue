"""
スプライト管理システム
個別ファイルからスプライトを読み込み・管理
"""

import pygame
import os
from typing import Dict, Optional
from enum import Enum

class Direction(Enum):
    """方向列挙型"""
    FRONT = "front"
    BACK = "back"
    LEFT = "left"
    RIGHT = "right"

class SpriteManager:
    """スプライト管理クラス"""
    
    def __init__(self):
        self.sprite_cache: Dict[str, pygame.Surface] = {}
        self.pet_sprites: Dict[str, Dict[str, pygame.Surface]] = {}
        self.player_sprites: Dict[str, pygame.Surface] = {}
        self.npc_sprites: Dict[str, pygame.Surface] = {}
    
    def load_sprite(self, file_path: str) -> Optional[pygame.Surface]:
        """個別スプライトファイルを読み込み"""
        if file_path in self.sprite_cache:
            return self.sprite_cache[file_path]
        
        if not os.path.exists(file_path):
            print(f"警告: スプライトファイルが見つかりません: {file_path}")
            return None
        
        try:
            sprite = pygame.image.load(file_path).convert_alpha()
            self.sprite_cache[file_path] = sprite
            return sprite
        except pygame.error as e:
            print(f"エラー: スプライト読み込みに失敗しました: {file_path} - {e}")
            return None
    
    def load_pet_sprites(self, pet_id: str, sprite_paths: Dict[str, str]) -> Dict[str, pygame.Surface]:
        """ペットの全方向スプライトを読み込み"""
        if pet_id in self.pet_sprites:
            return self.pet_sprites[pet_id]
        
        sprites = {}
        for direction, path in sprite_paths.items():
            sprite = self.load_sprite(path)
            if sprite:
                sprites[direction] = sprite
            else:
                # フォールバック: デフォルトスプライト作成
                sprites[direction] = self.create_default_sprite(32, 32, (100, 100, 100))
        
        self.pet_sprites[pet_id] = sprites
        return sprites
    
    def load_player_sprites(self) -> Dict[str, pygame.Surface]:
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
            sprite = self.load_sprite(path)
            if sprite:
                self.player_sprites[direction] = sprite
            else:
                # フォールバック: デフォルトスプライト作成
                self.player_sprites[direction] = self.create_default_sprite(32, 32, (0, 100, 200))
        
        return self.player_sprites
    
    def load_npc_sprites(self) -> Dict[str, pygame.Surface]:
        """NPCの全表情スプライトを読み込み"""
        if self.npc_sprites:
            return self.npc_sprites
        
        sprite_paths = {
            "normal": "assets/images/characters/npc_adult_normal.png",
            "talking": "assets/images/characters/npc_adult_talking.png",
            "surprised": "assets/images/characters/npc_adult_surprised.png"
        }
        
        for expression, path in sprite_paths.items():
            sprite = self.load_sprite(path)
            if sprite:
                self.npc_sprites[expression] = sprite
            else:
                # フォールバック: デフォルトスプライト作成
                self.npc_sprites[expression] = self.create_default_sprite(32, 32, (100, 150, 100))
        
        return self.npc_sprites
    
    def get_pet_sprite(self, pet_id: str, direction: str) -> Optional[pygame.Surface]:
        """ペットの指定方向スプライトを取得"""
        if pet_id not in self.pet_sprites:
            return None
        
        return self.pet_sprites[pet_id].get(direction)
    
    def get_player_sprite(self, direction: str) -> Optional[pygame.Surface]:
        """プレイヤーの指定方向スプライトを取得"""
        if not self.player_sprites:
            self.load_player_sprites()
        
        return self.player_sprites.get(direction)
    
    def get_npc_sprite(self, expression: str) -> Optional[pygame.Surface]:
        """NPCの指定表情スプライトを取得"""
        if not self.npc_sprites:
            self.load_npc_sprites()
        
        return self.npc_sprites.get(expression)
    
    def create_default_sprite(self, width: int, height: int, color: tuple) -> pygame.Surface:
        """デフォルトスプライトを作成"""
        sprite = pygame.Surface((width, height), pygame.SRCALPHA)
        sprite.fill(color)
        
        # 簡単な枠線を追加
        pygame.draw.rect(sprite, (255, 255, 255), sprite.get_rect(), 2)
        
        return sprite
    
    def clear_cache(self) -> None:
        """スプライトキャッシュをクリア"""
        self.sprite_cache.clear()
        self.pet_sprites.clear()
        self.player_sprites.clear()
        self.npc_sprites.clear()
    
    def preload_all_sprites(self, pets_data: Dict) -> None:
        """全スプライトを事前読み込み"""
        # プレイヤースプライト読み込み
        self.load_player_sprites()
        
        # NPCスプライト読み込み
        self.load_npc_sprites()
        
        # ペットスプライト読み込み
        for pet_id, pet_data in pets_data.items():
            if 'sprites' in pet_data:
                self.load_pet_sprites(pet_id, pet_data['sprites'])
    
    def get_sprite_info(self) -> Dict:
        """スプライト情報を取得"""
        return {
            'cached_sprites': len(self.sprite_cache),
            'pet_sprites': len(self.pet_sprites),
            'player_sprites': len(self.player_sprites),
            'npc_sprites': len(self.npc_sprites)
        }
