"""
ミニゲーム基底クラス
全てのミニゲームが継承する共通インターフェース
"""

import pygame
import time
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Callable
from enum import Enum
from dataclasses import dataclass

class GameState(Enum):
    """ゲーム状態"""
    READY = "ready"           # 準備中
    PLAYING = "playing"       # プレイ中
    PAUSED = "paused"         # 一時停止
    SUCCESS = "success"       # 成功
    FAILURE = "failure"       # 失敗
    TIMEOUT = "timeout"       # タイムアウト

class Difficulty(Enum):
    """難易度レベル"""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"

@dataclass
class GameScore:
    """ゲームスコア情報"""
    points: int = 0
    time_taken: float = 0.0
    accuracy: float = 0.0
    bonus_points: int = 0
    total_score: int = 0
    
    def calculate_total(self) -> int:
        """総合スコアを計算"""
        self.total_score = self.points + self.bonus_points
        return self.total_score

@dataclass
class GameConfig:
    """ゲーム設定"""
    time_limit: float = 60.0      # 制限時間（秒）
    difficulty: Difficulty = Difficulty.NORMAL
    max_attempts: int = 3         # 最大試行回数
    show_timer: bool = True       # タイマー表示
    show_score: bool = True       # スコア表示
    enable_sound: bool = True     # 音声有効
    enable_animations: bool = True # アニメーション有効

