"""
タイルベース2Dマップシステム

JSONファイルからマップデータを読み込み、レイヤー対応の描画と衝突判定を提供
"""

import pygame
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass
from config.constants import *


class TileType(Enum):
    """タイルタイプ"""
    EMPTY = 0
    GROUND = 1
    WALL = 2
    WATER = 3
    GRASS = 4
    TREE = 5
    ROCK = 6
    DOOR = 7
    CHEST = 8
    DECORATION = 9


class LayerType(Enum):
    """レイヤータイプ"""
    BACKGROUND = "background"
    COLLISION = "collision"
    DECORATION = "decoration"
    FOREGROUND = "foreground"


@dataclass
class Tile:
    """タイル情報"""
    tile_id: int
    tile_type: TileType
    solid: bool = False
    sprite_x: int = 0
    sprite_y: int = 0


@dataclass
class MapLayer:
    """マップレイヤー"""
    name: str
    layer_type: LayerType
    width: int
    height: int
    data: List[List[int]]
    visible: bool = True
    opacity: float = 1.0


class TileSet:
    """タイルセット管理"""
    
    def __init__(self, tileset_path: str, tile_size: int = 32):
        self.tile_size = tile_size
        self.tiles: Dict[int, Tile] = {}
        self.sprite_sheet = None
        self.tileset_path = tileset_path
        
        # デバッグ用の色付きタイル作成
        self._create_debug_tiles()
    
    def _create_debug_tiles(self):
        """デバッグ用のカラータイルを作成"""
        # タイル定義
        tile_definitions = {
            0: (TileType.EMPTY, False, (0, 0, 0, 0)),           # 透明
            1: (TileType.GROUND, False, (139, 69, 19)),         # 茶色（地面）
            2: (TileType.WALL, True, (128, 128, 128)),          # 灰色（壁）
            3: (TileType.WATER, True, (0, 100, 200)),           # 青色（水）
            4: (TileType.GRASS, False, (34, 139, 34)),          # 緑色（草）
            5: (TileType.TREE, True, (0, 100, 0)),              # 濃緑（木）
            6: (TileType.ROCK, True, (105, 105, 105)),          # 暗灰色（岩）
            7: (TileType.DOOR, False, (160, 82, 45)),           # 茶色（ドア）
            8: (TileType.CHEST, True, (218, 165, 32)),          # 金色（宝箱）
            9: (TileType.DECORATION, False, (255, 192, 203))    # ピンク（装飾）
        }
        
        for tile_id, (tile_type, solid, color) in tile_definitions.items():
            self.tiles[tile_id] = Tile(
                tile_id=tile_id,
                tile_type=tile_type,
                solid=solid
            )
    
    def get_tile_sprite(self, tile_id: int) -> pygame.Surface:
        """タイルのスプライトを取得"""
        if tile_id not in self.tiles:
            return self._create_empty_tile()
        
        tile = self.tiles[tile_id]
        
        # デバッグ用カラータイル作成
        sprite = pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
        
        if tile.tile_type == TileType.EMPTY:
            return sprite  # 透明
        
        # タイプに応じた色
        colors = {
            TileType.GROUND: (139, 69, 19),
            TileType.WALL: (128, 128, 128),
            TileType.WATER: (0, 100, 200),
            TileType.GRASS: (34, 139, 34),
            TileType.TREE: (0, 100, 0),
            TileType.ROCK: (105, 105, 105),
            TileType.DOOR: (160, 82, 45),
            TileType.CHEST: (218, 165, 32),
            TileType.DECORATION: (255, 192, 203)
        }
        
        color = colors.get(tile.tile_type, (255, 255, 255))
        pygame.draw.rect(sprite, color, (0, 0, self.tile_size, self.tile_size))
        
        # 境界線
        pygame.draw.rect(sprite, (0, 0, 0), (0, 0, self.tile_size, self.tile_size), 1)
        
        # 衝突判定があるタイルにはXマーク
        if tile.solid:
            pygame.draw.line(sprite, (255, 0, 0), (2, 2), (self.tile_size-2, self.tile_size-2), 2)
            pygame.draw.line(sprite, (255, 0, 0), (self.tile_size-2, 2), (2, self.tile_size-2), 2)
        
        return sprite
    
    def _create_empty_tile(self) -> pygame.Surface:
        """空のタイルを作成"""
        return pygame.Surface((self.tile_size, self.tile_size), pygame.SRCALPHA)
    
    def is_solid(self, tile_id: int) -> bool:
        """タイルが衝突判定を持つかチェック"""
        if tile_id in self.tiles:
            return self.tiles[tile_id].solid
        return False


