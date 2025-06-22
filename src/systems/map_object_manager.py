"""
マップオブジェクト管理システム
ベースタイルの上に配置するオブジェクト（岩・水・木など）を管理
"""

import pygame
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from src.systems.sprite_manager import SpriteManager, SpriteSize

class ObjectType(Enum):
    """オブジェクトタイプ"""
    ROCK = "rock"
    WATER = "water"
    TREE = "tree"
    BUSH = "bush"

@dataclass
class MapObject:
    """マップオブジェクト"""
    object_type: ObjectType
    x: int
    y: int
    width: int
    height: int
    is_obstacle: bool = True
    sprite_size: SpriteSize = SpriteSize.MEDIUM
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def contains_point(self, x: int, y: int) -> bool:
        return self.get_rect().collidepoint(x, y)

class MapObjectManager:
    """マップオブジェクト管理クラス"""
    
    def __init__(self, sprite_manager: SpriteManager):
        self.sprite_manager = sprite_manager
        self.objects: List[MapObject] = []
        
        # オブジェクトスプライト読み込み
        self._load_object_sprites()
    
    def _load_object_sprites(self):
        """オブジェクトスプライトを読み込み"""
        # 岩・水・木のスプライトを読み込み
        # 実際のファイルパスは後で調整
        object_files = {
            ObjectType.ROCK: "assets/images/objects/rock_object.png",
            ObjectType.WATER: "assets/images/objects/water_object.png", 
            ObjectType.TREE: "assets/images/objects/tree_object.png",
            ObjectType.BUSH: "assets/images/objects/bush_object.png"
        }
        
        for obj_type, path in object_files.items():
            # 仮実装: 既存のタイルスプライトを使用
            if obj_type == ObjectType.ROCK:
                # 岩オブジェクト用のスプライト（透明背景想定）
                pass
            elif obj_type == ObjectType.WATER:
                # 水オブジェクト用のスプライト（透明背景想定）
                pass
            elif obj_type == ObjectType.TREE:
                # 木オブジェクト用のスプライト（透明背景想定）
                pass
    
    def add_object(self, object_type: ObjectType, tile_x: int, tile_y: int, 
                   tile_size: int, is_obstacle: bool = True) -> MapObject:
        """オブジェクトを追加"""
        # タイル座標をピクセル座標に変換
        pixel_x = tile_x * tile_size
        pixel_y = tile_y * tile_size
        
        map_object = MapObject(
            object_type=object_type,
            x=pixel_x,
            y=pixel_y,
            width=tile_size,
            height=tile_size,
            is_obstacle=is_obstacle
        )
        
        self.objects.append(map_object)
        return map_object
    
    def remove_object_at(self, tile_x: int, tile_y: int, tile_size: int) -> bool:
        """指定位置のオブジェクトを削除"""
        pixel_x = tile_x * tile_size
        pixel_y = tile_y * tile_size
        
        for i, obj in enumerate(self.objects):
            if obj.x == pixel_x and obj.y == pixel_y:
                del self.objects[i]
                return True
        return False
    
    def get_object_at(self, tile_x: int, tile_y: int, tile_size: int) -> Optional[MapObject]:
        """指定位置のオブジェクトを取得"""
        pixel_x = tile_x * tile_size
        pixel_y = tile_y * tile_size
        
        for obj in self.objects:
            if obj.x == pixel_x and obj.y == pixel_y:
                return obj
        return None
    
    def is_obstacle_at(self, tile_x: int, tile_y: int, tile_size: int) -> bool:
        """指定位置に障害物があるかチェック"""
        obj = self.get_object_at(tile_x, tile_y, tile_size)
        return obj is not None and obj.is_obstacle
    
    def draw_objects(self, surface: pygame.Surface, camera_x: float = 0, camera_y: float = 0):
        """オブジェクトを描画"""
        for obj in self.objects:
            # カメラオフセットを適用
            draw_x = obj.x - camera_x
            draw_y = obj.y - camera_y
            
            # 画面内のオブジェクトのみ描画
            if (-obj.width <= draw_x <= surface.get_width() and 
                -obj.height <= draw_y <= surface.get_height()):
                
                sprite = self._get_object_sprite(obj)
                if sprite:
                    surface.blit(sprite, (draw_x, draw_y))
    
    def _get_object_sprite(self, obj: MapObject) -> Optional[pygame.Surface]:
        """オブジェクトのスプライトを取得"""
        # 仮実装: 既存のタイルスプライトを使用
        if obj.object_type == ObjectType.ROCK:
            return self.sprite_manager.get_tile_sprite('rock', obj.sprite_size)
        elif obj.object_type == ObjectType.WATER:
            return self.sprite_manager.get_tile_sprite('water', obj.sprite_size)
        elif obj.object_type == ObjectType.TREE:
            return self.sprite_manager.get_tile_sprite('tree', obj.sprite_size)
        
        return None
    
    def clear_objects(self):
        """全オブジェクトをクリア"""
        self.objects.clear()
    
    def get_objects_info(self) -> Dict:
        """オブジェクト情報を取得"""
        object_counts = {}
        obstacle_count = 0
        
        for obj in self.objects:
            obj_type = obj.object_type.value
            object_counts[obj_type] = object_counts.get(obj_type, 0) + 1
            if obj.is_obstacle:
                obstacle_count += 1
        
        return {
            'total_objects': len(self.objects),
            'obstacle_count': obstacle_count,
            'object_types': object_counts
        }
    
    def create_sample_objects(self, tile_size: int):
        """サンプルオブジェクトを作成"""
        # 岩オブジェクト
        self.add_object(ObjectType.ROCK, 3, 3, tile_size)
        self.add_object(ObjectType.ROCK, 7, 5, tile_size)
        self.add_object(ObjectType.ROCK, 2, 8, tile_size)
        
        # 水オブジェクト（池）
        for x in range(5, 8):
            for y in range(6, 9):
                self.add_object(ObjectType.WATER, x, y, tile_size)
        
        # 木オブジェクト
        self.add_object(ObjectType.TREE, 1, 1, tile_size)
        self.add_object(ObjectType.TREE, 9, 2, tile_size)
        self.add_object(ObjectType.TREE, 8, 8, tile_size)
