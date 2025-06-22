"""
ペットクラス

ゲーム内のペットを管理
"""

import pygame
import random
import math
from typing import Tuple, Optional
from config.constants import *


class Pet:
    """ペットクラス"""
    
    def __init__(self, pet_type: str, x: int, y: int, pet_id: Optional[str] = None):
        """
        ペットを初期化
        
        Args:
            pet_type: ペットの種類
            x: 初期X座標
            y: 初期Y座標
            pet_id: ペットID（省略時は自動生成）
        """
        self.pet_id = pet_id or f"{pet_type}_{random.randint(1000, 9999)}"
        self.pet_type = pet_type
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        
        # 状態
        self.state = PET_STATE_LOST
        self.trust_level = 0  # 0-100
        self.fear_level = 50  # 0-100
        self.hunger_level = 70  # 0-100
        
        # 移動
        self.speed = PET_SPEED
        self.direction = random.choice(["up", "down", "left", "right"])
        self.move_timer = 0
        self.move_interval = random.randint(60, 180)  # フレーム数
        
        # 当たり判定
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # AI行動
        self.behavior_state = "wandering"  # wandering, hiding, fleeing, following
        self.target_x = x
        self.target_y = y
        self.detection_radius = 100
        
        # アニメーション
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 15
        
        # 個性
        self.personality = self._generate_personality()
        
        # 飼い主情報
        self.owner_name = self._generate_owner_name()
        self.owner_description = self._generate_owner_description()
        
        # 発見状態
        self.is_discovered = False
        self.discovery_time = 0
    
    def _generate_personality(self) -> dict:
        """ペットの個性を生成"""
        personalities = {
            "dog": {"friendly": 80, "energetic": 70, "loyal": 90},
            "cat": {"independent": 85, "curious": 75, "aloof": 60},
            "rabbit": {"timid": 80, "gentle": 85, "quick": 70},
            "hamster": {"active": 90, "small": 95, "nocturnal": 80},
            "bird": {"vocal": 85, "intelligent": 80, "social": 70},
            "fish": {"calm": 95, "silent": 90, "graceful": 80},
            "turtle": {"slow": 95, "patient": 90, "wise": 85},
            "ferret": {"playful": 90, "mischievous": 85, "energetic": 80}
        }
        
        base_personality = personalities.get(self.pet_type, {"neutral": 50})
        
        # ランダムな変動を加える
        result = {}
        for trait, value in base_personality.items():
            variation = random.randint(-20, 20)
            result[trait] = max(0, min(100, value + variation))
        
        return result
    
    def _generate_owner_name(self) -> str:
        """飼い主の名前を生成"""
        names = [
            "田中さん", "佐藤さん", "鈴木さん", "高橋さん", "渡辺さん",
            "伊藤さん", "山田さん", "中村さん", "小林さん", "加藤さん"
        ]
        return random.choice(names)
    
    def _generate_owner_description(self) -> str:
        """飼い主の説明を生成"""
        descriptions = [
            "優しいおばあさん",
            "小さな男の子",
            "犬好きの女性",
            "一人暮らしの学生",
            "家族連れ",
            "動物愛好家",
            "近所の住人"
        ]
        return random.choice(descriptions)
    
    def update(self, player_pos: Tuple[int, int]):
        """ペットを更新"""
        # プレイヤーとの距離を計算
        distance_to_player = self._calculate_distance(player_pos)
        
        # AI行動を更新
        self._update_behavior(player_pos, distance_to_player)
        
        # 移動処理
        self._update_movement()
        
        # アニメーション更新
        self._update_animation()
        
        # 状態更新
        self._update_state()
        
        # 当たり判定更新
        self.rect.x = self.x
        self.rect.y = self.y
    
    def _calculate_distance(self, target_pos: Tuple[int, int]) -> float:
        """指定位置との距離を計算"""
        dx = self.x - target_pos[0]
        dy = self.y - target_pos[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def _update_behavior(self, player_pos: Tuple[int, int], distance: float):
        """AI行動を更新"""
        if distance <= self.detection_radius:
            if not self.is_discovered:
                self.is_discovered = True
                self.discovery_time = pygame.time.get_ticks()
            
            # 信頼度に基づいて行動を決定
            if self.trust_level > 70:
                self.behavior_state = "following"
                self.target_x = player_pos[0]
                self.target_y = player_pos[1]
            elif self.fear_level > 60:
                self.behavior_state = "fleeing"
                # プレイヤーから逃げる方向を設定
                dx = self.x - player_pos[0]
                dy = self.y - player_pos[1]
                if dx != 0 or dy != 0:
                    length = math.sqrt(dx * dx + dy * dy)
                    self.target_x = self.x + (dx / length) * 100
                    self.target_y = self.y + (dy / length) * 100
            else:
                self.behavior_state = "hiding"
        else:
            self.behavior_state = "wandering"
            self._set_random_target()
    
    def _set_random_target(self):
        """ランダムな目標位置を設定"""
        self.move_timer += 1
        if self.move_timer >= self.move_interval:
            self.move_timer = 0
            self.move_interval = random.randint(60, 180)
            
            # 現在位置から適度な距離の目標を設定
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(50, 150)
            self.target_x = self.x + math.cos(angle) * distance
            self.target_y = self.y + math.sin(angle) * distance
            
            # 画面境界内に制限
            self.target_x = max(0, min(SCREEN_WIDTH - self.width, self.target_x))
            self.target_y = max(0, min(SCREEN_HEIGHT - self.height, self.target_y))
    
    def _update_movement(self):
        """移動処理"""
        # 目標位置への移動
        dx = self.target_x - self.x
        dy = self.target_y - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > self.speed:
            # 正規化して移動
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            
            # 方向を更新
            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "down" if dy > 0 else "up"
    
    def _update_animation(self):
        """アニメーション更新"""
        self.animation_timer += 1
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % 4
    
    def _update_state(self):
        """状態更新"""
        # 時間経過による変化
        if self.hunger_level > 0:
            self.hunger_level -= 0.1
        
        # 恐怖レベルの自然減少
        if self.fear_level > 0:
            self.fear_level -= 0.05
    
    def render(self, screen: pygame.Surface):
        """ペットを描画"""
        # ペットの種類に応じた色
        colors = {
            "dog": COLOR_YELLOW,
            "cat": (255, 165, 0),  # オレンジ
            "rabbit": COLOR_WHITE,
            "hamster": (139, 69, 19),  # 茶色
            "bird": (0, 255, 255),  # シアン
            "fish": COLOR_BLUE,
            "turtle": COLOR_GREEN,
            "ferret": (128, 0, 128)  # 紫
        }
        
        color = colors.get(self.pet_type, COLOR_GRAY)
        
        # 状態に応じて色を調整
        if self.state == PET_STATE_FOUND:
            # 少し明るくする
            color = tuple(min(255, c + 50) for c in color)
        elif self.behavior_state == "fleeing":
            # 赤みを加える
            color = (min(255, color[0] + 50), color[1], color[2])
        
        # ペットを描画
        pygame.draw.ellipse(screen, color, self.rect)
        
        # 状態インジケーター
        if self.is_discovered:
            # 信頼度バー
            bar_width = self.width
            bar_height = 4
            bar_x = self.x
            bar_y = self.y - 8
            
            # 背景
            pygame.draw.rect(screen, COLOR_GRAY, (bar_x, bar_y, bar_width, bar_height))
            # 信頼度
            trust_width = int(bar_width * (self.trust_level / 100))
            pygame.draw.rect(screen, COLOR_GREEN, (bar_x, bar_y, trust_width, bar_height))
    
    def interact_with_player(self, interaction_type: str):
        """プレイヤーとの相互作用"""
        if interaction_type == "approach":
            if self.fear_level > 50:
                self.fear_level += 10
                self.trust_level -= 5
            else:
                self.trust_level += 5
                self.fear_level -= 3
        
        elif interaction_type == "feed":
            self.hunger_level = min(100, self.hunger_level + 30)
            self.trust_level += 15
            self.fear_level -= 10
        
        elif interaction_type == "pet":
            if self.trust_level > 30:
                self.trust_level += 10
                self.fear_level -= 5
            else:
                self.fear_level += 15
        
        # 値の範囲制限
        self.trust_level = max(0, min(100, self.trust_level))
        self.fear_level = max(0, min(100, self.fear_level))
        self.hunger_level = max(0, min(100, self.hunger_level))
    
    def can_be_rescued(self) -> bool:
        """救助可能かチェック"""
        return self.trust_level >= 70 and self.fear_level <= 30
    
    def rescue(self):
        """ペットを救助"""
        if self.can_be_rescued():
            self.state = PET_STATE_RESCUED
            return True
        return False
    
    def get_info(self) -> dict:
        """ペット情報を取得"""
        return {
            "id": self.pet_id,
            "type": self.pet_type,
            "state": self.state,
            "trust_level": self.trust_level,
            "fear_level": self.fear_level,
            "hunger_level": self.hunger_level,
            "owner_name": self.owner_name,
            "owner_description": self.owner_description,
            "personality": self.personality,
            "is_discovered": self.is_discovered
        }