class Camera:
    """カメラシステム"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.x = 0.0
        self.y = 0.0
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.target_x = 0.0
        self.target_y = 0.0
        self.follow_speed = 5.0
        self.bounds = None  # (min_x, min_y, max_x, max_y)
    
    def set_target(self, x: float, y: float):
        """カメラのターゲット位置を設定"""
        self.target_x = x - self.screen_width // 2
        self.target_y = y - self.screen_height // 2
    
    def update(self, dt: float):
        """カメラ位置を更新"""
        # スムーズな追従
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        
        self.x += dx * self.follow_speed * dt
        self.y += dy * self.follow_speed * dt
        
        # 境界制限
        if self.bounds:
            min_x, min_y, max_x, max_y = self.bounds
            self.x = max(min_x, min(max_x - self.screen_width, self.x))
            self.y = max(min_y, min(max_y - self.screen_height, self.y))
    
    def set_bounds(self, min_x: int, min_y: int, max_x: int, max_y: int):
        """カメラの移動範囲を設定"""
        self.bounds = (min_x, min_y, max_x, max_y)
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """ワールド座標をスクリーン座標に変換"""
        return (world_x - self.x, world_y - self.y)
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """スクリーン座標をワールド座標に変換"""
        return (screen_x + self.x, screen_y + self.y)


class MapSystem:
    """タイルベース2Dマップシステム"""
    
    def __init__(self, tile_size: int = 32):
        self.tile_size = tile_size
        self.layers: List[MapLayer] = []
        self.tileset: Optional[TileSet] = None
        self.width = 0
        self.height = 0
        self.camera = Camera(SCREEN_WIDTH, SCREEN_HEIGHT)
        
        # キャッシュ
        self._sprite_cache: Dict[int, pygame.Surface] = {}
    
    def load_from_json(self, map_file_path: str, tileset_path: str = None) -> bool:
        """JSONファイルからマップデータを読み込み"""
        try:
            with open(map_file_path, 'r', encoding='utf-8') as f:
                map_data = json.load(f)
            
            # タイルセット読み込み
            if tileset_path:
                self.tileset = TileSet(tileset_path, self.tile_size)
            else:
                self.tileset = TileSet("", self.tile_size)
            
            # マップサイズ
            self.width = map_data.get('width', 0)
            self.height = map_data.get('height', 0)
            
            # レイヤー読み込み
            self.layers.clear()
            for layer_data in map_data.get('layers', []):
                layer = self._parse_layer(layer_data)
                if layer:
                    self.layers.append(layer)
            
            # カメラ境界設定
            self.camera.set_bounds(
                0, 0,
                self.width * self.tile_size,
                self.height * self.tile_size
            )
            
            return True
            
        except Exception as e:
            print(f"マップ読み込みエラー: {e}")
            return False
    
    def _parse_layer(self, layer_data: Dict[str, Any]) -> Optional[MapLayer]:
        """レイヤーデータを解析"""
        try:
            name = layer_data.get('name', 'unknown')
            layer_type_str = layer_data.get('type', 'background')
            
            # レイヤータイプの決定
            layer_type = LayerType.BACKGROUND
            if 'collision' in name.lower() or layer_type_str == 'collision':
                layer_type = LayerType.COLLISION
            elif 'decoration' in name.lower() or layer_type_str == 'decoration':
                layer_type = LayerType.DECORATION
            elif 'foreground' in name.lower() or layer_type_str == 'foreground':
                layer_type = LayerType.FOREGROUND
            
            width = layer_data.get('width', self.width)
            height = layer_data.get('height', self.height)
            
            # データ形式の処理
            raw_data = layer_data.get('data', [])
            if isinstance(raw_data, list) and len(raw_data) > 0:
                if isinstance(raw_data[0], list):
                    # 2次元配列
                    data = raw_data
                else:
                    # 1次元配列を2次元に変換
                    data = []
                    for y in range(height):
                        row = []
                        for x in range(width):
                            index = y * width + x
                            if index < len(raw_data):
                                row.append(raw_data[index])
                            else:
                                row.append(0)
                        data.append(row)
            else:
                # 空のデータ
                data = [[0 for _ in range(width)] for _ in range(height)]
            
            return MapLayer(
                name=name,
                layer_type=layer_type,
                width=width,
                height=height,
                data=data,
                visible=layer_data.get('visible', True),
                opacity=layer_data.get('opacity', 1.0)
            )
            
        except Exception as e:
            print(f"レイヤー解析エラー: {e}")
            return None
    
    def create_sample_map(self):
        """サンプルマップを作成"""
        self.width = 20
        self.height = 15
        self.tileset = TileSet("", self.tile_size)
        
        # 背景レイヤー（草地）
        background_data = [[4 for _ in range(self.width)] for _ in range(self.height)]
        background_layer = MapLayer(
            name="background",
            layer_type=LayerType.BACKGROUND,
            width=self.width,
            height=self.height,
            data=background_data
        )
        
        # 衝突レイヤー（壁と障害物）
        collision_data = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # 外周に壁
        for x in range(self.width):
            collision_data[0][x] = 2  # 上の壁
            collision_data[self.height-1][x] = 2  # 下の壁
        for y in range(self.height):
            collision_data[y][0] = 2  # 左の壁
            collision_data[y][self.width-1] = 2  # 右の壁
        
        # 内部に障害物
        collision_data[5][5] = 5  # 木
        collision_data[5][6] = 5  # 木
        collision_data[8][10] = 6  # 岩
        collision_data[10][8] = 8  # 宝箱
        
        collision_layer = MapLayer(
            name="collision",
            layer_type=LayerType.COLLISION,
            width=self.width,
            height=self.height,
            data=collision_data
        )
        
        # 装飾レイヤー
        decoration_data = [[0 for _ in range(self.width)] for _ in range(self.height)]
        decoration_data[3][3] = 9  # 装飾
        decoration_data[12][15] = 9  # 装飾
        
        decoration_layer = MapLayer(
            name="decoration",
            layer_type=LayerType.DECORATION,
            width=self.width,
            height=self.height,
            data=decoration_data
        )
        
        self.layers = [background_layer, collision_layer, decoration_layer]
        
        # カメラ境界設定
        self.camera.set_bounds(
            0, 0,
            self.width * self.tile_size,
            self.height * self.tile_size
        )
    
    def update(self, dt: float):
        """マップシステムを更新"""
        self.camera.update(dt)
    
    def render(self, screen: pygame.Surface):
        """マップを描画"""
        if not self.tileset:
            return
        
        # 描画範囲の計算
        start_x = max(0, int(self.camera.x // self.tile_size))
        start_y = max(0, int(self.camera.y // self.tile_size))
        end_x = min(self.width, int((self.camera.x + SCREEN_WIDTH) // self.tile_size) + 1)
        end_y = min(self.height, int((self.camera.y + SCREEN_HEIGHT) // self.tile_size) + 1)
        
        # レイヤー順で描画
        layer_order = [LayerType.BACKGROUND, LayerType.COLLISION, LayerType.DECORATION, LayerType.FOREGROUND]
        
        for layer_type in layer_order:
            for layer in self.layers:
                if layer.layer_type == layer_type and layer.visible:
                    self._render_layer(screen, layer, start_x, start_y, end_x, end_y)
    
    def _render_layer(self, screen: pygame.Surface, layer: MapLayer, 
                     start_x: int, start_y: int, end_x: int, end_y: int):
        """レイヤーを描画"""
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                if y < len(layer.data) and x < len(layer.data[y]):
                    tile_id = layer.data[y][x]
                    if tile_id > 0:  # 空タイル以外
                        sprite = self._get_tile_sprite(tile_id)
                        if sprite:
                            screen_x, screen_y = self.camera.world_to_screen(
                                x * self.tile_size, y * self.tile_size
                            )
                            
                            # 透明度適用
                            if layer.opacity < 1.0:
                                sprite = sprite.copy()
                                sprite.set_alpha(int(255 * layer.opacity))
                            
                            screen.blit(sprite, (screen_x, screen_y))
    
    def _get_tile_sprite(self, tile_id: int) -> pygame.Surface:
        """タイルスプライトを取得（キャッシュ付き）"""
        if tile_id not in self._sprite_cache:
            self._sprite_cache[tile_id] = self.tileset.get_tile_sprite(tile_id)
        return self._sprite_cache[tile_id]
    
    def check_collision(self, x: float, y: float, width: float, height: float) -> bool:
        """矩形との衝突判定"""
        if not self.tileset:
            return False
        
        # 矩形の角の座標をタイル座標に変換
        left = int(x // self.tile_size)
        right = int((x + width - 1) // self.tile_size)
        top = int(y // self.tile_size)
        bottom = int((y + height - 1) // self.tile_size)
        
        # 衝突レイヤーをチェック
        for layer in self.layers:
            if layer.layer_type == LayerType.COLLISION:
                for ty in range(max(0, top), min(layer.height, bottom + 1)):
                    for tx in range(max(0, left), min(layer.width, right + 1)):
                        if ty < len(layer.data) and tx < len(layer.data[ty]):
                            tile_id = layer.data[ty][tx]
                            if tile_id > 0 and self.tileset.is_solid(tile_id):
                                return True
        
        return False
    
    def get_tile_at(self, x: float, y: float, layer_type: LayerType = LayerType.COLLISION) -> int:
        """指定座標のタイルIDを取得"""
        tile_x = int(x // self.tile_size)
        tile_y = int(y // self.tile_size)
        
        for layer in self.layers:
            if layer.layer_type == layer_type:
                if (0 <= tile_y < layer.height and 0 <= tile_x < layer.width and
                    tile_y < len(layer.data) and tile_x < len(layer.data[tile_y])):
                    return layer.data[tile_y][tile_x]
        
        return 0
    
    def set_camera_target(self, x: float, y: float):
        """カメラのターゲットを設定"""
        self.camera.set_target(x, y)
    
    def world_to_screen(self, world_x: float, world_y: float) -> Tuple[float, float]:
        """ワールド座標をスクリーン座標に変換"""
        return self.camera.world_to_screen(world_x, world_y)
    
    def screen_to_world(self, screen_x: float, screen_y: float) -> Tuple[float, float]:
        """スクリーン座標をワールド座標に変換"""
        return self.camera.screen_to_world(screen_x, screen_y)
    
    def get_map_size(self) -> Tuple[int, int]:
        """マップサイズを取得（ピクセル単位）"""
        return (self.width * self.tile_size, self.height * self.tile_size)
    
    def get_tile_size(self) -> int:
        """タイルサイズを取得"""
        return self.tile_size
