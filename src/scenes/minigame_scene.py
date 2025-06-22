"""
ミニゲームシーン
ミニゲームの選択と実行を管理するシーン
"""

import pygame
from typing import Optional

from src.core.scene import Scene
from src.systems.minigame_manager import MinigameManager, MinigameType
from src.core.minigame import GameConfig, Difficulty, GameScore

class MinigameScene(Scene):
    """ミニゲームシーンクラス"""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        
        # ミニゲームマネージャー
        self.minigame_manager = MinigameManager(screen)
        
        # 状態管理
        self.in_game = False
        self.selected_game_type = None
        self.current_difficulty = Difficulty.NORMAL
        self.current_time_limit = 60.0
        
        # 背景色
        self.background_color = (240, 248, 255)
        
        # フォント
        self.fonts = {
            'title': pygame.font.Font(None, 48),
            'large': pygame.font.Font(None, 36),
            'medium': pygame.font.Font(None, 24),
            'small': pygame.font.Font(None, 18)
        }
        
        self._setup_callbacks()
    
    def _setup_callbacks(self) -> None:
        """コールバック設定"""
        self.minigame_manager.set_callbacks(
            on_complete=self._on_game_complete,
            on_failed=self._on_game_failed
        )
    
    def enter(self) -> None:
        """シーン開始"""
        self.in_game = False
    
    def exit(self) -> None:
        """シーン終了"""
        self.minigame_manager.stop_current_game()
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """イベント処理"""
        # ゲーム中の場合はミニゲームにイベントを渡す
        if self.in_game:
            if self.minigame_manager.handle_event(event):
                return None
            
            # ESCキーでゲーム終了
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self._exit_game()
                return None
        else:
            # メニュー画面でのキー操作
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    self._start_selected_game(MinigameType.ACTION)
                elif event.key == pygame.K_2:
                    self._start_selected_game(MinigameType.MEMORY)
                elif event.key == pygame.K_ESCAPE:
                    return "menu"
                elif event.key == pygame.K_d:
                    self._cycle_difficulty()
                elif event.key == pygame.K_t:
                    self._cycle_time_limit()
        
        return None
    
    def _start_selected_game(self, game_type: MinigameType) -> None:
        """選択されたゲームを開始"""
        if not self.minigame_manager.is_game_available(game_type):
            return
        
        # ゲーム設定作成
        config = GameConfig(
            difficulty=self.current_difficulty,
            time_limit=self.current_time_limit,
            show_timer=True,
            show_score=True,
            enable_sound=True,
            enable_animations=True
        )
        
        # ゲーム開始
        if self.minigame_manager.start_game(game_type, config):
            self.in_game = True
            self.selected_game_type = game_type
    
    def _exit_game(self) -> None:
        """ゲーム終了"""
        self.minigame_manager.stop_current_game()
        self.in_game = False
        self.selected_game_type = None
    
    def _cycle_difficulty(self) -> None:
        """難易度切り替え"""
        difficulties = [Difficulty.EASY, Difficulty.NORMAL, Difficulty.HARD]
        current_index = difficulties.index(self.current_difficulty)
        self.current_difficulty = difficulties[(current_index + 1) % len(difficulties)]
    
    def _cycle_time_limit(self) -> None:
        """制限時間切り替え"""
        time_limits = [30.0, 60.0, 90.0, 120.0]
        if self.current_time_limit in time_limits:
            current_index = time_limits.index(self.current_time_limit)
            self.current_time_limit = time_limits[(current_index + 1) % len(time_limits)]
        else:
            self.current_time_limit = 60.0
    
    def _on_game_complete(self, game_type: MinigameType, score: GameScore, success: bool) -> None:
        """ゲーム完了コールバック"""
        print(f"ゲーム完了: {game_type.value}, スコア: {score.total_score}")
        # 3秒後に自動でメニューに戻る
        pygame.time.set_timer(pygame.USEREVENT + 1, 3000)
    
    def _on_game_failed(self, game_type: MinigameType, score: GameScore, success: bool) -> None:
        """ゲーム失敗コールバック"""
        print(f"ゲーム失敗: {game_type.value}, スコア: {score.total_score}")
        # 3秒後に自動でメニューに戻る
        pygame.time.set_timer(pygame.USEREVENT + 1, 3000)
    
    def update(self, time_delta: float) -> Optional[str]:
        """更新処理"""
        # 自動終了タイマーチェック
        for event in pygame.event.get():
            if event.type == pygame.USEREVENT + 1:
                pygame.time.set_timer(pygame.USEREVENT + 1, 0)  # タイマー停止
                self._exit_game()
        
        # ミニゲーム更新
        if self.in_game:
            self.minigame_manager.update(time_delta)
        
        return None
    
    def draw(self, surface: pygame.Surface) -> None:
        """描画処理"""
        # 背景
        surface.fill(self.background_color)
        
        if self.in_game:
            # ミニゲーム描画
            self.minigame_manager.draw(surface)
        else:
            # メニュー画面描画
            self._draw_menu(surface)
    
    def _draw_menu(self, surface: pygame.Surface) -> None:
        """メニュー画面描画"""
        # タイトル
        title_text = self.fonts['title'].render("ミニゲーム選択", True, (50, 50, 50))
        title_rect = title_text.get_rect(center=(surface.get_width() // 2, 80))
        surface.blit(title_text, title_rect)
        
        # ゲーム選択
        y_offset = 150
        available_games = self.minigame_manager.get_available_games()
        
        for i, (game_type, description) in enumerate(available_games.items()):
            if self.minigame_manager.is_game_available(game_type):
                # 利用可能なゲーム
                color = (33, 150, 243)
                key_text = f"{i + 1}. "
            else:
                # 利用不可能なゲーム
                color = (150, 150, 150)
                key_text = f"   "
            
            game_text = f"{key_text}{game_type.value.upper()}: {description}"
            text_surface = self.fonts['medium'].render(game_text, True, color)
            surface.blit(text_surface, (100, y_offset))
            y_offset += 40
        
        # 設定表示
        y_offset += 20
        
        # 難易度
        difficulty_text = f"D. 難易度: {self.current_difficulty.value.upper()}"
        text_surface = self.fonts['medium'].render(difficulty_text, True, (76, 175, 80))
        surface.blit(text_surface, (100, y_offset))
        y_offset += 30
        
        # 制限時間
        time_text = f"T. 制限時間: {self.current_time_limit:.0f}秒"
        text_surface = self.fonts['medium'].render(time_text, True, (255, 152, 0))
        surface.blit(text_surface, (100, y_offset))
        y_offset += 50
        
        # 統計表示
        self._draw_stats(surface, y_offset)
        
        # 操作説明
        instructions = [
            "1/2: ゲーム選択",
            "D: 難易度変更",
            "T: 制限時間変更",
            "ESC: メニューに戻る"
        ]
        
        instruction_y = surface.get_height() - 120
        for instruction in instructions:
            text_surface = self.fonts['small'].render(instruction, True, (100, 100, 100))
            surface.blit(text_surface, (100, instruction_y))
            instruction_y += 20
    
    def _draw_stats(self, surface: pygame.Surface, start_y: int) -> None:
        """統計表示"""
        stats_title = self.fonts['large'].render("ゲーム統計", True, (50, 50, 50))
        surface.blit(stats_title, (100, start_y))
        
        y_offset = start_y + 40
        stats = self.minigame_manager.get_game_stats()
        
        for game_type, stat in stats.items():
            if self.minigame_manager.is_game_available(game_type):
                win_rate = (stat['won'] / stat['played'] * 100) if stat['played'] > 0 else 0
                
                game_name = game_type.value.upper()
                stat_text = f"{game_name}: {stat['played']}回 | 勝率{win_rate:.1f}% | 最高{stat['best_score']}点"
                
                text_surface = self.fonts['small'].render(stat_text, True, (100, 100, 100))
                surface.blit(text_surface, (120, y_offset))
                y_offset += 25
