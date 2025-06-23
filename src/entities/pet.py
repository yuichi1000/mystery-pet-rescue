"""
ペットエンティティ
ゲーム内のペットキャラクター管理
"""

import pygame
import random
import math
from typing import Tuple, Dict, Optional
from dataclasses import dataclass
from enum import Enum

from src.utils.asset_manager import get_asset_manager

class PetState(Enum):
    """ペット状態"""
    IDLE = "idle"
    WANDERING = "wandering"
    SCARED = "scared"
    FOLLOWING = "following"
    RESCUED = "rescued"

class PetType(Enum):
    """ペットタイプ"""
    CAT = "cat"
    DOG = "dog"
    RABBIT = "rabbit"
    BIRD = "bird"

@dataclass
class PetData:
    """ペットデータ"""
    pet_id: str
    name: str
    pet_type: PetType
    personality: str
    rarity: str
    description: str

class Pet:
    """ペットクラス"""
    
    def __init__(self, pet_data: PetData, x: float, y: float):
        # 基本情報
        self.data = pet_data
        self.x = x
        self.y = y
        self.rect = pygame.Rect(x, y, 48, 48)
        
        # 状態
        self.state = PetState.IDLE
        self.direction = random.choice(["front", "back", "left", "right"])
        
        # 移動
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.speed = 50.0  # プレイヤーより遅い
        self.wander_timer = 0.0
        self.wander_interval = random.uniform(2.0, 5.0)
        
        # AI行動
        self.fear_distance = 100.0  # プレイヤーがこの距離に近づくと逃げる
        self.trust_level = 0.0      # 信頼度（0-100）
        self.rescue_threshold = 80.0 # この信頼度で救出可能
        
        # アニメーション
        self.animation_timer = 0.0
        self.animation_frame = 0
        
        # スプライト
        self.asset_manager = get_asset_manager()
        self.sprites = self._load_sprites()
        
        # エフェクト
        self.emotion_timer = 0.0
        self.current_emotion = None
        
        print(f"🐾 ペット生成: {self.data.name} ({self.data.pet_type.value})")
    
    def _load_sprites(self) -> Dict[str, pygame.Surface]:
        """ペットスプライトを読み込み"""
        sprites = {}
        
        # スプライトファイル名と実際の方向のマッピング
        # 犬のスプライトは前後が逆になっているため修正
        if self.data.pet_type == PetType.DOG:
            sprite_mapping = {
                "front": "back",   # frontスプライトを使いたい時はbackファイルを読み込む
                "back": "front",   # backスプライトを使いたい時はfrontファイルを読み込む
                "left": "left",
                "right": "right"
            }
        else:
            # 他のペットは正常
            sprite_mapping = {
                "front": "front",
                "back": "back", 
                "left": "left",
                "right": "right"
            }
        
        # ペットタイプに応じたスプライトパスを決定
        sprite_prefix = f"pet_{self.data.pet_type.value}_001"
        
        for direction, file_direction in sprite_mapping.items():
            sprite_path = f"pets/{sprite_prefix}_{file_direction}.png"
            sprite = self.asset_manager.load_image(sprite_path, (48, 48))
            if sprite:
                sprites[direction] = sprite
                print(f"✅ ペットスプライト読み込み: {sprite_prefix}_{file_direction} → {direction}")
            else:
                print(f"⚠️ ペットスプライト読み込み失敗: {sprite_prefix}_{file_direction}")
        
        return sprites
    
    def update(self, time_delta: float, player_pos: Tuple[float, float]):
        """ペットを更新"""
        # プレイヤーとの距離を計算
        distance_to_player = self._calculate_distance(player_pos)
        
        # 状態に応じた行動
        self._update_behavior(time_delta, player_pos, distance_to_player)
        
        # 移動処理
        self._update_movement(time_delta)
        
        # アニメーション更新
        self._update_animation(time_delta)
        
        # エモーション更新
        self._update_emotion(time_delta)
    
    def _calculate_distance(self, player_pos: Tuple[float, float]) -> float:
        """プレイヤーとの距離を計算"""
        dx = self.x - player_pos[0]
        dy = self.y - player_pos[1]
        return math.sqrt(dx * dx + dy * dy)
    
    def _update_behavior(self, time_delta: float, player_pos: Tuple[float, float], distance: float):
        """行動を更新"""
        if self.state == PetState.RESCUED:
            return
        
        # 恐怖状態の判定
        if distance < self.fear_distance and self.trust_level < 50:
            self._enter_scared_state(player_pos)
        elif self.state == PetState.SCARED and distance > self.fear_distance * 1.5:
            self.state = PetState.IDLE
            self.velocity_x = 0
            self.velocity_y = 0
        
        # 状態別行動
        if self.state == PetState.IDLE:
            self._idle_behavior(time_delta)
        elif self.state == PetState.WANDERING:
            self._wandering_behavior(time_delta)
        elif self.state == PetState.SCARED:
            self._scared_behavior(time_delta, player_pos)
        elif self.state == PetState.FOLLOWING:
            self._following_behavior(time_delta, player_pos)
    
    def _idle_behavior(self, time_delta: float):
        """待機行動"""
        self.wander_timer += time_delta
        
        if self.wander_timer >= self.wander_interval:
            # ランダムに徘徊開始
            if random.random() < 0.7:  # 70%の確率で徘徊
                self.state = PetState.WANDERING
                self._set_random_direction()
            
            self.wander_timer = 0.0
            self.wander_interval = random.uniform(2.0, 5.0)
    
    def _wandering_behavior(self, time_delta: float):
        """徘徊行動"""
        self.wander_timer += time_delta
        
        # 一定時間後に停止
        if self.wander_timer >= 3.0:
            self.state = PetState.IDLE
            self.velocity_x = 0
            self.velocity_y = 0
            self.wander_timer = 0.0
    
    def _scared_behavior(self, time_delta: float, player_pos: Tuple[float, float]):
        """恐怖行動"""
        # プレイヤーから逃げる方向に移動
        dx = self.x - player_pos[0]
        dy = self.y - player_pos[1]
        
        if dx != 0 or dy != 0:
            length = math.sqrt(dx * dx + dy * dy)
            self.velocity_x = (dx / length) * self.speed * 1.5  # 恐怖時は速く移動
            self.velocity_y = (dy / length) * self.speed * 1.5
            
            # 方向を更新
            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "back" if dy > 0 else "front"
        
        # エモーション表示
        self.current_emotion = "scared"
        self.emotion_timer = 1.0
    
    def _following_behavior(self, time_delta: float, player_pos: Tuple[float, float]):
        """追従行動"""
        # プレイヤーに向かって移動（一定距離を保つ）
        target_distance = 80.0
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        if distance > target_distance:
            # プレイヤーに近づく
            if distance > 0:
                self.velocity_x = (dx / distance) * self.speed * 0.8
                self.velocity_y = (dy / distance) * self.speed * 0.8
                
                # 方向を更新（正しい方向判定）
                if abs(dx) > abs(dy):
                    self.direction = "right" if dx > 0 else "left"
                else:
                    self.direction = "front" if dy > 0 else "back"  # 元に戻す
        else:
            # 十分近い場合は停止
            self.velocity_x = 0
            self.velocity_y = 0
    
    def _enter_scared_state(self, player_pos: Tuple[float, float]):
        """恐怖状態に入る"""
        if self.state != PetState.SCARED:
            self.state = PetState.SCARED
            print(f"😨 {self.data.name}が怖がっています")
    
    def _set_random_direction(self):
        """ランダムな方向に移動開始"""
        angle = random.uniform(0, 2 * math.pi)
        self.velocity_x = math.cos(angle) * self.speed
        self.velocity_y = math.sin(angle) * self.speed
        
        # 方向を更新（正しい方向判定）
        if abs(self.velocity_x) > abs(self.velocity_y):
            self.direction = "right" if self.velocity_x > 0 else "left"
        else:
            self.direction = "front" if self.velocity_y > 0 else "back"  # 元に戻す
    
    def _update_movement(self, time_delta: float):
        """移動を更新"""
        self.x += self.velocity_x * time_delta
        self.y += self.velocity_y * time_delta
        
        # 矩形更新
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)
    
    def _update_animation(self, time_delta: float):
        """アニメーションを更新"""
        if abs(self.velocity_x) > 0 or abs(self.velocity_y) > 0:
            self.animation_timer += time_delta
            if self.animation_timer >= 0.3:  # プレイヤーより少し遅いアニメーション
                self.animation_frame = (self.animation_frame + 1) % 2
                self.animation_timer = 0.0
        else:
            self.animation_frame = 0
    
    def _update_emotion(self, time_delta: float):
        """エモーション表示を更新"""
        if self.emotion_timer > 0:
            self.emotion_timer -= time_delta
            if self.emotion_timer <= 0:
                self.current_emotion = None
    
    def interact(self, player_pos: Tuple[float, float]) -> bool:
        """プレイヤーとの相互作用"""
        distance = self._calculate_distance(player_pos)
        
        if distance < 60.0:  # 相互作用可能距離
            if self.state == PetState.SCARED:
                # 恐怖状態では信頼度が下がる
                self.trust_level = max(0, self.trust_level - 5)
                print(f"😰 {self.data.name}の信頼度が下がりました: {self.trust_level:.1f}")
                return False
            else:
                # 信頼度を上げる
                self.trust_level = min(100, self.trust_level + 10)
                print(f"😊 {self.data.name}の信頼度が上がりました: {self.trust_level:.1f}")
                
                # エモーション表示
                self.current_emotion = "happy"
                self.emotion_timer = 2.0
                
                # 信頼度が高くなったら追従開始
                if self.trust_level >= 60 and self.state != PetState.FOLLOWING:
                    self.state = PetState.FOLLOWING
                    print(f"💕 {self.data.name}があなたについてきます")
                
                # 救出可能判定
                if self.trust_level >= self.rescue_threshold:
                    return True
        
        return False
    
    def rescue(self) -> bool:
        """ペットを救出"""
        if self.trust_level >= self.rescue_threshold:
            self.state = PetState.RESCUED
            print(f"🎉 {self.data.name}を救出しました！")
            return True
        return False
    
    def draw(self, screen: pygame.Surface, camera_offset: Tuple[int, int] = (0, 0)):
        """ペットを描画"""
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]
        
        # スプライト描画
        if self.direction in self.sprites:
            sprite = self.sprites[self.direction]
            screen.blit(sprite, (draw_x, draw_y))
        else:
            # フォールバック: 色付き矩形
            color_map = {
                PetType.CAT: (255, 165, 0),    # オレンジ
                PetType.DOG: (139, 69, 19),    # 茶色
                PetType.RABBIT: (255, 255, 255), # 白
                PetType.BIRD: (0, 191, 255)    # 青
            }
            color = color_map.get(self.data.pet_type, (128, 128, 128))
            pygame.draw.rect(screen, color, (draw_x, draw_y, self.rect.width, self.rect.height))
            
            # ペット名表示
            font = pygame.font.Font(None, 16)
            name_surface = font.render(self.data.name, True, (255, 255, 255))
            screen.blit(name_surface, (draw_x, draw_y - 20))
        
        # 信頼度バー
        if self.trust_level > 0:
            self._draw_trust_bar(screen, draw_x, draw_y)
        
        # エモーション表示
        if self.current_emotion:
            self._draw_emotion(screen, draw_x, draw_y)
    
    def _draw_trust_bar(self, screen: pygame.Surface, x: int, y: int):
        """信頼度バーを描画"""
        bar_width = self.rect.width
        bar_height = 3
        bar_y = y - 12
        
        # 背景
        pygame.draw.rect(screen, (100, 100, 100), (x, bar_y, bar_width, bar_height))
        
        # 信頼度
        trust_width = int(bar_width * (self.trust_level / 100))
        trust_color = (0, 255, 0) if self.trust_level >= self.rescue_threshold else (255, 255, 0)
        pygame.draw.rect(screen, trust_color, (x, bar_y, trust_width, bar_height))
    
    def _draw_emotion(self, screen: pygame.Surface, x: int, y: int):
        """エモーションを描画"""
        emotion_symbols = {
            "happy": "♥",
            "scared": "!",
            "angry": "💢"
        }
        
        symbol = emotion_symbols.get(self.current_emotion, "?")
        font = pygame.font.Font(None, 24)
        emotion_surface = font.render(symbol, True, (255, 255, 255))
        
        # ペットの上に表示
        emotion_x = x + self.rect.width // 2 - emotion_surface.get_width() // 2
        emotion_y = y - 30
        screen.blit(emotion_surface, (emotion_x, emotion_y))
    
    def get_position(self) -> Tuple[float, float]:
        """位置を取得"""
        return (self.x, self.y)
    
    def get_trust_level(self) -> float:
        """信頼度を取得"""
        return self.trust_level
    
    def is_rescuable(self) -> bool:
        """救出可能かチェック"""
        return self.trust_level >= self.rescue_threshold
    
    def get_state(self) -> PetState:
        """状態を取得"""
        return self.state
