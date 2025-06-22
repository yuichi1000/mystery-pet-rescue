"""
アクションゲーム - 障害物回避でペットに近づく
プレイヤーが障害物を避けながらペットに到達するゲーム
"""

import pygame
import random
import math
from typing import List, Tuple
from dataclasses import dataclass

from src.core.minigame import MinigameBase, GameConfig, Difficulty
from src.core.animation import SlideAnimation, BounceAnimation, create_success_animation

@dataclass
class GameObject:
    """ゲームオブジェクト基底クラス"""
    x: float
    y: float
    width: int
    height: int
    color: Tuple[int, int, int]
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    def collides_with(self, other: 'GameObject') -> bool:
        return self.get_rect().colliderect(other.get_rect())

@dataclass
class Player(GameObject):
    """プレイヤークラス"""
    speed: float = 200.0
    
    def move(self, dx: float, dy: float, time_delta: float, bounds: pygame.Rect) -> None:
        """プレイヤー移動"""
        new_x = self.x + dx * self.speed * time_delta
        new_y = self.y + dy * self.speed * time_delta
        
        # 画面境界チェック
        self.x = max(bounds.left, min(bounds.right - self.width, new_x))
        self.y = max(bounds.top, min(bounds.bottom - self.height, new_y))

@dataclass
class Obstacle(GameObject):
    """障害物クラス"""
    speed: float = 100.0
    direction: Tuple[float, float] = (0, 1)  # 移動方向
    
    def update(self, time_delta: float, bounds: pygame.Rect) -> bool:
        """障害物更新（画面外に出たらFalseを返す）"""
        self.x += self.direction[0] * self.speed * time_delta
        self.y += self.direction[1] * self.speed * time_delta
        
        # 画面外チェック
        return (self.x + self.width >= bounds.left and 
                self.x <= bounds.right and
                self.y + self.height >= bounds.top and 
                self.y <= bounds.bottom)

@dataclass
class Pet(GameObject):
    """ペットクラス"""
    rescued: bool = False
    animation_time: float = 0.0
    
    def update(self, time_delta: float) -> None:
        """ペットアニメーション更新"""
        self.animation_time += time_delta

