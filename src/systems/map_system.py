"""
タイルベースマップシステム
マップデータの読み込み・描画・衝突判定
"""

import pygame
import json
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from src.utils.asset_manager import get_asset_manager

class TileType(Enum):
    """タイルタイプ"""
    GRASS = "grass"
    GROUND = "ground"
    CONCRETE = "concrete"
    ROCK = "rock"
    STONE_WALL = "stone_wall"
    TREE = "tree"
    WATER = "water"

@dataclass
class TileData:
    """タイルデータ"""
    tile_type: TileType
    walkable: bool = True
    sprite_path: str = ""
    collision: bool = False

@dataclass
class MapData:
    """マップデータ"""
    width: int
    height: int
    tile_size: int
    tiles: List[List[TileType]]
    spawn_points: Dict[str, Tuple[int, int]]
    pet_locations: List[Tuple[int, int]]

class MapSystem:
    """マップシステムクラス"""
    
    def __init__(self, tile_size: int = 64):
        self.tile_size = tile_size
        self.asset_manager = get_asset_manager()
        
        # タイル定義
        self.tile_definitions = self._setup_tile_definitions()
        
        # タイル画像
        self.tile_sprites: Dict[TileType, pygame.Surface] = {}
        
        # 現在のマップ
        self.current_map: Optional[MapData] = None
        self.map_surface: Optional[pygame.Surface] = None
        
        # 描画最適化
        self.visible_tiles_cache = {}
        self.last_camera_pos = (0, 0)
        
        # タイル画像を読み込み
        self._load_tile_sprites()
        
        print("🗺️ マップシステム初期化完了")
    
    def _setup_tile_definitions(self) -> Dict[TileType, TileData]:
        """タイル定義を設定"""
        return {
            TileType.GRASS: TileData(
                tile_type=TileType.GRASS,
                walkable=True,
                sprite_path="tiles/grass_tile.png",
                collision=False
            ),
            TileType.GROUND: TileData(
                tile_type=TileType.GROUND,
                walkable=True,
                sprite_path="tiles/ground_tile.png",
                collision=False
            ),
            TileType.CONCRETE: TileData(
                tile_type=TileType.CONCRETE,
                walkable=True,
                sprite_path="tiles/concrete_tile.png",
                collision=False
            ),
            TileType.ROCK: TileData(
                tile_type=TileType.ROCK,
                walkable=False,
                sprite_path="tiles/rock_tile.png",
                collision=True
            ),
            TileType.STONE_WALL: TileData(
                tile_type=TileType.STONE_WALL,
                walkable=False,
                sprite_path="tiles/stone_wall_tile.png",
                collision=True
            ),
            TileType.TREE: TileData(
                tile_type=TileType.TREE,
                walkable=False,
                sprite_path="tiles/tree_tile.png",
                collision=True
            ),
            TileType.WATER: TileData(
                tile_type=TileType.WATER,
                walkable=False,
                sprite_path="tiles/water_tile.png",
                collision=True
            )
        }
    
    def _load_tile_sprites(self):
        """タイル画像を読み込み"""
        for tile_type, tile_data in self.tile_definitions.items():
            sprite = self.asset_manager.load_image(
                tile_data.sprite_path,
                (self.tile_size, self.tile_size)
            )
            if sprite:
                self.tile_sprites[tile_type] = sprite
                print(f"✅ タイル画像読み込み: {tile_type.value}")
            else:
                print(f"❌ タイル画像読み込み失敗: {tile_type.value} - {tile_data.sprite_path}")
                # プレースホルダーは作らない！画像がないならエラー
    
    def load_map(self, map_file: str) -> bool:
        """マップファイルを読み込み"""
        map_path = Path("data/maps") / map_file
        
        try:
            if map_path.exists():
                with open(map_path, 'r', encoding='utf-8') as f:
                    map_json = json.load(f)
                
                self.current_map = self._parse_map_data(map_json)
                self._generate_map_surface()
                
                print(f"✅ マップ読み込み完了: {map_file}")
                print(f"📐 マップサイズ: {self.current_map.width}x{self.current_map.height}")
                return True
            else:
                print(f"⚠️ マップファイルが見つかりません: {map_path}")
                self._create_default_map()
                return False
                
        except Exception as e:
            print(f"❌ マップ読み込みエラー: {e}")
            self._create_default_map()
            return False
    
    def _parse_map_data(self, map_json: Dict[str, Any]) -> MapData:
        """JSONデータをMapDataに変換（新旧形式対応）"""
        # 新形式（dimensions）と旧形式の両方に対応
        if "dimensions" in map_json:
            # 新形式
            dimensions = map_json["dimensions"]
            width = dimensions.get("width", 20)
            height = dimensions.get("height", 15)
            tile_size = dimensions.get("tile_size", self.tile_size)
        else:
            # 旧形式
            width = map_json.get("width", 20)
            height = map_json.get("height", 15)
            tile_size = map_json.get("tile_size", self.tile_size)
        
        print(f"📏 マップデータ解析: {width}x{height}, tile_size={tile_size}")
        
        # タイルデータの変換
        tiles = []
        tile_data = map_json.get("tiles", [])
        
        for row in tile_data:
            tile_row = []
            for tile_str in row:
                try:
                    tile_type = TileType(tile_str)
                    tile_row.append(tile_type)
                except ValueError:
                    tile_row.append(TileType.GRASS)  # デフォルト
            tiles.append(tile_row)
        
        # 不足分を埋める
        while len(tiles) < height:
            tiles.append([TileType.GRASS] * width)
        
        for row in tiles:
            while len(row) < width:
                row.append(TileType.GRASS)
        
        # スポーン地点
        spawn_points = map_json.get("spawn_points", {
            "player": [5, 5],
            "pets": [[10, 8], [15, 12], [8, 3], [18, 10]]
        })
        
        # ペット位置
        pet_locations = map_json.get("pet_locations", [[10, 8], [15, 12], [8, 3], [18, 10]])
        
        return MapData(
            width=width,
            height=height,
            tile_size=tile_size,
            tiles=tiles,
            spawn_points=spawn_points,
            pet_locations=pet_locations
        )
    
    def _create_default_map(self):
        """デフォルトマップを作成"""
        width, height = 25, 20
        
        # 基本的な地形パターンを作成
        tiles = []
        for y in range(height):
            row = []
            for x in range(width):
                # 境界は石壁
                if x == 0 or x == width-1 or y == 0 or y == height-1:
                    row.append(TileType.STONE_WALL)
                # 水域
                elif 8 <= x <= 12 and 6 <= y <= 9:
                    row.append(TileType.WATER)
                # 木々
                elif (x + y) % 7 == 0 and x > 2 and x < width-3:
                    row.append(TileType.TREE)
                # 岩
                elif (x * y) % 11 == 0 and x > 1 and x < width-2:
                    row.append(TileType.ROCK)
                # コンクリート道
                elif y == height // 2:
                    row.append(TileType.CONCRETE)
                elif x == width // 2:
                    row.append(TileType.CONCRETE)
                # 地面と草地
                elif (x + y) % 3 == 0:
                    row.append(TileType.GROUND)
                else:
                    row.append(TileType.GRASS)
            tiles.append(row)
        
        self.current_map = MapData(
            width=width,
            height=height,
            tile_size=self.tile_size,
            tiles=tiles,
            spawn_points={
                "player": (5, 5),
                "pets": [(10, 8), (15, 12), (8, 3), (18, 10)]
            },
            pet_locations=[(10, 8), (15, 12), (8, 3), (18, 10)]
        )
        
        self._generate_map_surface()
        print("🗺️ デフォルトマップを生成しました")
    
    def _generate_map_surface(self):
        """マップ全体を事前描画（画像使用版）"""
        if not self.current_map:
            return
        
        map_width = self.current_map.width * self.current_map.tile_size
        map_height = self.current_map.height * self.current_map.tile_size
        
        print(f"🗺️ マップサーフェス生成: {map_width} x {map_height}")
        print(f"   タイル数: {self.current_map.width} x {self.current_map.height}")
        print(f"   タイルサイズ: {self.current_map.tile_size}")
        
        self.map_surface = pygame.Surface((map_width, map_height))
        
        # 実際に生成されたサーフェスサイズを確認
        actual_size = self.map_surface.get_size()
        print(f"✅ 実際のマップサーフェスサイズ: {actual_size}")
        
        # 基本タイル（草・道路）を描画
        for y in range(self.current_map.height):
            for x in range(self.current_map.width):
                tile_type = self.current_map.tiles[y][x]
                if tile_type in self.tile_sprites:
                    sprite = self.tile_sprites[tile_type]
                    pos_x = x * self.current_map.tile_size
                    pos_y = y * self.current_map.tile_size
                    self.map_surface.blit(sprite, (pos_x, pos_y))
        
        # 建物画像を描画
        if hasattr(self, 'buildings'):
            for building in self.buildings:
                self._draw_building_image(building)
        
        # 自然地形画像を描画
        if hasattr(self, 'natural_features'):
            for feature in self.natural_features:
                self._draw_natural_feature_image(feature)
        
        print("🎨 マップサーフェス生成完了（画像使用版）")
    
    def _draw_building_image(self, building):
        """建物画像を描画（マップデータ使用版）"""
        try:
            pos = building['position']
            size = building['size']
            
            # マップデータから直接画像パスを取得
            if 'image_path' in building:
                image_path = building['image_path']
            elif 'sprite_path' in building:
                image_path = building['sprite_path']
            else:
                # フォールバック: 建物IDから推測
                building_id = building.get('id', '')
                if 'house' in building_id:
                    image_path = "buildings/house_residential.png"
                elif 'pet_shop' in building_id:
                    image_path = "buildings/house_petshop.png"
                else:
                    print(f"⚠️ 建物画像パス不明: {building}")
                    return
            
            # 画像を読み込み
            building_image = self.asset_manager.load_image(
                image_path, 
                (size['width'] * self.current_map.tile_size, size['height'] * self.current_map.tile_size)
            )
            
            if building_image:
                pos_x = pos['x'] * self.current_map.tile_size
                pos_y = pos['y'] * self.current_map.tile_size
                self.map_surface.blit(building_image, (pos_x, pos_y))
                print(f"🏠 建物画像描画: {building['name']} ({image_path})")
            else:
                print(f"⚠️ 建物画像未発見: {image_path}")
                
        except Exception as e:
            print(f"❌ 建物画像描画エラー: {e}")
    
    def _draw_natural_feature_image(self, feature):
        """自然地形画像を描画（サイズ調整版）"""
        try:
            pos = feature['position']
            size = feature['size']
            
            # サイズを建物と同じくらいに調整
            adjusted_width = min(size['width'], 4)  # 最大4タイル
            adjusted_height = min(size['height'], 3)  # 最大3タイル
            
            # マップデータから直接画像パスを取得
            if 'image_path' in feature:
                image_path = feature['image_path']
            elif 'sprite_path' in feature:
                image_path = feature['sprite_path']
            else:
                # フォールバック: 地形IDから推測
                feature_id = feature.get('id', '')
                if 'park' in feature_id:
                    image_path = "buildings/park_facility.png"
                else:
                    print(f"⚠️ 自然地形画像パス不明: {feature}")
                    return
            
            # 画像を読み込み（調整されたサイズで）
            feature_image = self.asset_manager.load_image(
                image_path,
                (adjusted_width * self.current_map.tile_size, adjusted_height * self.current_map.tile_size)
            )
            
            if feature_image:
                pos_x = pos['x'] * self.current_map.tile_size
                pos_y = pos['y'] * self.current_map.tile_size
                self.map_surface.blit(feature_image, (pos_x, pos_y))
                print(f"🌳 自然地形画像描画: {feature['name']} ({image_path}) - サイズ調整: {adjusted_width}x{adjusted_height}")
            else:
                print(f"⚠️ 自然地形画像未発見: {image_path}")
                
        except Exception as e:
            print(f"❌ 自然地形画像描画エラー: {e}")
    
    def draw(self, screen: pygame.Surface, camera_x: float, camera_y: float):
        """マップを描画"""
        if not self.map_surface:
            return
        
        # カメラ位置に基づいて描画範囲を計算
        screen_rect = screen.get_rect()
        
        # マップサーフェスから必要な部分を切り取って描画
        source_rect = pygame.Rect(
            int(camera_x),
            int(camera_y),
            screen_rect.width,
            screen_rect.height
        )
        
        # マップ境界内に制限
        map_rect = self.map_surface.get_rect()
        source_rect = source_rect.clip(map_rect)
        
        if source_rect.width > 0 and source_rect.height > 0:
            screen.blit(self.map_surface, (0, 0), source_rect)
    
    def get_tile_at_position(self, world_x: float, world_y: float) -> Optional[TileType]:
        """ワールド座標のタイルタイプを取得"""
        if not self.current_map:
            return None
        
        tile_x = int(world_x // self.tile_size)
        tile_y = int(world_y // self.tile_size)
        
        if (0 <= tile_x < self.current_map.width and 
            0 <= tile_y < self.current_map.height):
            return self.current_map.tiles[tile_y][tile_x]
        
        return None
    
    def is_walkable(self, world_x: float, world_y: float) -> bool:
        """指定位置が歩行可能かチェック"""
        tile_type = self.get_tile_at_position(world_x, world_y)
        if tile_type is None:
            return False
        
        tile_data = self.tile_definitions.get(tile_type)
        return tile_data.walkable if tile_data else True
    
    def check_collision(self, rect: pygame.Rect) -> bool:
        """矩形との衝突判定（マップ境界・建物チェック含む）"""
        if not self.current_map:
            return False
        
        # マップ境界チェック（正確な計算）
        map_width_pixels = self.current_map.width * self.current_map.tile_size
        map_height_pixels = self.current_map.height * self.current_map.tile_size
        
        # 境界チェック：キャラクターが完全にマップ内に収まるかチェック
        if (rect.left < 0 or 
            rect.top < 0 or 
            rect.right > map_width_pixels or 
            rect.bottom > map_height_pixels):
            # ペット用の境界チェックログは出力しない
            return True
        
        # 建物衝突チェック
        if self._check_building_collision(rect):
            return True
        
        # タイル衝突チェック（マップ内の場合のみ）
        corners = [
            (rect.left, rect.top),
            (rect.right - 1, rect.top),
            (rect.left, rect.bottom - 1),
            (rect.right - 1, rect.bottom - 1)
        ]
        
        for x, y in corners:
            if not self.is_walkable(x, y):
                return True
        
        return False
    
    def _check_building_collision(self, rect: pygame.Rect) -> bool:
        """建物・自然地形との衝突判定"""
        # 建物との衝突チェック
        if hasattr(self, 'buildings') and self.buildings:
            for building in self.buildings:
                # 建物の矩形を計算
                pos = building['position']
                size = building['size']
                
                building_rect = pygame.Rect(
                    pos['x'] * self.current_map.tile_size,
                    pos['y'] * self.current_map.tile_size,
                    size['width'] * self.current_map.tile_size,
                    size['height'] * self.current_map.tile_size
                )
                
                # 衝突判定
                if rect.colliderect(building_rect):
                    return True
        
        # 自然地形との衝突チェック（公園施設など）
        if hasattr(self, 'natural_features') and self.natural_features:
            for feature in self.natural_features:
                # 自然地形の矩形を計算
                pos = feature['position']
                size = feature['size']
                
                # サイズを建物と同じくらいに調整
                adjusted_width = min(size['width'], 4)  # 最大4タイル
                adjusted_height = min(size['height'], 3)  # 最大3タイル
                
                feature_rect = pygame.Rect(
                    pos['x'] * self.current_map.tile_size,
                    pos['y'] * self.current_map.tile_size,
                    adjusted_width * self.current_map.tile_size,
                    adjusted_height * self.current_map.tile_size
                )
                
                # 衝突判定
                if rect.colliderect(feature_rect):
                    return True
        
        return False
    
    def get_spawn_point(self, spawn_type: str) -> Optional[Tuple[int, int]]:
        """スポーン地点を取得"""
        if not self.current_map:
            return None
        
        spawn_point = self.current_map.spawn_points.get(spawn_type)
        if spawn_point:
            return (spawn_point[0] * self.tile_size, spawn_point[1] * self.tile_size)
        
        return None
    
    def get_pet_locations(self) -> List[Tuple[int, int]]:
        """ペット配置位置を取得"""
        if not self.current_map:
            return []
        
        locations = []
        for tile_x, tile_y in self.current_map.pet_locations:
            world_x = tile_x * self.tile_size
            world_y = tile_y * self.tile_size
            locations.append((world_x, world_y))
        
        return locations
    
    def get_map_size(self) -> Tuple[int, int]:
        """マップサイズ（ピクセル）を取得"""
        if not self.current_map:
            return (0, 0)
        
        return (
            self.current_map.width * self.tile_size,
            self.current_map.height * self.tile_size
        )
    
    def save_map(self, filename: str) -> bool:
        """現在のマップをファイルに保存"""
        if not self.current_map:
            return False
        
        try:
            map_data = {
                "width": self.current_map.width,
                "height": self.current_map.height,
                "tile_size": self.current_map.tile_size,
                "tiles": [[tile.value for tile in row] for row in self.current_map.tiles],
                "spawn_points": self.current_map.spawn_points,
                "pet_locations": self.current_map.pet_locations
            }
            
            map_path = Path("data/maps") / filename
            map_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(map_path, 'w', encoding='utf-8') as f:
                json.dump(map_data, f, ensure_ascii=False, indent=2)
            
            print(f"💾 マップ保存完了: {filename}")
            return True
            
        except Exception as e:
            print(f"❌ マップ保存エラー: {e}")
            return False
    
    def _update_from_new_map_data(self, new_map_data):
        """新しいマップデータからMapSystemを更新（画像使用版）"""
        try:
            from src.systems.map_data_loader import MapData as NewMapData
            
            print(f"🔄 MapSystemを新データで更新中...")
            
            # 新しいサイズでマップデータを作成
            width = new_map_data.dimensions.width
            height = new_map_data.dimensions.height
            
            # 基本は草タイルのマップ
            tiles = []
            for y in range(height):
                row = []
                for x in range(width):
                    row.append(TileType.GRASS)
                tiles.append(row)
            
            # 道路を配置（タイルとして）
            roads = new_map_data.terrain.get('roads', [])
            for road in roads:
                if road['type'] == 'main_road':
                    for point in road['points']:
                        start_y = point['y']
                        for road_y in range(start_y, min(start_y + road['width'], height)):
                            for x in range(width):
                                if 0 <= road_y < height:
                                    tiles[road_y][x] = TileType.CONCRETE
                elif road['type'] == 'side_road':
                    for point in road['points']:
                        start_x = point['x']
                        for road_x in range(start_x, min(start_x + road['width'], width)):
                            for y in range(height):
                                if 0 <= road_x < width:
                                    tiles[y][road_x] = TileType.CONCRETE
            
            # 新しいMapDataを作成（建物は別途描画）
            self.current_map = MapData(
                width=width,
                height=height,
                tile_size=self.tile_size,
                tiles=tiles,
                spawn_points={
                    'player': {'x': width//2, 'y': height-2},
                    'pets': [],
                    'npcs': []
                },
                pet_locations=[]
            )
            
            # 建物・自然地形情報を保存（画像描画用）
            self.buildings = new_map_data.terrain.get('buildings', [])
            self.natural_features = new_map_data.terrain.get('natural_features', [])
            
            print(f"🏠 建物情報保存: {len(self.buildings)}個")
            print(f"🌳 自然地形情報保存: {len(self.natural_features)}個")
            
            # マップサーフェスを再生成
            self._generate_map_surface()
            
            print(f"✅ MapSystem更新完了: {width}x{height}")
            return True
            
        except Exception as e:
            print(f"❌ MapSystem更新エラー: {e}")
            return False
