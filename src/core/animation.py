"""
アニメーション効果システム
ミニゲーム用のアニメーション効果を提供
"""

import pygame
import math
from typing import Tuple, Optional
from abc import ABC, abstractmethod

class Animation(ABC):
    """アニメーション基底クラス"""
    
    def __init__(self, duration: float):
        self.duration = duration
        self.elapsed_time = 0.0
        self.is_finished = False
    
    @abstractmethod
    def update(self, time_delta: float) -> bool:
        """アニメーション更新（継続中はTrue、終了時はFalse）"""
        self.elapsed_time += time_delta
        if self.elapsed_time >= self.duration:
            self.is_finished = True
            return False
        return True
    
    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """アニメーション描画"""
        pass
    
    def get_progress(self) -> float:
        """進捗率取得（0.0-1.0）"""
        return min(1.0, self.elapsed_time / self.duration)

class FadeAnimation(Animation):
    """フェードアニメーション"""
    
    def __init__(self, surface: pygame.Surface, position: Tuple[int, int], 
                 duration: float, fade_in: bool = True):
        super().__init__(duration)
        self.surface = surface.copy()
        self.position = position
        self.fade_in = fade_in
        self.original_alpha = surface.get_alpha() or 255
    
    def update(self, time_delta: float) -> bool:
        if not super().update(time_delta):
            return False
        
        progress = self.get_progress()
        if self.fade_in:
            alpha = int(self.original_alpha * progress)
        else:
            alpha = int(self.original_alpha * (1.0 - progress))
        
        self.surface.set_alpha(alpha)
        return True
    
    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.position)

class ScaleAnimation(Animation):
    """スケールアニメーション"""
    
    def __init__(self, surface: pygame.Surface, position: Tuple[int, int],
                 duration: float, start_scale: float = 0.0, end_scale: float = 1.0):
        super().__init__(duration)
        self.original_surface = surface.copy()
        self.position = position
        self.start_scale = start_scale
        self.end_scale = end_scale
        self.current_surface = surface
    
    def update(self, time_delta: float) -> bool:
        if not super().update(time_delta):
            return False
        
        progress = self.get_progress()
        # イージング関数（ease-out）
        eased_progress = 1 - (1 - progress) ** 3
        
        current_scale = self.start_scale + (self.end_scale - self.start_scale) * eased_progress
        
        if current_scale > 0:
            original_size = self.original_surface.get_size()
            new_size = (int(original_size[0] * current_scale), 
                       int(original_size[1] * current_scale))
            
            if new_size[0] > 0 and new_size[1] > 0:
                self.current_surface = pygame.transform.scale(self.original_surface, new_size)
        
        return True
    
    def draw(self, surface: pygame.Surface) -> None:
        if self.current_surface:
            # 中央揃えで描画
            rect = self.current_surface.get_rect()
            rect.center = self.position
            surface.blit(self.current_surface, rect)

class SlideAnimation(Animation):
    """スライドアニメーション"""
    
    def __init__(self, surface: pygame.Surface, start_pos: Tuple[int, int],
                 end_pos: Tuple[int, int], duration: float):
        super().__init__(duration)
        self.surface = surface
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = start_pos
    
    def update(self, time_delta: float) -> bool:
        if not super().update(time_delta):
            return False
        
        progress = self.get_progress()
        # イージング関数（ease-in-out）
        eased_progress = 0.5 * (1 - math.cos(progress * math.pi))
        
        self.current_pos = (
            int(self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * eased_progress),
            int(self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * eased_progress)
        )
        
        return True
    
    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.current_pos)

class BounceAnimation(Animation):
    """バウンスアニメーション"""
    
    def __init__(self, surface: pygame.Surface, position: Tuple[int, int],
                 duration: float, bounce_height: int = 20):
        super().__init__(duration)
        self.surface = surface
        self.base_position = position
        self.bounce_height = bounce_height
        self.current_position = position
    
    def update(self, time_delta: float) -> bool:
        if not super().update(time_delta):
            return False
        
        progress = self.get_progress()
        # バウンス効果（sin波）
        bounce_offset = int(math.sin(progress * math.pi * 4) * 
                           self.bounce_height * (1 - progress))
        
        self.current_position = (
            self.base_position[0],
            self.base_position[1] - bounce_offset
        )
        
        return True
    
    def draw(self, surface: pygame.Surface) -> None:
        surface.blit(self.surface, self.current_position)

class RotateAnimation(Animation):
    """回転アニメーション"""
    
    def __init__(self, surface: pygame.Surface, position: Tuple[int, int],
                 duration: float, start_angle: float = 0, end_angle: float = 360):
        super().__init__(duration)
        self.original_surface = surface.copy()
        self.position = position
        self.start_angle = start_angle
        self.end_angle = end_angle
        self.current_surface = surface
    
    def update(self, time_delta: float) -> bool:
        if not super().update(time_delta):
            return False
        
        progress = self.get_progress()
        current_angle = self.start_angle + (self.end_angle - self.start_angle) * progress
        
        self.current_surface = pygame.transform.rotate(self.original_surface, current_angle)
        
        return True
    
    def draw(self, surface: pygame.Surface) -> None:
        # 回転による位置ずれを補正
        rect = self.current_surface.get_rect()
        rect.center = self.position
        surface.blit(self.current_surface, rect)

