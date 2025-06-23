"""
パフォーマンス最適化システム
FPS安定化、メモリ管理、描画最適化
"""

import pygame
import time
import gc
from typing import Dict, List, Optional, Any, Tuple
from collections import deque
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    """パフォーマンス指標"""
    fps: float = 0.0
    frame_time: float = 0.0
    memory_usage: float = 0.0
    draw_calls: int = 0
    update_time: float = 0.0
    draw_time: float = 0.0

class PerformanceOptimizer:
    """パフォーマンス最適化クラス"""
    
    def __init__(self, target_fps: int = 60):
        self.target_fps = target_fps
        self.target_frame_time = 1.0 / target_fps
        
        # フレーム時間履歴（移動平均用）
        self.frame_times = deque(maxlen=60)  # 1秒分
        self.update_times = deque(maxlen=60)
        self.draw_times = deque(maxlen=60)
        
        # パフォーマンス指標
        self.metrics = PerformanceMetrics()
        
        # 最適化設定
        self.optimization_level = 1  # 0=無効, 1=軽微, 2=中程度, 3=積極的
        self.adaptive_quality = True
        self.vsync_enabled = True
        
        # 描画最適化
        self.dirty_rect_enabled = True
        self.dirty_rects: List[pygame.Rect] = []
        
        # メモリ管理
        self.gc_interval = 300  # 5秒ごと
        self.gc_counter = 0
        
        # 統計
        self.total_frames = 0
        self.start_time = time.time()
        
        print("⚡ パフォーマンス最適化システム初期化完了")
    
    def begin_frame(self) -> float:
        """フレーム開始"""
        self.frame_start_time = time.time()
        self.draw_calls_count = 0
        self.dirty_rects.clear()
        return self.frame_start_time
    
    def begin_update(self):
        """更新処理開始"""
        self.update_start_time = time.time()
    
    def end_update(self):
        """更新処理終了"""
        if hasattr(self, 'update_start_time'):
            update_time = time.time() - self.update_start_time
            self.update_times.append(update_time)
    
    def begin_draw(self):
        """描画処理開始"""
        self.draw_start_time = time.time()
    
    def end_draw(self):
        """描画処理終了"""
        if hasattr(self, 'draw_start_time'):
            draw_time = time.time() - self.draw_start_time
            self.draw_times.append(draw_time)
    
    def add_dirty_rect(self, rect: pygame.Rect):
        """ダーティ矩形を追加"""
        if self.dirty_rect_enabled:
            self.dirty_rects.append(rect)
    
    def get_dirty_rects(self) -> List[pygame.Rect]:
        """ダーティ矩形を取得"""
        return self.dirty_rects.copy()
    
    def end_frame(self) -> bool:
        """
        フレーム終了
        
        Returns:
            bool: フレームスキップが必要かどうか
        """
        if not hasattr(self, 'frame_start_time'):
            return False
        
        # フレーム時間計算
        frame_time = time.time() - self.frame_start_time
        self.frame_times.append(frame_time)
        
        # 統計更新
        self.total_frames += 1
        self._update_metrics()
        
        # ガベージコレクション
        self._manage_memory()
        
        # 適応的品質調整
        if self.adaptive_quality:
            self._adjust_quality()
        
        # フレームスキップ判定
        return self._should_skip_frame()
    
    def _update_metrics(self):
        """パフォーマンス指標を更新"""
        if self.frame_times:
            avg_frame_time = sum(self.frame_times) / len(self.frame_times)
            self.metrics.frame_time = avg_frame_time
            self.metrics.fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
        
        if self.update_times:
            self.metrics.update_time = sum(self.update_times) / len(self.update_times)
        
        if self.draw_times:
            self.metrics.draw_time = sum(self.draw_times) / len(self.draw_times)
        
        self.metrics.draw_calls = self.draw_calls_count
    
    def _manage_memory(self):
        """メモリ管理"""
        self.gc_counter += 1
        
        if self.gc_counter >= self.gc_interval:
            # ガベージコレクション実行
            collected = gc.collect()
            if collected > 0:
                print(f"🧹 ガベージコレクション: {collected}オブジェクト回収")
            self.gc_counter = 0
    
    def _adjust_quality(self):
        """適応的品質調整"""
        if len(self.frame_times) < 30:  # 十分なサンプルがない
            return
        
        avg_fps = self.metrics.fps
        
        if avg_fps < self.target_fps * 0.8:  # 80%以下
            # 品質を下げる
            if self.optimization_level < 3:
                self.optimization_level += 1
                print(f"📉 品質レベル下げ: {self.optimization_level}")
        elif avg_fps > self.target_fps * 0.95:  # 95%以上
            # 品質を上げる
            if self.optimization_level > 0:
                self.optimization_level -= 1
                print(f"📈 品質レベル上げ: {self.optimization_level}")
    
    def _should_skip_frame(self) -> bool:
        """フレームスキップが必要かどうか判定"""
        if self.optimization_level >= 3:
            # 積極的最適化：重いフレームをスキップ
            if len(self.frame_times) >= 3:
                recent_times = list(self.frame_times)[-3:]
                avg_recent = sum(recent_times) / len(recent_times)
                if avg_recent > self.target_frame_time * 1.5:
                    return True
        
        return False
    
    def get_optimization_settings(self) -> Dict[str, Any]:
        """現在の最適化設定を取得"""
        return {
            'optimization_level': self.optimization_level,
            'dirty_rect_enabled': self.dirty_rect_enabled,
            'adaptive_quality': self.adaptive_quality,
            'vsync_enabled': self.vsync_enabled
        }
    
    def get_metrics(self) -> PerformanceMetrics:
        """パフォーマンス指標を取得"""
        return self.metrics
    
    def get_performance_report(self) -> str:
        """パフォーマンスレポートを生成"""
        uptime = time.time() - self.start_time
        avg_fps = self.total_frames / uptime if uptime > 0 else 0
        
        report = f"""
⚡ パフォーマンスレポート
━━━━━━━━━━━━━━━━━━━━
📊 基本指標:
  現在FPS: {self.metrics.fps:.1f}
  平均FPS: {avg_fps:.1f}
  フレーム時間: {self.metrics.frame_time*1000:.2f}ms
  更新時間: {self.metrics.update_time*1000:.2f}ms
  描画時間: {self.metrics.draw_time*1000:.2f}ms

🎯 最適化状況:
  最適化レベル: {self.optimization_level}/3
  適応的品質: {'有効' if self.adaptive_quality else '無効'}
  ダーティ矩形: {'有効' if self.dirty_rect_enabled else '無効'}
  
📈 統計:
  総フレーム数: {self.total_frames}
  稼働時間: {uptime:.1f}秒
  描画コール数: {self.metrics.draw_calls}
━━━━━━━━━━━━━━━━━━━━
"""
        return report

# グローバル最適化インスタンス
_global_optimizer = None

def get_performance_optimizer() -> PerformanceOptimizer:
    """グローバル最適化インスタンスを取得"""
    global _global_optimizer
    if _global_optimizer is None:
        _global_optimizer = PerformanceOptimizer()
    return _global_optimizer

def optimize_surface(surface: pygame.Surface) -> pygame.Surface:
    """サーフェスを最適化"""
    if surface.get_flags() & pygame.SRCALPHA:
        # アルファチャンネル付き
        return surface.convert_alpha()
    else:
        # 通常のサーフェス
        return surface.convert()

def batch_blit(surface: pygame.Surface, blits: List[Tuple[pygame.Surface, Tuple[int, int]]]):
    """バッチ描画（複数の描画を一度に実行）"""
    if len(blits) > 1:
        # Pygameのblitsメソッドを使用（高速）
        surface.blits(blits)
    elif len(blits) == 1:
        # 単一描画
        surface.blit(blits[0][0], blits[0][1])
