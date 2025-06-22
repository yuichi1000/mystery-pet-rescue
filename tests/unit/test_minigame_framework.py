"""
ミニゲームフレームワークの単体テスト
"""

import pytest
import pygame
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.core.minigame import GameConfig, Difficulty, GameScore, GameState
from src.systems.minigame_manager import MinigameManager, MinigameType
from src.minigames.action_game import ActionGame
from src.minigames.memory_game import MemoryGame

class TestGameConfig:
    """ゲーム設定テスト"""
    
    def test_default_config(self):
        """デフォルト設定テスト"""
        config = GameConfig()
        assert config.time_limit == 60.0
        assert config.difficulty == Difficulty.NORMAL
        assert config.max_attempts == 3
        assert config.show_timer == True
        assert config.show_score == True
    
    def test_custom_config(self):
        """カスタム設定テスト"""
        config = GameConfig(
            time_limit=120.0,
            difficulty=Difficulty.HARD,
            max_attempts=5
        )
        assert config.time_limit == 120.0
        assert config.difficulty == Difficulty.HARD
        assert config.max_attempts == 5

class TestGameScore:
    """ゲームスコアテスト"""
    
    def test_score_calculation(self):
        """スコア計算テスト"""
        score = GameScore(points=100, bonus_points=50)
        total = score.calculate_total()
        assert total == 150
        assert score.total_score == 150
    
    def test_empty_score(self):
        """空スコアテスト"""
        score = GameScore()
        total = score.calculate_total()
        assert total == 0

class TestMinigameManager:
    """ミニゲームマネージャーテスト"""
    
    @pytest.fixture
    def screen(self):
        """テスト用画面"""
        pygame.init()
        return pygame.display.set_mode((800, 600))
    
    @pytest.fixture
    def manager(self, screen):
        """テスト用マネージャー"""
        return MinigameManager(screen)
    
    def test_available_games(self, manager):
        """利用可能ゲームテスト"""
        available = manager.get_available_games()
        assert MinigameType.ACTION in available
        assert MinigameType.MEMORY in available
        assert MinigameType.PUZZLE in available  # 将来追加予定
        assert MinigameType.RHYTHM in available  # 将来追加予定
    
    def test_game_availability(self, manager):
        """ゲーム利用可能性テスト"""
        assert manager.is_game_available(MinigameType.ACTION) == True
        assert manager.is_game_available(MinigameType.MEMORY) == True
        assert manager.is_game_available(MinigameType.PUZZLE) == False
        assert manager.is_game_available(MinigameType.RHYTHM) == False
    
    def test_start_available_game(self, manager):
        """利用可能ゲーム開始テスト"""
        config = GameConfig(difficulty=Difficulty.EASY)
        result = manager.start_game(MinigameType.ACTION, config)
        assert result == True
        assert manager.current_game is not None
        assert manager.current_type == MinigameType.ACTION
    
    def test_start_unavailable_game(self, manager):
        """利用不可ゲーム開始テスト"""
        result = manager.start_game(MinigameType.PUZZLE)
        assert result == False
        assert manager.current_game is None
    
    def test_game_stats(self, manager):
        """ゲーム統計テスト"""
        stats = manager.get_game_stats()
        assert MinigameType.ACTION in stats
        assert MinigameType.MEMORY in stats
        
        # 初期統計
        action_stats = stats[MinigameType.ACTION]
        assert action_stats['played'] == 0
        assert action_stats['won'] == 0
        assert action_stats['best_score'] == 0
    
    def test_recommended_difficulty(self, manager):
        """推奨難易度テスト"""
        # 初期状態
        difficulty = manager.get_recommended_difficulty(MinigameType.ACTION)
        assert difficulty == Difficulty.NORMAL
        
        # 統計を模擬的に変更
        manager.game_stats[MinigameType.ACTION]['played'] = 10
        manager.game_stats[MinigameType.ACTION]['won'] = 9
        
        difficulty = manager.get_recommended_difficulty(MinigameType.ACTION)
        assert difficulty == Difficulty.HARD