class PulseAnimation(Animation):
    """パルスアニメーション"""
    
    def __init__(self, surface: pygame.Surface, position: Tuple[int, int],
                 duration: float, min_scale: float = 0.8, max_scale: float = 1.2):
        super().__init__(duration)
        self.original_surface = surface.copy()
        self.position = position
        self.min_scale = min_scale
        self.max_scale = max_scale
        self.current_surface = surface
    
    def update(self, time_delta: float) -> bool:
        if not super().update(time_delta):
            return False
        
        progress = self.get_progress()
        # パルス効果（sin波）
        pulse_factor = math.sin(progress * math.pi * 6) * 0.5 + 0.5
        current_scale = self.min_scale + (self.max_scale - self.min_scale) * pulse_factor
        
        original_size = self.original_surface.get_size()
        new_size = (int(original_size[0] * current_scale), 
                   int(original_size[1] * current_scale))
        
        if new_size[0] > 0 and new_size[1] > 0:
            self.current_surface = pygame.transform.scale(self.original_surface, new_size)
        
        return True
    
    def draw(self, surface: pygame.Surface) -> None:
        rect = self.current_surface.get_rect()
        rect.center = self.position
        surface.blit(self.current_surface, rect)

class TextAnimation(Animation):
    """テキストアニメーション"""
    
    def __init__(self, text: str, font: pygame.font.Font, color: Tuple[int, int, int],
                 position: Tuple[int, int], duration: float, animation_type: str = "fade"):
        super().__init__(duration)
        self.text = text
        self.font = font
        self.color = color
        self.position = position
        self.animation_type = animation_type
        self.text_surface = font.render(text, True, color)
    
    def update(self, time_delta: float) -> bool:
        return super().update(time_delta)
    
    def draw(self, surface: pygame.Surface) -> None:
        progress = self.get_progress()
        
        if self.animation_type == "fade":
            alpha = int(255 * progress)
            temp_surface = self.text_surface.copy()
            temp_surface.set_alpha(alpha)
            surface.blit(temp_surface, self.position)
        
        elif self.animation_type == "slide_up":
            offset_y = int(50 * (1 - progress))
            pos = (self.position[0], self.position[1] - offset_y)
            alpha = int(255 * progress)
            temp_surface = self.text_surface.copy()
            temp_surface.set_alpha(alpha)
            surface.blit(temp_surface, pos)
        
        elif self.animation_type == "scale":
            scale = progress
            if scale > 0:
                original_size = self.text_surface.get_size()
                new_size = (int(original_size[0] * scale), 
                           int(original_size[1] * scale))
                if new_size[0] > 0 and new_size[1] > 0:
                    scaled_surface = pygame.transform.scale(self.text_surface, new_size)
                    rect = scaled_surface.get_rect()
                    rect.center = self.position
                    surface.blit(scaled_surface, rect)

class ParticleAnimation(Animation):
    """パーティクルアニメーション"""
    
    def __init__(self, position: Tuple[int, int], duration: float, 
                 particle_count: int = 20, colors: list = None):
        super().__init__(duration)
        self.position = position
        self.particles = []
        
        if colors is None:
            colors = [(255, 255, 0), (255, 200, 0), (255, 150, 0)]
        
        # パーティクル初期化
        import random
        for _ in range(particle_count):
            particle = {
                'x': position[0],
                'y': position[1],
                'vx': random.uniform(-100, 100),
                'vy': random.uniform(-150, -50),
                'color': random.choice(colors),
                'size': random.randint(2, 6),
                'life': 1.0
            }
            self.particles.append(particle)
    
    def update(self, time_delta: float) -> bool:
        if not super().update(time_delta):
            return False
        
        # パーティクル更新
        for particle in self.particles:
            particle['x'] += particle['vx'] * time_delta
            particle['y'] += particle['vy'] * time_delta
            particle['vy'] += 200 * time_delta  # 重力
            particle['life'] = 1.0 - self.get_progress()
        
        return True
    
    def draw(self, surface: pygame.Surface) -> None:
        for particle in self.particles:
            if particle['life'] > 0:
                alpha = int(255 * particle['life'])
                color = (*particle['color'], alpha)
                
                # パーティクル描画（円）
                pos = (int(particle['x']), int(particle['y']))
                pygame.draw.circle(surface, particle['color'], pos, 
                                 max(1, int(particle['size'] * particle['life'])))

def create_success_animation(position: Tuple[int, int]) -> list:
    """成功時のアニメーション作成"""
    animations = []
    
    # パーティクル効果
    animations.append(ParticleAnimation(position, 2.0, 30, 
                                      [(255, 215, 0), (255, 255, 0), (255, 165, 0)]))
    
    # 成功テキスト
    font = pygame.font.Font(None, 48)
    animations.append(TextAnimation("成功！", font, (76, 175, 80), 
                                  position, 1.5, "scale"))
    
    return animations

def create_failure_animation(position: Tuple[int, int]) -> list:
    """失敗時のアニメーション作成"""
    animations = []
    
    # 失敗テキスト
    font = pygame.font.Font(None, 48)
    animations.append(TextAnimation("失敗...", font, (244, 67, 54), 
                                  position, 1.5, "fade"))
    
    return animations
