"""
ミニゲームシステム

ペットとの信頼関係を築くためのミニゲーム
"""

import pygame
import random
import math
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod
from enum import Enum

from config.constants import *


class MiniGameResult(Enum):
    """ミニゲーム結果"""
    SUCCESS = "success"
    FAILURE = "failure"
    PERFECT = "perfect"
    TIMEOUT = "timeout"


class MiniGame(ABC):
    """ミニゲームの基底クラス"""
    
    def __init__(self, pet_type: str, difficulty: int = 1):
        """
        ミニゲームを初期化
        
        Args:
            pet_type: ペットの種類
            difficulty: 難易度 (1-5)
        """
        self.pet_type = pet_type
        self.difficulty = difficulty
        self.time_limit = 30.0  # 秒
        self.start_time = 0
        self.is_active = False
        self.result = None
        self.score = 0
        self.max_score = 100
    
    @abstractmethod
    def start(self):
        """ゲーム開始"""
        pass
    
    @abstractmethod
    def update(self, input_handler):
        """ゲーム更新"""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """ゲーム描画"""
        pass
    
    def get_remaining_time(self) -> float:
        """残り時間を取得"""
        if not self.is_active:
            return 0
        
        elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
        return max(0, self.time_limit - elapsed)
    
    def is_time_up(self) -> bool:
        """時間切れかチェック"""
        return self.get_remaining_time() <= 0
    
    def calculate_trust_bonus(self) -> int:
        """信頼度ボーナスを計算"""
        if self.result == MiniGameResult.PERFECT:
            return 25
        elif self.result == MiniGameResult.SUCCESS:
            return 15
        elif self.result == MiniGameResult.FAILURE:
            return 5
        else:
            return 0


