"""
建物システム
建物の配置・描画・相互作用を管理
"""

import pygame
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum

from src.utils.asset_manager import get_asset_manager

class BuildingType(Enum):
    """建物タイプ"""
    HOUSE_RESIDENTIAL = "house_residential"
    HOUSE_PETSHOP = "house_petshop"
    PARK_FACILITY = "park_facility"

@dataclass
class Building:
    """建物データ"""
    id: str
    building_type: BuildingType
    position: Tuple[int, int]  # タイル座標
    size: Tuple[int, int]      # タイルサイズ
    name: str
    name_en: str
    interactable: bool = True
    description: str = ""
    special: bool = False

class BuildingSystem:
    """建物システムクラス"""
    
    def __init__(self, tile_size: int = 64):
        self.tile_size = tile_size
        self.asset_manager = get_asset_manager()
        
        # 建物スプライト
        self.building_sprites: Dict[BuildingType, pygame.Surface] = {}
        
        # 建物リスト
        self.buildings: List[Building] = []
        
        # 建物画像を読み込み
        self._load_building_sprites()
        
        print("🏠 建物システム初期化完了")
    
    def _load_building_sprites(self):
        """建物画像を読み込み"""
        building_paths = {
            BuildingType.HOUSE_RESIDENTIAL: "buildings/house_residential.png",
            BuildingType.HOUSE_PETSHOP: "buildings/house_petshop.png",
            BuildingType.PARK_FACILITY: "buildings/park_facility.png"
        }
        
        for building_type, path in building_paths.items():
            # 建物画像を元のサイズで読み込み（描画時にスケール）
            sprite = self.asset_manager.load_image(path)
            if sprite:
                self.building_sprites[building_type] = sprite
                print(f"✅ 建物画像読み込み: {building_type.value}")
            else:
                print(f"❌ 建物画像読み込み失敗: {building_type.value} - {path}")
    
    def load_buildings_from_map(self, map_data: Dict[str, Any]):
        """マップデータから建物を読み込み"""
        self.buildings.clear()
        
        buildings_data = map_data.get("buildings", [])
        for building_data in buildings_data:
            try:
                building = Building(
                    id=building_data["id"],
                    building_type=BuildingType(building_data["type"]),
                    position=(building_data["position"]["x"], building_data["position"]["y"]),
                    size=(building_data["size"]["width"], building_data["size"]["height"]),
                    name=building_data["name"],
                    name_en=building_data.get("name_en", building_data["name"]),
                    interactable=building_data.get("interactable", True),
                    description=building_data.get("description", ""),
                    special=building_data.get("special", False)
                )
                self.buildings.append(building)
                print(f"🏠 建物追加: {building.name} ({building.building_type.value})")
            except Exception as e:
                print(f"❌ 建物データエラー: {e}")
        
        print(f"✅ 建物読み込み完了: {len(self.buildings)}軒")
    
    def draw_buildings(self, screen: pygame.Surface, camera_offset: Tuple[int, int], debug_collision: bool = False):
        """建物を描画"""
        for building in self.buildings:
            sprite = self.building_sprites.get(building.building_type)
            if sprite:
                # タイル座標をピクセル座標に変換
                pixel_x = building.position[0] * self.tile_size - camera_offset[0]
                pixel_y = building.position[1] * self.tile_size - camera_offset[1]
                
                # 画面内にある場合のみ描画
                screen_rect = screen.get_rect()
                building_rect = pygame.Rect(
                    pixel_x, pixel_y,
                    building.size[0] * self.tile_size,
                    building.size[1] * self.tile_size
                )
                
                if screen_rect.colliderect(building_rect):
                    # 建物サイズに合わせてスプライトをスケール
                    scaled_sprite = pygame.transform.scale(
                        sprite,
                        (building.size[0] * self.tile_size, building.size[1] * self.tile_size)
                    )
                    screen.blit(scaled_sprite, (pixel_x, pixel_y))
                    
                    # デバッグ: 衝突判定エリアを表示
                    if debug_collision:
                        collision_rect = pygame.Rect(
                            pixel_x, pixel_y,
                            building.size[0] * self.tile_size,
                            building.size[1] * self.tile_size
                        )
                        pygame.draw.rect(screen, (255, 0, 0, 100), collision_rect, 2)  # 赤い枠
    
    def get_building_at_position(self, tile_x: int, tile_y: int) -> Optional[Building]:
        """指定位置の建物を取得"""
        for building in self.buildings:
            bx, by = building.position
            bw, bh = building.size
            
            if bx <= tile_x < bx + bw and by <= tile_y < by + bh:
                return building
        return None
    
    def get_interactable_buildings_near(self, tile_x: int, tile_y: int, radius: int = 1) -> List[Building]:
        """指定位置周辺の相互作用可能な建物を取得"""
        nearby_buildings = []
        
        for building in self.buildings:
            if not building.interactable:
                continue
                
            bx, by = building.position
            bw, bh = building.size
            
            # 建物の境界との距離をチェック
            min_dist_x = max(0, max(bx - tile_x, tile_x - (bx + bw - 1)))
            min_dist_y = max(0, max(by - tile_y, tile_y - (by + bh - 1)))
            
            if min_dist_x <= radius and min_dist_y <= radius:
                nearby_buildings.append(building)
        
        return nearby_buildings
    
    def is_position_blocked_by_building(self, tile_x: int, tile_y: int, debug: bool = False) -> bool:
        """指定位置が建物によってブロックされているかチェック"""
        for building in self.buildings:
            bx, by = building.position
            bw, bh = building.size
            
            # 建物の全エリア + 周辺バッファを衝突判定とする
            # ペットが建物内部に配置されるのを防ぐため適切なマージンを設定
            buffer = 1  # 周辺バッファ（ペット配置の安全性を確保）
            
            collision_x1 = bx - buffer
            collision_y1 = by - buffer  
            collision_x2 = bx + bw + buffer
            collision_y2 = by + bh + buffer
            
            if collision_x1 <= tile_x < collision_x2 and collision_y1 <= tile_y < collision_y2:
                if debug:
                    print(f"🏠 建物衝突: {building.name} at ({tile_x}, {tile_y}) - 建物エリア: ({collision_x1}, {collision_y1}) to ({collision_x2}, {collision_y2})")
                return True
        
        return False
    
    def get_building_info(self, building_id: str) -> Optional[Dict[str, Any]]:
        """建物情報を取得"""
        for building in self.buildings:
            if building.id == building_id:
                return {
                    "id": building.id,
                    "type": building.building_type.value,
                    "name": building.name,
                    "description": building.description,
                    "position": building.position,
                    "size": building.size,
                    "interactable": building.interactable,
                    "special": building.special
                }
        return None
