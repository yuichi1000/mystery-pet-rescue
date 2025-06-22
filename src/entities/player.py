"""
プレイヤークラス

プレイヤーキャラクターを管理
"""

import pygame
from typing import Tuple
from config.constants import *


class Player:
    """プレイヤークラス"""
    
    def __init__(self, x: int, y: int):
        """
        プレイヤーを初期化
        
        Args:
            x: 初期X座標
            y: 初期Y座標
        """
        self.x = x
        self.y = y
        self.speed = PLAYER_SPEED
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        
        # 移動状態
        self.moving = False
        self.direction = "down"  # up, down, left, right
        
        # アニメーション
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 10  # フレーム数
        
        # 当たり判定
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # インベントリ
        self.inventory = []
        self.max_inventory_size = 10
        
        # ステータス
        self.health = 100
        self.max_health = 100
        self.energy = 100
        self.max_energy = 100
        
        # 統計
        self.pets_rescued = 0
        self.distance_walked = 0.0
        self.play_time = 0.0
    
    def update(self, input_handler):
        """プレイヤーを更新"""
        # 移動処理
        self._handle_movement(input_handler)
        
        # アニメーション更新
        self._update_animation()
        
        # 当たり判定更新
        self.rect.x = self.x
        self.rect.y = self.y
    
    def _handle_movement(self, input_handler):
        """移動処理"""
        # 移動ベクトルを取得
        dx, dy = input_handler.get_movement_vector()
        
        if dx != 0 or dy != 0:
            self.moving = True
            
            # 方向を更新
            if dx > 0:
                self.direction = "right"
            elif dx < 0:
                self.direction = "left"
            elif dy > 0:
                self.direction = "down"
            elif dy < 0:
                self.direction = "up"
            
            # 位置を更新
            new_x = self.x + dx * self.speed
            new_y = self.y + dy * self.speed
            
            # 画面境界チェック
            if 0 <= new_x <= SCREEN_WIDTH - self.width:
                self.x = new_x
            if 0 <= new_y <= SCREEN_HEIGHT - self.height:
                self.y = new_y
            
            # 歩行距離を更新
            self.distance_walked += self.speed * 0.1  # 適当な係数
        else:
            self.moving = False
    
    def _update_animation(self):
        """アニメーション更新"""
        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4
        else:
            self.animation_frame = 0
    
    def render(self, screen: pygame.Surface):
        """プレイヤーを描画"""
        # 仮の描画（四角形）
        color = COLOR_BLUE
        pygame.draw.rect(screen, color, self.rect)
        
        # 方向を示す矢印
        center_x = self.rect.centerx
        center_y = self.rect.centery
        
        if self.direction == "up":
            pygame.draw.polygon(screen, COLOR_WHITE, [
                (center_x, center_y - 8),
                (center_x - 4, center_y),
                (center_x + 4, center_y)
            ])
        elif self.direction == "down":
            pygame.draw.polygon(screen, COLOR_WHITE, [
                (center_x, center_y + 8),
                (center_x - 4, center_y),
                (center_x + 4, center_y)
            ])
        elif self.direction == "left":
            pygame.draw.polygon(screen, COLOR_WHITE, [
                (center_x - 8, center_y),
                (center_x, center_y - 4),
                (center_x, center_y + 4)
            ])
        elif self.direction == "right":
            pygame.draw.polygon(screen, COLOR_WHITE, [
                (center_x + 8, center_y),
                (center_x, center_y - 4),
                (center_x, center_y + 4)
            ])
    
    def get_position(self) -> Tuple[int, int]:
        """位置を取得"""
        return (self.x, self.y)
    
    def set_position(self, x: int, y: int):
        """位置を設定"""
        self.x = x
        self.y = y
        self.rect.x = x
        self.rect.y = y
    
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