class CatchGame(MiniGame):
    """キャッチゲーム - ペットが投げるボールをキャッチ"""
    
    def __init__(self, pet_type: str, difficulty: int = 1):
        super().__init__(pet_type, difficulty)
        self.balls = []
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT - 100
        self.player_width = 60
        self.player_height = 20
        self.balls_caught = 0
        self.balls_missed = 0
        self.target_catches = 5 + difficulty
        self.ball_spawn_timer = 0
        self.ball_spawn_interval = max(30, 90 - difficulty * 10)
    
    def start(self):
        """ゲーム開始"""
        self.is_active = True
        self.start_time = pygame.time.get_ticks()
        self.balls.clear()
        self.balls_caught = 0
        self.balls_missed = 0
        self.score = 0
    
    def update(self, input_handler):
        """ゲーム更新"""
        if not self.is_active:
            return
        
        # 時間切れチェック
        if self.is_time_up():
            self._end_game(MiniGameResult.TIMEOUT)
            return
        
        # プレイヤー移動
        movement = input_handler.get_movement_vector()
        self.player_x += movement[0] * 8
        self.player_x = max(0, min(SCREEN_WIDTH - self.player_width, self.player_x))
        
        # ボール生成
        self.ball_spawn_timer += 1
        if self.ball_spawn_timer >= self.ball_spawn_interval:
            self.ball_spawn_timer = 0
            self._spawn_ball()
        
        # ボール更新
        for ball in self.balls[:]:
            ball["y"] += ball["speed"]
            
            # プレイヤーとの当たり判定
            if (ball["x"] < self.player_x + self.player_width and
                ball["x"] + ball["size"] > self.player_x and
                ball["y"] < self.player_y + self.player_height and
                ball["y"] + ball["size"] > self.player_y):
                
                self.balls.remove(ball)
                self.balls_caught += 1
                self.score += 10
                
                # 成功判定
                if self.balls_caught >= self.target_catches:
                    result = MiniGameResult.PERFECT if self.balls_missed == 0 else MiniGameResult.SUCCESS
                    self._end_game(result)
                    return
            
            # 画面外に出た場合
            elif ball["y"] > SCREEN_HEIGHT:
                self.balls.remove(ball)
                self.balls_missed += 1
                
                # 失敗判定
                if self.balls_missed > 3:
                    self._end_game(MiniGameResult.FAILURE)
                    return
    
    def _spawn_ball(self):
        """ボールを生成"""
        ball = {
            "x": random.randint(20, SCREEN_WIDTH - 40),
            "y": 0,
            "size": 20,
            "speed": 3 + self.difficulty,
            "color": random.choice([COLOR_RED, COLOR_BLUE, COLOR_GREEN, COLOR_YELLOW])
        }
        self.balls.append(ball)
    
    def _end_game(self, result: MiniGameResult):
        """ゲーム終了"""
        self.is_active = False
        self.result = result
        self.score = min(self.max_score, self.score)
    
    def render(self, screen: pygame.Surface):
        """ゲーム描画"""
        # 背景
        screen.fill(COLOR_LIGHT_GRAY)
        
        # プレイヤー（キャッチャー）
        player_rect = pygame.Rect(self.player_x, self.player_y, self.player_width, self.player_height)
        pygame.draw.rect(screen, COLOR_BLUE, player_rect)
        
        # ボール
        for ball in self.balls:
            ball_rect = pygame.Rect(ball["x"], ball["y"], ball["size"], ball["size"])
            pygame.draw.ellipse(screen, ball["color"], ball_rect)
        
        # UI
        font = pygame.font.Font(None, 36)
        
        # スコア
        score_text = font.render(f"キャッチ: {self.balls_caught}/{self.target_catches}", True, COLOR_BLACK)
        screen.blit(score_text, (10, 10))
        
        # ミス
        miss_text = font.render(f"ミス: {self.balls_missed}/3", True, COLOR_RED)
        screen.blit(miss_text, (10, 50))
        
        # 残り時間
        time_text = font.render(f"時間: {self.get_remaining_time():.1f}s", True, COLOR_BLACK)
        screen.blit(time_text, (SCREEN_WIDTH - 150, 10))
        
        # 結果表示
        if not self.is_active and self.result:
            self._render_result(screen)
    
    def _render_result(self, screen: pygame.Surface):
        """結果表示"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        result_texts = {
            MiniGameResult.PERFECT: "パーフェクト！",
            MiniGameResult.SUCCESS: "成功！",
            MiniGameResult.FAILURE: "失敗...",
            MiniGameResult.TIMEOUT: "時間切れ"
        }
        
        result_text = font.render(result_texts[self.result], True, COLOR_WHITE)
        text_rect = result_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(result_text, text_rect)


class MemoryGame(MiniGame):
    """記憶ゲーム - 順番を覚えて再現"""
    
    def __init__(self, pet_type: str, difficulty: int = 1):
        super().__init__(pet_type, difficulty)
        self.sequence = []
        self.player_sequence = []
        self.sequence_length = 3 + difficulty
        self.showing_sequence = True
        self.show_index = 0
        self.show_timer = 0
        self.show_duration = max(30, 60 - difficulty * 5)
        self.buttons = self._create_buttons()
        self.button_states = {}
    
    def _create_buttons(self) -> List[Dict[str, Any]]:
        """ボタンを作成"""
        colors = [COLOR_RED, COLOR_BLUE, COLOR_GREEN, COLOR_YELLOW]
        buttons = []
        
        for i, color in enumerate(colors):
            x = 200 + (i % 2) * 200
            y = 200 + (i // 2) * 150
            buttons.append({
                "id": i,
                "rect": pygame.Rect(x, y, 150, 100),
                "color": color,
                "pressed": False
            })
        
        return buttons
    
    def start(self):
        """ゲーム開始"""
        self.is_active = True
        self.start_time = pygame.time.get_ticks()
        self.sequence = [random.randint(0, 3) for _ in range(self.sequence_length)]
        self.player_sequence.clear()
        self.showing_sequence = True
        self.show_index = 0
        self.show_timer = 0
        self.score = 0
        
        for button in self.buttons:
            button["pressed"] = False
    
    def update(self, input_handler):
        """ゲーム更新"""
        if not self.is_active:
            return
        
        # 時間切れチェック
        if self.is_time_up():
            self._end_game(MiniGameResult.TIMEOUT)
            return
        
        if self.showing_sequence:
            self._update_sequence_display()
        else:
            self._update_player_input(input_handler)
    
    def _update_sequence_display(self):
        """シーケンス表示更新"""
        self.show_timer += 1
        
        if self.show_timer >= self.show_duration:
            self.show_timer = 0
            self.show_index += 1
            
            if self.show_index >= len(self.sequence):
                self.showing_sequence = False
                self.show_index = 0
    
    def _update_player_input(self, input_handler):
        """プレイヤー入力更新"""
        mouse_pos = input_handler.get_mouse_pos()
        mouse_clicked = input_handler.is_mouse_button_just_pressed(1)
        
        if mouse_clicked:
            for button in self.buttons:
                if button["rect"].collidepoint(mouse_pos):
                    self._handle_button_press(button["id"])
                    break
    
    def _handle_button_press(self, button_id: int):
        """ボタン押下処理"""
        self.player_sequence.append(button_id)
        
        # 正解チェック
        current_index = len(self.player_sequence) - 1
        if self.player_sequence[current_index] != self.sequence[current_index]:
            self._end_game(MiniGameResult.FAILURE)
            return
        
        # 完了チェック
        if len(self.player_sequence) == len(self.sequence):
            result = MiniGameResult.PERFECT
            self.score = self.max_score
            self._end_game(result)
    
    def _end_game(self, result: MiniGameResult):
        """ゲーム終了"""
        self.is_active = False
        self.result = result
        if result == MiniGameResult.FAILURE:
            self.score = len(self.player_sequence) * 10
    
    def render(self, screen: pygame.Surface):
        """ゲーム描画"""
        screen.fill(COLOR_GRAY)
        
        # ボタン描画
        for i, button in enumerate(self.buttons):
            color = button["color"]
            
            # シーケンス表示中のハイライト
            if (self.showing_sequence and 
                self.show_index < len(self.sequence) and
                self.sequence[self.show_index] == i and
                self.show_timer < self.show_duration // 2):
                color = tuple(min(255, c + 100) for c in color)
            
            pygame.draw.rect(screen, color, button["rect"])
            pygame.draw.rect(screen, COLOR_BLACK, button["rect"], 3)
        
        # UI
        font = pygame.font.Font(None, 36)
        
        if self.showing_sequence:
            status_text = font.render("順番を覚えてください", True, COLOR_WHITE)
        else:
            status_text = font.render("順番通りにクリックしてください", True, COLOR_WHITE)
        
        text_rect = status_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        screen.blit(status_text, text_rect)
        
        # 進捗
        progress_text = font.render(f"{len(self.player_sequence)}/{len(self.sequence)}", True, COLOR_WHITE)
        screen.blit(progress_text, (10, 10))
        
        # 残り時間
        time_text = font.render(f"時間: {self.get_remaining_time():.1f}s", True, COLOR_WHITE)
        screen.blit(time_text, (SCREEN_WIDTH - 150, 10))
        
        # 結果表示
        if not self.is_active and self.result:
            self._render_result(screen)
    
    def _render_result(self, screen: pygame.Surface):
        """結果表示"""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        font = pygame.font.Font(None, 72)
        result_texts = {
            MiniGameResult.PERFECT: "パーフェクト！",
            MiniGameResult.SUCCESS: "成功！",
            MiniGameResult.FAILURE: "失敗...",
            MiniGameResult.TIMEOUT: "時間切れ"
        }
        
        result_text = font.render(result_texts[self.result], True, COLOR_WHITE)
        text_rect = result_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2))
        screen.blit(result_text, text_rect)


class MiniGameManager:
    """ミニゲーム管理クラス"""
    
    def __init__(self):
        self.available_games = {
            "catch": CatchGame,
            "memory": MemoryGame,
            # 他のゲームも追加可能
        }
        self.current_game: Optional[MiniGame] = None
        self.game_history = []
    
    def start_game(self, game_type: str, pet_type: str, difficulty: int = 1) -> bool:
        """
        ミニゲームを開始
        
        Args:
            game_type: ゲームタイプ
            pet_type: ペットの種類
            difficulty: 難易度
            
        Returns:
            開始成功時True
        """
        if game_type not in self.available_games:
            print(f"未知のゲームタイプ: {game_type}")
            return False
        
        if self.current_game and self.current_game.is_active:
            print("既にゲームが実行中です")
            return False
        
        # ゲームを作成して開始
        game_class = self.available_games[game_type]
        self.current_game = game_class(pet_type, difficulty)
        self.current_game.start()
        
        print(f"ミニゲーム開始: {game_type} (難易度: {difficulty})")
        return True
    
    def update(self, input_handler):
        """ミニゲームを更新"""
        if self.current_game and self.current_game.is_active:
            self.current_game.update(input_handler)
    
    def render(self, screen: pygame.Surface):
        """ミニゲームを描画"""
        if self.current_game:
            self.current_game.render(screen)
    
    def is_game_active(self) -> bool:
        """ゲームがアクティブかチェック"""
        return self.current_game is not None and self.current_game.is_active
    
    def get_game_result(self) -> Optional[Dict[str, Any]]:
        """ゲーム結果を取得"""
        if not self.current_game or self.current_game.is_active:
            return None
        
        result = {
            "game_type": type(self.current_game).__name__,
            "pet_type": self.current_game.pet_type,
            "difficulty": self.current_game.difficulty,
            "result": self.current_game.result.value,
            "score": self.current_game.score,
            "max_score": self.current_game.max_score,
            "trust_bonus": self.current_game.calculate_trust_bonus()
        }
        
        # 履歴に追加
        self.game_history.append(result)
        
        return result
    
    def end_current_game(self):
        """現在のゲームを終了"""
        if self.current_game:
            self.current_game.is_active = False
    
    def get_recommended_game(self, pet_type: str, trust_level: int) -> str:
        """おすすめのゲームを取得"""
        # ペットの種類と信頼度に基づいてゲームを推奨
        if pet_type in ["dog", "ferret"]:
            return "catch"  # 活発なペットにはキャッチゲーム
        elif pet_type in ["cat", "bird"]:
            return "memory"  # 知的なペットには記憶ゲーム
        else:
            return random.choice(list(self.available_games.keys()))
    
    def get_game_history(self) -> List[Dict[str, Any]]:
        """ゲーム履歴を取得"""
        return self.game_history.copy()
    
    def clear_history(self):
        """履歴をクリア"""
        self.game_history.clear()
