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
from src.utils.language_manager import get_language_manager

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
        
        # AI行動（簡素化版）
        self.fear_distance = 100.0  # プレイヤーがこの距離に近づくと逃げる
        
        # アニメーション
        self.animation_timer = 0.0
        self.animation_frame = 0
        
        # スプライト
        self.asset_manager = get_asset_manager()
        self.language_manager = get_language_manager()
        self.sprites = self._load_sprites()
        
        # エフェクト
        self.emotion_timer = 0.0
        self.current_emotion = None
        
        print(f"🐾 ペット生成: {self.get_display_name()} ({self.data.pet_type.value})")
    
    def get_display_name(self) -> str:
        """表示用の動物名を取得"""
        return self.language_manager.get_pet_name(self.data.pet_type.value)
    
    def _load_sprites(self) -> Dict[str, pygame.Surface]:
        """ペットスプライトを読み込み"""
        sprites = {}
        
        # スプライトファイル名と実際の方向のマッピング
        # 全てのペットで正常なマッピングを使用
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
    
    def update(self, time_delta: float, player_pos: Optional[Tuple[float, float]] = None, map_system=None):
        """ペットを更新"""
        # ミニゲーム用の簡単な更新（player_posがない場合）
        if player_pos is None:
            self._update_animation(time_delta)
            self._update_emotion(time_delta)
            return
        
        # 通常のゲーム更新
        # プレイヤーとの距離を計算
        distance_to_player = self._calculate_distance(player_pos)
        
        # 状態に応じた行動
        self._update_behavior(time_delta, player_pos, distance_to_player)
        
        # 移動処理（境界チェック付き）
        self._update_movement(time_delta, map_system)
        
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
        
        # 恐怖状態の判定（簡素化版）
        if distance < self.fear_distance:
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
            
            # 方向を更新（scared状態でも正しい判定）
            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                # 修正：下向き移動→front、上向き移動→back
                self.direction = "front" if dy > 0 else "back"
        
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
                
                # 方向を更新（現在が逆なので反転）
                if abs(self.velocity_x) > abs(self.velocity_y):
                    self.direction = "right" if self.velocity_x > 0 else "left"
                else:
                    # 現在: 下向き→back, 上向き→front なので、これを逆転
                    new_direction = "back" if self.velocity_y < 0 else "front"
                    if new_direction != self.direction:
                        move_type = "下向き" if self.velocity_y > 0 else "上向き"
                        print(f"🐾 {self.data.name}: {move_type}移動 velocity_y={self.velocity_y:.2f} → {new_direction}画像を表示")
                    self.direction = new_direction
        else:
            # 十分近い場合は停止
            self.velocity_x = 0
            self.velocity_y = 0
    
    def _enter_scared_state(self, player_pos: Tuple[float, float]):
        """恐怖状態に入る"""
        if self.state != PetState.SCARED:
            self.state = PetState.SCARED
            print(f"😨 {self.get_display_name()}が怖がっています")
    
    def _set_random_direction(self):
        """ランダムな方向に移動開始"""
        angle = random.uniform(0, 2 * math.pi)
        self.velocity_x = math.cos(angle) * self.speed
        self.velocity_y = math.sin(angle) * self.speed
        
        # 方向を更新（現在が逆なので反転）
        if abs(self.velocity_x) > abs(self.velocity_y):
            self.direction = "right" if self.velocity_x > 0 else "left"
        else:
            # 現在: 下向き→back, 上向き→front なので、これを逆転
            new_direction = "back" if self.velocity_y < 0 else "front"
            if new_direction != self.direction:
                move_type = "下向き" if self.velocity_y > 0 else "上向き"
                print(f"🐾 {self.data.name}(ランダム): {move_type}移動 velocity_y={self.velocity_y:.2f} → {new_direction}画像を表示")
            self.direction = new_direction
    
    def _update_movement(self, time_delta: float, map_system=None):
        """移動を更新（境界チェック付き）"""
        # 移動前の位置を保存
        old_x = self.x
        old_y = self.y
        
        # 新しい位置を計算
        new_x = self.x + self.velocity_x * time_delta
        new_y = self.y + self.velocity_y * time_delta
        
        # 境界・衝突判定
        if map_system:
            # X軸移動をチェック
            test_rect_x = pygame.Rect(new_x, self.y, self.rect.width, self.rect.height)
            if not map_system.check_collision(test_rect_x):
                self.x = new_x
            else:
                # 衝突した場合は方向を変える（ログなし）
                self.velocity_x = -self.velocity_x * 0.5
            
            # Y軸移動をチェック
            test_rect_y = pygame.Rect(self.x, new_y, self.rect.width, self.rect.height)
            if not map_system.check_collision(test_rect_y):
                self.y = new_y
            else:
                # 衝突した場合は方向を変える（ログなし）
                self.velocity_y = -self.velocity_y * 0.5
        else:
            # 境界判定なしの場合
            self.x = new_x
            self.y = new_y
        
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
        """プレイヤーとの相互作用（簡素化版）"""
        distance = self._calculate_distance(player_pos)
        
        if distance < 60.0:  # 相互作用可能距離
            if self.state == PetState.SCARED:
                # 恐怖状態では相互作用失敗
                print(f"😰 {self.get_display_name()}は怖がっています")
                return False
            else:
                # 相互作用成功
                print(f"😊 {self.get_display_name()}と仲良くなりました")
                
                # エモーション表示
                self.current_emotion = "happy"
                self.emotion_timer = 2.0
                
                # 追従開始
                if self.state != PetState.FOLLOWING:
                    self.state = PetState.FOLLOWING
                    print(f"💕 {self.get_display_name()}があなたについてきます")
                
                # 救出可能（簡素化版では常に可能）
                return True
        
        return False
    
    def rescue(self) -> bool:
        """ペットを救出（簡素化版）"""
        self.state = PetState.RESCUED
        print(f"🎉 {self.get_display_name()}を救出しました！")
        return True
    
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
            name_surface = font.render(self.get_display_name(), True, (255, 255, 255))
            screen.blit(name_surface, (draw_x, draw_y - 20))
        
        # エモーション表示
        if self.current_emotion:
            self._draw_emotion(screen, draw_x, draw_y)
    
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
    
    def is_rescuable(self) -> bool:
        """救出可能かチェック（簡素化版では常に可能）"""
        return True
    
    def get_state(self) -> PetState:
        """状態を取得"""
        return self.state
