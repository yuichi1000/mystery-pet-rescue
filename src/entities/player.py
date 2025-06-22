"""
プレイヤークラス

プレイヤーキャラクターを管理
"""

import pygame
import math
from typing import Tuple, Dict, Set
from enum import Enum
from config.constants import *


class AnimationState(Enum):
    """アニメーション状態"""
    IDLE = "idle"
    WALKING = "walking"
    RUNNING = "running"


class Direction(Enum):
    """移動方向"""
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"
    UP_LEFT = "up_left"
    UP_RIGHT = "up_right"
    DOWN_LEFT = "down_left"
    DOWN_RIGHT = "down_right"


class Player:
    """プレイヤークラス"""
    
    def __init__(self, x: int, y: int):
        """
        プレイヤーを初期化
        
        Args:
            x: 初期X座標
            y: 初期Y座標
        """
        # 位置と移動
        self.x = float(x)
        self.y = float(y)
        self.base_speed = PLAYER_SPEED
        self.current_speed = self.base_speed
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        
        # 移動状態
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.is_moving = False
        self.direction = Direction.DOWN
        self.last_direction = Direction.DOWN
        
        # アニメーション状態
        self.animation_state = AnimationState.IDLE
        self.animation_frame = 0
        self.animation_timer = 0.0
        self.animation_speed = 0.15  # 秒単位
        self.max_frames = {
            AnimationState.IDLE: 4,
            AnimationState.WALKING: 8,
            AnimationState.RUNNING: 6
        }
        
        # スプライト管理
        self.sprites: Dict[str, pygame.Surface] = {}
        self.current_sprite = None
        self.sprite_flip_x = False
        self.sprite_flip_y = False
        
        # 当たり判定
        self.rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
        self.collision_rect = pygame.Rect(
            int(self.x) + 8, int(self.y) + 16, 
            self.width - 16, self.height - 16
        )
        
        # ゲーム状態
        self.health = 100
        self.max_health = 100
        self.energy = 100
        self.max_energy = 100
        self.stamina = 100
        self.max_stamina = 100
        
        # インベントリ
        self.inventory = []
        self.max_inventory_size = 10
        
        # 統計
        self.pets_rescued = 0
        self.distance_walked = 0.0
        self.play_time = 0.0
        
        # デバッグ用の仮スプライト作成
        self._create_debug_sprites()
    
    
    def _create_debug_sprites(self):
        """デバッグ用の仮スプライトを作成"""
        # 各方向・状態用の色付き矩形スプライトを作成
        colors = {
            AnimationState.IDLE: COLOR_BLUE,
            AnimationState.WALKING: COLOR_GREEN,
            AnimationState.RUNNING: COLOR_RED
        }
        
        for state in AnimationState:
            for direction in Direction:
                for frame in range(self.max_frames[state]):
                    sprite_key = f"{state.value}_{direction.value}_{frame}"
                    sprite = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                    
                    # 基本色
                    base_color = colors[state]
                    
                    # フレームによる明度変化
                    brightness = 0.8 + 0.2 * math.sin(frame * math.pi / 4)
                    color = tuple(int(c * brightness) for c in base_color)
                    
                    # 矩形描画
                    pygame.draw.rect(sprite, color, (0, 0, self.width, self.height))
                    pygame.draw.rect(sprite, COLOR_WHITE, (0, 0, self.width, self.height), 2)
                    
                    # 方向を示す矢印
                    self._draw_direction_arrow(sprite, direction)
                    
                    self.sprites[sprite_key] = sprite
        
        # 初期スプライト設定
        self.current_sprite = self.sprites[f"{self.animation_state.value}_{self.direction.value}_0"]
    
    def _draw_direction_arrow(self, sprite: pygame.Surface, direction: Direction):
        """スプライトに方向を示す矢印を描画"""
        center_x = self.width // 2
        center_y = self.height // 2
        arrow_size = 8
        
        # 方向に応じた矢印の描画
        if direction == Direction.UP:
            points = [(center_x, center_y - arrow_size), 
                     (center_x - 4, center_y), 
                     (center_x + 4, center_y)]
        elif direction == Direction.DOWN:
            points = [(center_x, center_y + arrow_size), 
                     (center_x - 4, center_y), 
                     (center_x + 4, center_y)]
        elif direction == Direction.LEFT:
            points = [(center_x - arrow_size, center_y), 
                     (center_x, center_y - 4), 
                     (center_x, center_y + 4)]
        elif direction == Direction.RIGHT:
            points = [(center_x + arrow_size, center_y), 
                     (center_x, center_y - 4), 
                     (center_x, center_y + 4)]
        elif direction == Direction.UP_LEFT:
            points = [(center_x - 6, center_y - 6), 
                     (center_x - 2, center_y - 2), 
                     (center_x - 6, center_y - 2)]
        elif direction == Direction.UP_RIGHT:
            points = [(center_x + 6, center_y - 6), 
                     (center_x + 2, center_y - 2), 
                     (center_x + 6, center_y - 2)]
        elif direction == Direction.DOWN_LEFT:
            points = [(center_x - 6, center_y + 6), 
                     (center_x - 2, center_y + 2), 
                     (center_x - 6, center_y + 2)]
        elif direction == Direction.DOWN_RIGHT:
            points = [(center_x + 6, center_y + 6), 
                     (center_x + 2, center_y + 2), 
                     (center_x + 6, center_y + 2)]
        
        pygame.draw.polygon(sprite, COLOR_WHITE, points)
    
    def update(self, dt: float, input_handler, map_system=None):
        """
        プレイヤーを更新
        
        Args:
            dt: デルタタイム（秒）
            input_handler: 入力ハンドラー
            map_system: マップシステム（衝突判定用）
        """
        # 入力処理
        self._handle_input(input_handler)
        
        # 移動処理（マップ衝突判定付き）
        self._update_movement(dt, map_system)
        
        # アニメーション更新
        self._update_animation(dt)
        
        # 当たり判定更新
        self._update_collision_rects()
        
        # 統計更新
        self._update_stats(dt)
    
    def _handle_input(self, input_handler):
        """入力処理"""
        # 移動入力の取得
        move_x = 0
        move_y = 0
        
        # 直接pygame.key.get_pressed()を使用（最も確実）
        keys = pygame.key.get_pressed()
        
        # WASD / 矢印キー入力
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            move_x -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            move_x += 1
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            move_y -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            move_y += 1
        
        # 走行状態の判定（Shiftキー）
        running = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        
        # 移動ベクトルの正規化（8方向移動対応）
        if move_x != 0 or move_y != 0:
            # 速度とアニメーション状態の更新
            if running and self.stamina > 0:
                self.current_speed = self.base_speed * 1.5
                self.animation_state = AnimationState.RUNNING
                self.stamina -= 20 * (1/60)  # スタミナ消費
            else:
                self.current_speed = self.base_speed
                self.animation_state = AnimationState.WALKING
            
            # 斜め移動の場合は速度を調整
            if move_x != 0 and move_y != 0:
                move_x *= 0.707  # 1/√2
                move_y *= 0.707
            
            self.velocity_x = move_x * self.current_speed
            self.velocity_y = move_y * self.current_speed
            self.is_moving = True
            
            # 方向の決定
            self._update_direction(move_x, move_y)
        else:
            self.velocity_x = 0
            self.velocity_y = 0
            self.is_moving = False
            self.animation_state = AnimationState.IDLE
            # スタミナ回復
            self.stamina = min(self.max_stamina, self.stamina + 10 * (1/60))
    
    def _update_direction(self, move_x: float, move_y: float):
        """移動方向を更新"""
        # 8方向の判定
        if move_x > 0 and move_y < 0:
            self.direction = Direction.UP_RIGHT
        elif move_x > 0 and move_y > 0:
            self.direction = Direction.DOWN_RIGHT
        elif move_x < 0 and move_y < 0:
            self.direction = Direction.UP_LEFT
        elif move_x < 0 and move_y > 0:
            self.direction = Direction.DOWN_LEFT
        elif move_x > 0:
            self.direction = Direction.RIGHT
        elif move_x < 0:
            self.direction = Direction.LEFT
        elif move_y < 0:
            self.direction = Direction.UP
        elif move_y > 0:
            self.direction = Direction.DOWN
        
        # 移動中の場合は最後の方向を記録
        if self.is_moving:
            self.last_direction = self.direction
    
    def _update_movement(self, dt: float, map_system=None):
        """移動処理"""
        if self.is_moving:
            # 新しい位置を計算
            new_x = self.x + self.velocity_x * dt
            new_y = self.y + self.velocity_y * dt
            
            # マップ衝突判定
            if map_system:
                # X軸移動チェック
                if not map_system.check_collision(new_x, self.y, self.width, self.height):
                    # 移動距離を記録
                    distance = abs(new_x - self.x)
                    self.distance_walked += distance
                    self.x = new_x
                
                # Y軸移動チェック
                if not map_system.check_collision(self.x, new_y, self.width, self.height):
                    # 移動距離を記録
                    distance = abs(new_y - self.y)
                    self.distance_walked += distance
                    self.y = new_y
            else:
                # 画面境界チェック（マップシステムがない場合）
                new_x = max(0, min(SCREEN_WIDTH - self.width, new_x))
                new_y = max(0, min(SCREEN_HEIGHT - self.height, new_y))
                
                # 移動距離を記録
                distance = math.sqrt((new_x - self.x)**2 + (new_y - self.y)**2)
                self.distance_walked += distance
                
                # 位置更新
                self.x = new_x
                self.y = new_y
    
    def _update_animation(self, dt: float):
        """アニメーション更新"""
        self.animation_timer += dt
        
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            
            # フレーム更新
            max_frame = self.max_frames[self.animation_state]
            self.animation_frame = (self.animation_frame + 1) % max_frame
        
        # 現在のスプライトを更新
        sprite_key = f"{self.animation_state.value}_{self.direction.value}_{self.animation_frame}"
        if sprite_key in self.sprites:
            self.current_sprite = self.sprites[sprite_key]
    
    def _update_collision_rects(self):
        """当たり判定矩形を更新"""
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
        
        # 衝突判定用の矩形（少し小さめ）
        self.collision_rect.x = int(self.x) + 8
        self.collision_rect.y = int(self.y) + 16
    
    def _update_stats(self, dt: float):
        """統計情報を更新"""
        self.play_time += dt
        
        # エネルギー自然回復
        if not self.is_moving:
            self.energy = min(self.max_energy, self.energy + 5 * dt)
    
    def render(self, screen: pygame.Surface):
        """プレイヤーを描画"""
        if self.current_sprite:
            # スプライト描画
            sprite_rect = self.current_sprite.get_rect()
            sprite_rect.center = (int(self.x + self.width // 2), int(self.y + self.height // 2))
            
            if self.sprite_flip_x or self.sprite_flip_y:
                flipped_sprite = pygame.transform.flip(self.current_sprite, self.sprite_flip_x, self.sprite_flip_y)
                screen.blit(flipped_sprite, sprite_rect)
            else:
                screen.blit(self.current_sprite, sprite_rect)
        else:
            # フォールバック描画
            pygame.draw.rect(screen, COLOR_BLUE, self.rect)
            pygame.draw.rect(screen, COLOR_WHITE, self.rect, 2)
    
    def render_debug(self, screen: pygame.Surface):
        """デバッグ情報を描画"""
        # 当たり判定矩形
        pygame.draw.rect(screen, COLOR_RED, self.rect, 1)
        pygame.draw.rect(screen, COLOR_YELLOW, self.collision_rect, 1)
        
        # 移動ベクトル
        if self.is_moving:
            start_pos = (int(self.x + self.width // 2), int(self.y + self.height // 2))
            end_pos = (int(start_pos[0] + self.velocity_x * 0.1), 
                      int(start_pos[1] + self.velocity_y * 0.1))
            pygame.draw.line(screen, COLOR_GREEN, start_pos, end_pos, 2)
    
    def get_position(self) -> Tuple[float, float]:
        """位置を取得"""
        return (self.x, self.y)
    
    def set_position(self, x: float, y: float):
        """位置を設定"""
        self.x = x
        self.y = y
        self._update_collision_rects()
    
    def get_center(self) -> Tuple[float, float]:
        """中心座標を取得"""
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def set_speed(self, speed: float):
        """移動速度を設定"""
        self.base_speed = speed
        if not self.is_moving or self.animation_state != AnimationState.RUNNING:
            self.current_speed = speed
    
    def load_sprites(self, sprite_sheet_path: str):
        """スプライトシートから画像を読み込み"""
        # TODO: 実際のスプライトシート読み込み実装
        # 現在はデバッグ用スプライトを使用
        pass
    
    def check_collision(self, rect: pygame.Rect) -> bool:
        """他のオブジェクトとの衝突判定"""
        return self.collision_rect.colliderect(rect)
    
    def add_to_inventory(self, item) -> bool:
        """アイテムをインベントリに追加"""
        if len(self.inventory) < self.max_inventory_size:
            self.inventory.append(item)
            return True
        return False
    
    def remove_from_inventory(self, item) -> bool:
        """アイテムをインベントリから削除"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def heal(self, amount: int):
        """体力を回復"""
        self.health = min(self.max_health, self.health + amount)
    
    def restore_energy(self, amount: int):
        """エネルギーを回復"""
        self.energy = min(self.max_energy, self.energy + amount)
    
    def rescue_pet(self):
        """ペット救助数を増加"""
        self.pets_rescued += 1
    
    def get_stats(self) -> Dict[str, any]:
        """プレイヤー統計を取得"""
        return {
            "position": (self.x, self.y),
            "health": self.health,
            "energy": self.energy,
            "stamina": self.stamina,
            "pets_rescued": self.pets_rescued,
            "distance_walked": self.distance_walked,
            "play_time": self.play_time,
            "is_moving": self.is_moving,
            "direction": self.direction.value,
            "animation_state": self.animation_state.value,
            "current_speed": self.current_speed
        }