class ActionGame(MinigameBase):
    """アクションゲーム実装"""
    
    def __init__(self, screen: pygame.Surface, config: GameConfig = None):
        # ゲーム設定を先に初期化
        self.game_area = pygame.Rect(50, 100, screen.get_width() - 100, screen.get_height() - 150)
        
        # ゲームオブジェクト
        self.player = None
        self.pet = None
        self.obstacles: List[Obstacle] = []
        
        # 障害物生成
        self.obstacle_spawn_timer = 0.0
        self.obstacle_spawn_interval = 2.0  # 秒
        
        # 難易度設定
        self.difficulty_settings = {
            Difficulty.EASY: {
                'obstacle_speed': 80.0,
                'spawn_interval': 2.5,
                'obstacle_count': 1
            },
            Difficulty.NORMAL: {
                'obstacle_speed': 120.0,
                'spawn_interval': 2.0,
                'obstacle_count': 2
            },
            Difficulty.HARD: {
                'obstacle_speed': 160.0,
                'spawn_interval': 1.5,
                'obstacle_count': 3
            }
        }
        
        # 効果音（仮想）
        self.sounds = {
            'move': None,
            'collision': None,
            'success': None
        }
        
        # 親クラス初期化（最後に実行）
        super().__init__(screen, config)
        
        # 現在の設定を適用
        current_settings = self.difficulty_settings[self.config.difficulty]
        self.obstacle_spawn_interval = current_settings['spawn_interval']
        self.obstacle_speed = current_settings['obstacle_speed']
        self.obstacles_per_spawn = current_settings['obstacle_count']
    
    def _initialize_game(self) -> None:
        """ゲーム初期化"""
        # プレイヤー初期化
        player_size = 64  # 256→64に縮小して使用
        self.player = Player(
            x=self.game_area.centerx - player_size // 2,
            y=self.game_area.bottom - player_size - 10,
            width=player_size,
            height=player_size,
            color=(33, 150, 243),  # 青色
            speed=200.0
        )
        
        # ペット初期化
        pet_size = 64  # 256→64に縮小して使用
        self.pet = Pet(
            x=self.game_area.centerx - pet_size // 2,
            y=self.game_area.top + 20,
            width=pet_size,
            height=pet_size,
            color=(255, 193, 7),  # 黄色
            rescued=False
        )
        
        # 障害物リセット
        self.obstacles.clear()
        self.obstacle_spawn_timer = 0.0
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self.state.value == "ready":
                self.start_game()
                return True
            elif event.key == pygame.K_r and self.state.value in ["success", "failure", "timeout"]:
                self.reset_game()
                return True
        
        return False
    
    def update_game_logic(self, time_delta: float) -> None:
        """ゲームロジック更新"""
        # キー入力処理
        keys = pygame.key.get_pressed()
        dx = dy = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            dx = -1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            dx = 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            dy = -1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            dy = 1
        
        # プレイヤー移動
        if dx != 0 or dy != 0:
            self.player.move(dx, dy, time_delta, self.game_area)
        
        # 障害物生成
        self.obstacle_spawn_timer += time_delta
        if self.obstacle_spawn_timer >= self.obstacle_spawn_interval:
            self._spawn_obstacles()
            self.obstacle_spawn_timer = 0.0
        
        # 障害物更新
        self.obstacles = [obs for obs in self.obstacles 
                         if obs.update(time_delta, self.game_area)]
        
        # ペットアニメーション更新
        self.pet.update(time_delta)
        
        # 衝突判定
        for obstacle in self.obstacles:
            if self.player.collides_with(obstacle):
                # 衝突時の処理
                self._handle_collision()
                break
        
        # ペット到達判定
        if self.player.collides_with(self.pet) and not self.pet.rescued:
            self.pet.rescued = True
            self.score.points += 100
            
            # 成功アニメーション
            pet_center = (int(self.pet.x + self.pet.width // 2), 
                         int(self.pet.y + self.pet.height // 2))
            success_animations = create_success_animation(pet_center)
            for anim in success_animations:
                self.add_animation(anim)
    
    def _spawn_obstacles(self) -> None:
        """障害物生成"""
        for _ in range(self.obstacles_per_spawn):
            # ランダムな位置から生成
            spawn_side = random.choice(['top', 'left', 'right'])
            obstacle_size = random.randint(15, 30)
            
            if spawn_side == 'top':
                x = random.randint(self.game_area.left, 
                                 self.game_area.right - obstacle_size)
                y = self.game_area.top - obstacle_size
                direction = (random.uniform(-0.5, 0.5), 1.0)
            elif spawn_side == 'left':
                x = self.game_area.left - obstacle_size
                y = random.randint(self.game_area.top, 
                                 self.game_area.bottom - obstacle_size)
                direction = (1.0, random.uniform(-0.5, 0.5))
            else:  # right
                x = self.game_area.right
                y = random.randint(self.game_area.top, 
                                 self.game_area.bottom - obstacle_size)
                direction = (-1.0, random.uniform(-0.5, 0.5))
            
            obstacle = Obstacle(
                x=x, y=y,
                width=obstacle_size,
                height=obstacle_size,
                color=(244, 67, 54),  # 赤色
                speed=self.obstacle_speed,
                direction=direction
            )
            
            self.obstacles.append(obstacle)
    
    def _handle_collision(self) -> None:
        """衝突処理"""
        # プレイヤーを初期位置に戻す
        self.player.x = self.game_area.centerx - self.player.width // 2
        self.player.y = self.game_area.bottom - self.player.height - 10
        
        # スコア減点
        self.score.points = max(0, self.score.points - 20)
        
        # 衝突アニメーション
        collision_pos = (int(self.player.x + self.player.width // 2),
                        int(self.player.y + self.player.height // 2))
        
        # プレイヤーをバウンスさせる
        player_surface = pygame.Surface((self.player.width, self.player.height))
        player_surface.fill(self.player.color)
        bounce_anim = BounceAnimation(player_surface, collision_pos, 0.5, 10)
        self.add_animation(bounce_anim)
    
    def draw_game_content(self, surface: pygame.Surface) -> None:
        """ゲーム内容描画"""
        # ゲームエリア背景
        pygame.draw.rect(surface, (245, 245, 245), self.game_area)
        pygame.draw.rect(surface, (200, 200, 200), self.game_area, 2)
        
        # プレイヤー描画
        pygame.draw.rect(surface, self.player.color, self.player.get_rect())
        pygame.draw.rect(surface, (255, 255, 255), self.player.get_rect(), 2)
        
        # ペット描画（アニメーション付き）
        pet_rect = self.pet.get_rect()
        if not self.pet.rescued:
            # ペットの点滅アニメーション
            alpha = int(128 + 127 * math.sin(self.pet.animation_time * 4))
            pet_surface = pygame.Surface((self.pet.width, self.pet.height), pygame.SRCALPHA)
            pet_surface.fill((*self.pet.color, alpha))
            surface.blit(pet_surface, pet_rect)
        else:
            # 救助済みペット
            pygame.draw.rect(surface, (76, 175, 80), pet_rect)
        
        pygame.draw.rect(surface, (255, 255, 255), pet_rect, 2)
        
        # 障害物描画
        for obstacle in self.obstacles:
            pygame.draw.rect(surface, obstacle.color, obstacle.get_rect())
            pygame.draw.rect(surface, (150, 150, 150), obstacle.get_rect(), 1)
        
        # 操作説明
        if self.state.value == "ready":
            instructions = [
                "WASD または矢印キー: 移動",
                "障害物を避けてペットに到達しよう！",
                "SPACE: ゲーム開始"
            ]
            
            y_offset = self.game_area.bottom + 20
            for instruction in instructions:
                text_surface = self.fonts['small'].render(instruction, True, self.colors['text'])
                text_rect = text_surface.get_rect(center=(surface.get_width() // 2, y_offset))
                surface.blit(text_surface, text_rect)
                y_offset += 25
        
        # 距離表示
        if self.state.value == "playing":
            distance = math.sqrt((self.player.x - self.pet.x) ** 2 + 
                               (self.player.y - self.pet.y) ** 2)
            distance_text = f"ペットまでの距離: {int(distance)}"
            text_surface = self.fonts['small'].render(distance_text, True, self.colors['info'])
            surface.blit(text_surface, (10, 70))
    
    def check_win_condition(self) -> bool:
        """勝利条件チェック"""
        return self.pet.rescued
    
    def check_lose_condition(self) -> bool:
        """敗北条件チェック"""
        # このゲームでは時間切れのみが敗北条件
        return False