class TestActionGame:
    """アクションゲームテスト"""
    
    @pytest.fixture
    def screen(self):
        """テスト用画面"""
        pygame.init()
        return pygame.display.set_mode((800, 600))
    
    @pytest.fixture
    def game(self, screen):
        """テスト用ゲーム"""
        config = GameConfig(time_limit=30.0, difficulty=Difficulty.EASY)
        return ActionGame(screen, config)
    
    def test_game_initialization(self, game):
        """ゲーム初期化テスト"""
        assert game.state == GameState.READY
        assert game.player is not None
        assert game.pet is not None
        assert len(game.obstacles) == 0
    
    def test_difficulty_settings(self, screen):
        """難易度設定テスト"""
        easy_game = ActionGame(screen, GameConfig(difficulty=Difficulty.EASY))
        hard_game = ActionGame(screen, GameConfig(difficulty=Difficulty.HARD))
        
        assert easy_game.obstacle_speed < hard_game.obstacle_speed
        assert easy_game.obstacle_spawn_interval > hard_game.obstacle_spawn_interval
    
    def test_win_condition(self, game):
        """勝利条件テスト"""
        # 初期状態では勝利していない
        assert game.check_win_condition() == False
        
        # ペットを救助状態にする
        game.pet.rescued = True
        assert game.check_win_condition() == True

class TestMemoryGame:
    """記憶ゲームテスト"""
    
    @pytest.fixture
    def screen(self):
        """テスト用画面"""
        pygame.init()
        return pygame.display.set_mode((800, 600))
    
    @pytest.fixture
    def game(self, screen):
        """テスト用ゲーム"""
        config = GameConfig(time_limit=60.0, difficulty=Difficulty.NORMAL)
        return MemoryGame(screen, config)
    
    def test_game_initialization(self, game):
        """ゲーム初期化テスト"""
        assert game.state == GameState.READY
        assert len(game.cards) > 0
        assert game.matched_pairs == 0
        assert game.total_pairs > 0
    
    def test_card_pairs(self, game):
        """カードペアテスト"""
        # カード数は偶数である必要がある
        assert len(game.cards) % 2 == 0
        
        # 各IDのカードが2枚ずつある
        card_ids = {}
        for card in game.cards:
            card_ids[card.id] = card_ids.get(card.id, 0) + 1
        
        for count in card_ids.values():
            assert count == 2
    
    def test_difficulty_settings(self, screen):
        """難易度設定テスト"""
        easy_game = MemoryGame(screen, GameConfig(difficulty=Difficulty.EASY))
        hard_game = MemoryGame(screen, GameConfig(difficulty=Difficulty.HARD))
        
        assert len(easy_game.cards) < len(hard_game.cards)
        assert easy_game.flip_time > hard_game.flip_time
    
    def test_win_condition(self, game):
        """勝利条件テスト"""
        # 初期状態では勝利していない
        assert game.check_win_condition() == False
        
        # 全ペアをマッチさせる
        game.matched_pairs = game.total_pairs
        assert game.check_win_condition() == True

def test_framework_integration():
    """フレームワーク統合テスト"""
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # マネージャー作成
    manager = MinigameManager(screen)
    
    # アクションゲーム開始
    config = GameConfig(difficulty=Difficulty.NORMAL, time_limit=30.0)
    assert manager.start_game(MinigameType.ACTION, config) == True
    
    # ゲーム情報取得
    info = manager.get_current_game_info()
    assert info is not None
    assert info['type'] == 'action'
    assert info['state'] == 'ready'
    
    # ゲーム停止
    manager.stop_current_game()
    assert manager.current_game is None
    
    # 記憶ゲーム開始
    assert manager.start_game(MinigameType.MEMORY, config) == True
    
    info = manager.get_current_game_info()
    assert info['type'] == 'memory'
    
    pygame.quit()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
