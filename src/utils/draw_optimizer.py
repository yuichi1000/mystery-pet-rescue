"""
描画最適化システム
バッチ描画、カリング、ダーティ矩形管理
"""

import pygame
from typing import List, Tuple, Optional, Dict, Set
from dataclasses import dataclass
from src.utils.performance_optimizer import get_performance_optimizer

@dataclass
class DrawCall:
    """描画コール"""
    surface: pygame.Surface
    position: Tuple[int, int]
    source_rect: Optional[pygame.Rect] = None
    special_flags: int = 0

class DrawOptimizer:
    """描画最適化クラス"""
    
    def __init__(self, screen_width: int, screen_height: int):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen_rect = pygame.Rect(0, 0, screen_width, screen_height)
        
        # バッチ描画
        self.draw_calls: List[DrawCall] = []
        self.batch_size = 50  # バッチサイズ
        
        # カリング（画面外描画の除外）
        self.culling_enabled = True
        self.culling_margin = 32  # カリング余白
        
        # ダーティ矩形
        self.dirty_rects: List[pygame.Rect] = []
        self.dirty_rect_enabled = True
        
        # 統計
        self.total_draw_calls = 0
        self.culled_draw_calls = 0
        self.batched_draw_calls = 0
        
        self.optimizer = get_performance_optimizer()
        
        print("🎨 描画最適化システム初期化完了")
    
    def add_draw_call(self, surface: pygame.Surface, position: Tuple[int, int], 
                     source_rect: Optional[pygame.Rect] = None, 
                     special_flags: int = 0) -> bool:
        """
        描画コールを追加
        
        Returns:
            bool: 描画が必要かどうか（カリングされた場合False）
        """
        self.total_draw_calls += 1
        
        # カリング判定
        if self.culling_enabled and self._should_cull(surface, position, source_rect):
            self.culled_draw_calls += 1
            return False
        
        # 描画コールを追加
        draw_call = DrawCall(surface, position, source_rect, special_flags)
        self.draw_calls.append(draw_call)
        
        # ダーティ矩形を追加
        if self.dirty_rect_enabled:
            rect = self._get_draw_rect(surface, position, source_rect)
            self.dirty_rects.append(rect)
            self.optimizer.add_dirty_rect(rect)
        
        return True
    
    def _should_cull(self, surface: pygame.Surface, position: Tuple[int, int], 
                    source_rect: Optional[pygame.Rect]) -> bool:
        """カリング判定"""
        # 描画矩形を計算
        draw_rect = self._get_draw_rect(surface, position, source_rect)
        
        # 画面外判定（余白を考慮）
        extended_screen = pygame.Rect(
            -self.culling_margin, 
            -self.culling_margin,
            self.screen_width + self.culling_margin * 2,
            self.screen_height + self.culling_margin * 2
        )
        
        return not draw_rect.colliderect(extended_screen)
    
    def _get_draw_rect(self, surface: pygame.Surface, position: Tuple[int, int], 
                      source_rect: Optional[pygame.Rect]) -> pygame.Rect:
        """描画矩形を取得"""
        if source_rect:
            return pygame.Rect(position[0], position[1], source_rect.width, source_rect.height)
        else:
            return pygame.Rect(position[0], position[1], surface.get_width(), surface.get_height())
    
    def flush_draws(self, target_surface: pygame.Surface):
        """バッチ描画を実行"""
        if not self.draw_calls:
            return
        
        # バッチ描画
        if len(self.draw_calls) > 1:
            # Pygameのblitsメソッドを使用
            blits = []
            for draw_call in self.draw_calls:
                if draw_call.source_rect:
                    blits.append((draw_call.surface, draw_call.position, draw_call.source_rect))
                else:
                    blits.append((draw_call.surface, draw_call.position))
            
            target_surface.blits(blits)
            self.batched_draw_calls += len(blits)
        else:
            # 単一描画
            draw_call = self.draw_calls[0]
            if draw_call.source_rect:
                target_surface.blit(draw_call.surface, draw_call.position, draw_call.source_rect)
            else:
                target_surface.blit(draw_call.surface, draw_call.position)
        
        # クリア
        self.draw_calls.clear()
    
    def clear_dirty_rects(self):
        """ダーティ矩形をクリア"""
        self.dirty_rects.clear()
    
    def get_dirty_rects(self) -> List[pygame.Rect]:
        """ダーティ矩形を取得"""
        return self.dirty_rects.copy()
    
    def optimize_surface_for_blitting(self, surface: pygame.Surface) -> pygame.Surface:
        """描画用にサーフェスを最適化（余計な処理なし）"""
        # 画像をそのまま返す
        return surface
    
    def set_optimization_level(self, level: int):
        """最適化レベルを設定"""
        if level >= 2:
            self.culling_enabled = True
            self.dirty_rect_enabled = True
            self.batch_size = 100
        elif level >= 1:
            self.culling_enabled = True
            self.dirty_rect_enabled = False
            self.batch_size = 50
        else:
            self.culling_enabled = False
            self.dirty_rect_enabled = False
            self.batch_size = 1
    
    def get_statistics(self) -> Dict[str, int]:
        """描画統計を取得"""
        return {
            'total_draw_calls': self.total_draw_calls,
            'culled_draw_calls': self.culled_draw_calls,
            'batched_draw_calls': self.batched_draw_calls,
            'current_batch_size': len(self.draw_calls),
            'dirty_rects': len(self.dirty_rects)
        }
    
    def reset_statistics(self):
        """統計をリセット"""
        self.total_draw_calls = 0
        self.culled_draw_calls = 0
        self.batched_draw_calls = 0

# グローバル描画最適化インスタンス
_global_draw_optimizer = None

def get_draw_optimizer(screen_width: int = 1280, screen_height: int = 720) -> DrawOptimizer:
    """グローバル描画最適化インスタンスを取得"""
    global _global_draw_optimizer
    if _global_draw_optimizer is None:
        _global_draw_optimizer = DrawOptimizer(screen_width, screen_height)
    return _global_draw_optimizer

def optimized_blit(target: pygame.Surface, source: pygame.Surface, 
                  position: Tuple[int, int], source_rect: Optional[pygame.Rect] = None):
    """最適化された描画"""
    optimizer = get_draw_optimizer()
    if optimizer.add_draw_call(source, position, source_rect):
        # 即座に描画するか、バッチに追加するかは設定による
        if len(optimizer.draw_calls) >= optimizer.batch_size:
            optimizer.flush_draws(target)