class MinigameBase(ABC):
    """ミニゲーム基底クラス"""
    
    def __init__(self, screen: pygame.Surface, config: GameConfig = None):
        self.screen = screen
        self.config = config or GameConfig()
        
        # ゲーム状態
        self.state = GameState.READY
        self.score = GameScore()
        
        # タイマー関連
        self.start_time = 0.0
        self.elapsed_time = 0.0
        self.remaining_time = self.config.time_limit
        
        # 試行回数
        self.attempts = 0
        self.max_attempts = self.config.max_attempts
        
        # コールバック関数
        self.on_success: Optional[Callable] = None
        self.on_failure: Optional[Callable] = None
        self.on_timeout: Optional[Callable] = None
        self.on_score_update: Optional[Callable] = None
        
        # アニメーション管理
        self.animations = []
        
        # 色定義
        self.colors = {
            'background': (240, 248, 255),
            'text': (50, 50, 50),
            'success': (76, 175, 80),
            'failure': (244, 67, 54),
            'warning': (255, 152, 0),
            'info': (33, 150, 243),
            'timer_normal': (100, 100, 100),
            'timer_warning': (255, 152, 0),
            'timer_critical': (244, 67, 54)
        }
        
        # フォント
        self.fonts = {
            'title': pygame.font.Font(None, 48),
            'large': pygame.font.Font(None, 36),
            'medium': pygame.font.Font(None, 24),
            'small': pygame.font.Font(None, 18)
        }
        
        self._initialize_game()
    
    @abstractmethod
    def _initialize_game(self) -> None:
        """ゲーム固有の初期化処理"""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理（ゲーム固有）"""
        pass
    
    @abstractmethod
    def update_game_logic(self, time_delta: float) -> None:
        """ゲームロジック更新（ゲーム固有）"""
        pass
    
    @abstractmethod
    def draw_game_content(self, surface: pygame.Surface) -> None:
        """ゲーム内容描画（ゲーム固有）"""
        pass
    
    @abstractmethod
    def check_win_condition(self) -> bool:
        """勝利条件チェック"""
        pass
    
    @abstractmethod
    def check_lose_condition(self) -> bool:
        """敗北条件チェック"""
        pass
    
    def start_game(self) -> None:
        """ゲーム開始"""
        if self.state == GameState.READY:
            self.state = GameState.PLAYING
            self.start_time = time.time()
            self.attempts += 1
    
    def pause_game(self) -> None:
        """ゲーム一時停止"""
        if self.state == GameState.PLAYING:
            self.state = GameState.PAUSED
    
    def resume_game(self) -> None:
        """ゲーム再開"""
        if self.state == GameState.PAUSED:
            self.state = GameState.PLAYING
    
    def reset_game(self) -> None:
        """ゲームリセット"""
        self.state = GameState.READY
        self.score = GameScore()
        self.elapsed_time = 0.0
        self.remaining_time = self.config.time_limit
        self.attempts = 0
        self.animations.clear()
        self._initialize_game()
    
    def update(self, time_delta: float) -> None:
        """メイン更新処理"""
        if self.state == GameState.PLAYING:
            # タイマー更新
            self.elapsed_time += time_delta
            self.remaining_time = max(0, self.config.time_limit - self.elapsed_time)
            
            # タイムアウトチェック
            if self.remaining_time <= 0:
                self._handle_timeout()
                return
            
            # ゲーム固有のロジック更新
            self.update_game_logic(time_delta)
            
            # 勝敗判定
            if self.check_win_condition():
                self._handle_success()
            elif self.check_lose_condition():
                self._handle_failure()
        
        # アニメーション更新
        self._update_animations(time_delta)
    
    def draw(self, surface: pygame.Surface) -> None:
        """メイン描画処理"""
        # 背景
        surface.fill(self.colors['background'])
        
        # ゲーム固有の内容描画
        self.draw_game_content(surface)
        
        # UI描画
        self._draw_ui(surface)
        
        # アニメーション描画
        self._draw_animations(surface)
        
        # 状態別オーバーレイ
        self._draw_state_overlay(surface)
    
    def _draw_ui(self, surface: pygame.Surface) -> None:
        """UI描画"""
        # タイマー表示
        if self.config.show_timer and self.state == GameState.PLAYING:
            self._draw_timer(surface)
        
        # スコア表示
        if self.config.show_score:
            self._draw_score(surface)
        
        # 試行回数表示
        self._draw_attempts(surface)
    
    def _draw_timer(self, surface: pygame.Surface) -> None:
        """タイマー描画"""
        # タイマーの色を残り時間に応じて変更
        if self.remaining_time > 20:
            color = self.colors['timer_normal']
        elif self.remaining_time > 10:
            color = self.colors['timer_warning']
        else:
            color = self.colors['timer_critical']
        
        # 時間表示
        time_text = f"残り時間: {self.remaining_time:.1f}秒"
        text_surface = self.fonts['medium'].render(time_text, True, color)
        surface.blit(text_surface, (10, 10))
        
        # プログレスバー
        bar_width = 200
        bar_height = 10
        bar_x = 10
        bar_y = 40
        
        # 背景バー
        pygame.draw.rect(surface, (200, 200, 200), 
                        (bar_x, bar_y, bar_width, bar_height))
        
        # 進捗バー
        progress = self.remaining_time / self.config.time_limit
        progress_width = int(bar_width * progress)
        pygame.draw.rect(surface, color, 
                        (bar_x, bar_y, progress_width, bar_height))
    
    def _draw_score(self, surface: pygame.Surface) -> None:
        """スコア描画"""
        score_text = f"スコア: {self.score.total_score}"
        text_surface = self.fonts['medium'].render(score_text, True, self.colors['text'])
        surface.blit(text_surface, (surface.get_width() - 150, 10))
    
    def _draw_attempts(self, surface: pygame.Surface) -> None:
        """試行回数描画"""
        attempts_text = f"試行: {self.attempts}/{self.max_attempts}"
        text_surface = self.fonts['small'].render(attempts_text, True, self.colors['text'])
        surface.blit(text_surface, (surface.get_width() - 150, 40))
    
    def _draw_state_overlay(self, surface: pygame.Surface) -> None:
        """状態別オーバーレイ描画"""
        if self.state in [GameState.SUCCESS, GameState.FAILURE, GameState.TIMEOUT]:
            # 半透明オーバーレイ
            overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            surface.blit(overlay, (0, 0))
            
            # 結果メッセージ
            if self.state == GameState.SUCCESS:
                message = "成功！"
                color = self.colors['success']
            elif self.state == GameState.FAILURE:
                message = "失敗..."
                color = self.colors['failure']
            else:  # TIMEOUT
                message = "時間切れ"
                color = self.colors['warning']
            
            text_surface = self.fonts['title'].render(message, True, color)
            text_rect = text_surface.get_rect(center=(surface.get_width()//2, surface.get_height()//2))
            surface.blit(text_surface, text_rect)
            
            # スコア表示
            score_text = f"最終スコア: {self.score.total_score}"
            score_surface = self.fonts['large'].render(score_text, True, self.colors['text'])
            score_rect = score_surface.get_rect(center=(surface.get_width()//2, surface.get_height()//2 + 60))
            surface.blit(score_surface, score_rect)
    
    def _handle_success(self) -> None:
        """成功処理"""
        self.state = GameState.SUCCESS
        self._calculate_final_score()
        
        if self.on_success:
            self.on_success(self.score)
    
    def _handle_failure(self) -> None:
        """失敗処理"""
        if self.attempts >= self.max_attempts:
            self.state = GameState.FAILURE
            self._calculate_final_score()
            
            if self.on_failure:
                self.on_failure(self.score)
        else:
            # 再試行可能
            self.state = GameState.READY
            self._initialize_game()
    
    def _handle_timeout(self) -> None:
        """タイムアウト処理"""
        self.state = GameState.TIMEOUT
        self._calculate_final_score()
        
        if self.on_timeout:
            self.on_timeout(self.score)
    
    def _calculate_final_score(self) -> None:
        """最終スコア計算"""
        # 時間ボーナス
        if self.state == GameState.SUCCESS:
            time_bonus = max(0, int((self.remaining_time / self.config.time_limit) * 100))
            self.score.bonus_points += time_bonus
        
        # 難易度ボーナス
        difficulty_multiplier = {
            Difficulty.EASY: 1.0,
            Difficulty.NORMAL: 1.5,
            Difficulty.HARD: 2.0
        }
        multiplier = difficulty_multiplier.get(self.config.difficulty, 1.0)
        self.score.points = int(self.score.points * multiplier)
        
        # 総合スコア計算
        self.score.calculate_total()
        
        if self.on_score_update:
            self.on_score_update(self.score)
    
    def _update_animations(self, time_delta: float) -> None:
        """アニメーション更新"""
        self.animations = [anim for anim in self.animations if anim.update(time_delta)]
    
    def _draw_animations(self, surface: pygame.Surface) -> None:
        """アニメーション描画"""
        for animation in self.animations:
            animation.draw(surface)
    
    def add_animation(self, animation) -> None:
        """アニメーション追加"""
        if self.config.enable_animations:
            self.animations.append(animation)
    
    def set_callbacks(self, on_success: Callable = None, on_failure: Callable = None, 
                     on_timeout: Callable = None, on_score_update: Callable = None) -> None:
        """コールバック関数設定"""
        self.on_success = on_success
        self.on_failure = on_failure
        self.on_timeout = on_timeout
        self.on_score_update = on_score_update
    
    def get_game_info(self) -> Dict[str, Any]:
        """ゲーム情報取得"""
        return {
            'state': self.state.value,
            'score': self.score,
            'elapsed_time': self.elapsed_time,
            'remaining_time': self.remaining_time,
            'attempts': self.attempts,
            'max_attempts': self.max_attempts,
            'difficulty': self.config.difficulty.value
        }
