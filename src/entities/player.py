"""
プレイヤーエンティティ
プレイヤーキャラクターの管理
"""

import pygame
from typing import Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

from src.utils.asset_manager import get_asset_manager

class Direction(Enum):
    """移動方向"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"

@dataclass
class PlayerStats:
    """プレイヤー統計"""
    health: int = 100
    max_health: int = 100
    stamina: int = 100
    max_stamina: int = 100
    speed: float = 200.0  # ピクセル/秒
    run_speed: float = 350.0

class Player:
    """プレイヤークラス"""
    
    def __init__(self, x: float = 400, y: float = 300):
        # 位置
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 64, 64)  # スプライトサイズに合わせて調整
        
        # 移動
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.direction = Direction.DOWN
        self.is_moving = False
        self.is_running = False
        
        # 統計
        self.stats = PlayerStats()
        
        # アニメーション
        self.animation_timer = 0.0
        self.animation_frame = 0
        
        # スプライト
        self.asset_manager = get_asset_manager()
        self.sprites = self._load_sprites()
        
        # 描画用の色（スプライトがない場合のフォールバック）
        self.color = (0, 100, 200)
        
        print("👤 プレイヤー初期化完了")
    
    def _load_sprites(self) -> Dict[str, pygame.Surface]:
        """プレイヤースプライトを読み込み"""
        sprites = {}
        directions = {
            Direction.UP: "back",
            Direction.DOWN: "front", 
            Direction.LEFT: "left",
            Direction.RIGHT: "right"
        }
        
        for direction, sprite_name in directions.items():
            sprite_path = f"characters/player_{sprite_name}.png"
            sprite = self.asset_manager.load_image(sprite_path, (64, 64))
            if sprite:
                sprites[direction] = sprite
                print(f"✅ プレイヤースプライト読み込み: {sprite_name}")
            else:
                print(f"⚠️ プレイヤースプライト読み込み失敗: {sprite_name}")
        
        return sprites
    
    def update(self, time_delta: float, keys_pressed: pygame.key.ScancodeWrapper, map_system=None):
        """
        プレイヤーを更新
        
        Args:
            time_delta: フレーム時間（秒）
            keys_pressed: pygame.key.get_pressed()の戻り値
            map_system: マップシステム（衝突判定用、オプション）
        """
        # Phase 1: 基本入力処理
        self._handle_input(keys_pressed)
        
        # Phase 2: 移動処理
        self._update_movement(time_delta, map_system)
        
        # Phase 3: 状態更新
        self._update_stamina(time_delta)
        self._update_animation(time_delta)
    
    def _handle_input(self, keys_pressed: pygame.key.ScancodeWrapper):
        """
        入力処理 - Phase 1: 基本移動のみ
        
        Args:
            keys_pressed: pygame.key.get_pressed()の戻り値
        """
        """
        入力処理 - デモと同じ機能を全て実装
        
        Args:
            keys_pressed: pygame.key.get_pressed()の戻り値
        """
        # 移動入力をリセット
        self.velocity_x = 0
        self.velocity_y = 0
        self.is_moving = False
        
        # 走行判定（デモと同じ）
        self.is_running = keys_pressed[pygame.K_LSHIFT] and self.stats.stamina > 0
        
        # 移動速度決定（デモと同じ）
        speed = self.stats.run_speed if self.is_running else self.stats.speed
        
        # WASD + 矢印キー対応（デモと同じ）
        if keys_pressed[pygame.K_a] or keys_pressed[pygame.K_LEFT]:
            self.velocity_x = -speed
            self.direction = Direction.LEFT
            self.is_moving = True
        
        if keys_pressed[pygame.K_d] or keys_pressed[pygame.K_RIGHT]:
            self.velocity_x = speed
            self.direction = Direction.RIGHT
            self.is_moving = True
        
        if keys_pressed[pygame.K_w] or keys_pressed[pygame.K_UP]:
            self.velocity_y = -speed
            self.direction = Direction.UP
            self.is_moving = True
        
        if keys_pressed[pygame.K_s] or keys_pressed[pygame.K_DOWN]:
            self.velocity_y = speed
            self.direction = Direction.DOWN
            self.is_moving = True
        
        # 斜め移動の速度調整（デモと同じ）
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x *= 0.707  # 1/√2
            self.velocity_y *= 0.707
        
        # 斜め移動の速度調整
        if self.velocity_x != 0 and self.velocity_y != 0:
            self.velocity_x *= 0.707  # 1/√2
            self.velocity_y *= 0.707
    
    def _update_movement(self, time_delta: float, map_system=None):
        """移動更新（建物衝突判定付き）"""
        # 移動前の位置を保存
        old_x = self.x
        old_y = self.y
        
        # 新しい位置を計算
        new_x = self.x + self.velocity_x * time_delta
        new_y = self.y + self.velocity_y * time_delta
        
        if map_system:
            # X軸移動をチェック
            test_rect_x = pygame.Rect(new_x, self.y, self.rect.width, self.rect.height)
            if not map_system.check_collision(test_rect_x):
                self.x = new_x
            else:
                # 建物や障害物に衝突した場合は移動を停止
                self.velocity_x = 0
            
            # Y軸移動をチェック
            test_rect_y = pygame.Rect(self.x, new_y, self.rect.width, self.rect.height)
            if not map_system.check_collision(test_rect_y):
                self.y = new_y
            else:
                # 建物や障害物に衝突した場合は移動を停止
                self.velocity_y = 0
        else:
            # フォールバック: 境界チェックのみ
            MAP_WIDTH = 2560
            MAP_HEIGHT = 1920
            self.x = max(0, min(new_x, MAP_WIDTH - self.rect.width))
            self.y = max(0, min(new_y, MAP_HEIGHT - self.rect.height))
            print("⚠️ フォールバック境界チェック使用")
        
        # 矩形位置を更新
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def _update_stamina(self, time_delta: float):
        """スタミナ更新"""
        if self.is_running and self.is_moving:
            # スタミナ消費
            self.stats.stamina -= 30 * time_delta
            self.stats.stamina = max(0, self.stats.stamina)
        else:
            # スタミナ回復
            self.stats.stamina += 20 * time_delta
            self.stats.stamina = min(self.stats.max_stamina, self.stats.stamina)
    
    def _update_animation(self, time_delta: float):
        """アニメーション更新"""
        if self.is_moving:
            self.animation_timer += time_delta
            if self.animation_timer >= 0.2:  # 0.2秒ごとにフレーム変更
                self.animation_frame = (self.animation_frame + 1) % 4
                self.animation_timer = 0.0
        else:
            self.animation_frame = 0
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理（プレイヤー固有のイベント）"""
        # 現在は特別なイベント処理は不要
        # 将来的にアイテム使用やスキル発動などを追加可能
        pass
    
    def draw(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """プレイヤーを描画"""
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]
        
        # スプライト描画（透明度を保持）
        if self.direction in self.sprites:
            sprite = self.sprites[self.direction]
            # 画像をそのまま描画（透明度保持）
            screen.blit(sprite, (draw_x, draw_y))
        else:
            # フォールバック: 矩形描画
            pygame.draw.rect(screen, self.color, (draw_x, draw_y, self.rect.width, self.rect.height))
            
            # 方向インジケーター
            center_x = draw_x + self.rect.width // 2
            center_y = draw_y + self.rect.height // 2
            
            if self.direction == Direction.UP:
                pygame.draw.polygon(screen, (255, 255, 255), 
                                  [(center_x, draw_y), (center_x - 5, draw_y + 10), (center_x + 5, draw_y + 10)])
            elif self.direction == Direction.DOWN:
                pygame.draw.polygon(screen, (255, 255, 255), 
                                  [(center_x, draw_y + self.rect.height), (center_x - 5, draw_y + self.rect.height - 10), 
                                   (center_x + 5, draw_y + self.rect.height - 10)])
            elif self.direction == Direction.LEFT:
                pygame.draw.polygon(screen, (255, 255, 255), 
                                  [(draw_x, center_y), (draw_x + 10, center_y - 5), (draw_x + 10, center_y + 5)])
            elif self.direction == Direction.RIGHT:
                pygame.draw.polygon(screen, (255, 255, 255), 
                                  [(draw_x + self.rect.width, center_y), (draw_x + self.rect.width - 10, center_y - 5), 
                                   (draw_x + self.rect.width - 10, center_y + 5)])
        
        # スタミナバー（走行中のみ表示）
        if self.is_running or self.stats.stamina < self.stats.max_stamina:
            self._draw_stamina_bar(screen, draw_x, draw_y)
    
    def _draw_stamina_bar(self, screen: pygame.Surface, x: int, y: int):
        """スタミナバーを描画"""
        bar_width = self.rect.width
        bar_height = 4
        bar_y = y - 8
        
        # 背景
        pygame.draw.rect(screen, (100, 100, 100), (x, bar_y, bar_width, bar_height))
        
        # スタミナ
        stamina_ratio = self.stats.stamina / self.stats.max_stamina
        stamina_width = int(bar_width * stamina_ratio)
        stamina_color = (255, 255, 0) if stamina_ratio > 0.3 else (255, 100, 100)
        pygame.draw.rect(screen, stamina_color, (x, bar_y, stamina_width, bar_height))
    
    def get_position(self) -> Tuple[float, float]:
        """位置を取得"""
        return (self.x, self.y)
    
    def set_position(self, x: float, y: float):
        """位置を設定"""
        self.x = x
        self.y = y
        self.rect.x = int(x)
        self.rect.y = int(y)
    
    def get_stats(self) -> PlayerStats:
        """統計を取得"""
        return self.stats
    
    def get_center(self) -> Tuple[float, float]:
        """中心位置を取得"""
        return (self.x + self.rect.width // 2, self.y + self.rect.height // 2)
