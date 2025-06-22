"""
ミニゲームマネージャー
ミニゲームの管理、選択、実行を行う
"""

import pygame
from typing import Dict, Type, Optional, Callable, Any
from enum import Enum

from src.core.minigame import MinigameBase, GameConfig, Difficulty, GameScore
from src.minigames.action_game import ActionGame
from src.minigames.memory_game import MemoryGame

class MinigameType(Enum):
    """ミニゲームタイプ"""
    ACTION = "action"
    MEMORY = "memory"
    # 将来追加予定
    PUZZLE = "puzzle"      # v1.1で追加予定
    RHYTHM = "rhythm"      # v2.0で追加予定

class MinigameManager:
    """ミニゲームマネージャークラス"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        
        # 利用可能なミニゲーム（v1.0）
        self.available_games: Dict[MinigameType, Type[MinigameBase]] = {
            MinigameType.ACTION: ActionGame,
            MinigameType.MEMORY: MemoryGame
        }
        
        # 将来追加予定のゲーム（プレースホルダー）
        self.future_games: Dict[MinigameType, str] = {
            MinigameType.PUZZLE: "v1.1で追加予定",
            MinigameType.RHYTHM: "v2.0で追加予定"
        }
        
        # 現在のゲーム
        self.current_game: Optional[MinigameBase] = None
        self.current_type: Optional[MinigameType] = None
        
        # ゲーム結果コールバック
        self.on_game_complete: Optional[Callable] = None
        self.on_game_failed: Optional[Callable] = None
        
        # ゲーム統計
        self.game_stats = {
            MinigameType.ACTION: {
                'played': 0,
                'won': 0,
                'best_score': 0,
                'total_time': 0.0
            },
            MinigameType.MEMORY: {
                'played': 0,
                'won': 0,
                'best_score': 0,
                'total_time': 0.0
            }
        }
    
    def is_game_available(self, game_type: MinigameType) -> bool:
        """ゲームが利用可能かチェック"""
        return game_type in self.available_games
    
    def get_available_games(self) -> Dict[MinigameType, str]:
        """利用可能なゲーム一覧取得"""
        games = {}
        
        # 利用可能なゲーム
        for game_type in self.available_games:
            games[game_type] = self._get_game_description(game_type)
        
        # 将来追加予定のゲーム
        for game_type, description in self.future_games.items():
            games[game_type] = description
        
        return games
    
    def _get_game_description(self, game_type: MinigameType) -> str:
        """ゲーム説明取得"""
        descriptions = {
            MinigameType.ACTION: "障害物を避けてペットに近づくアクションゲーム",
            MinigameType.MEMORY: "ペットのカードでペアを作る記憶ゲーム",
            MinigameType.PUZZLE: "パズルを解いてペットを救出（v1.1で追加予定）",
            MinigameType.RHYTHM: "音楽に合わせてペットと踊るリズムゲーム（v2.0で追加予定）"
        }
        return descriptions.get(game_type, "説明なし")
    
    def start_game(self, game_type: MinigameType, config: GameConfig = None) -> bool:
        """ミニゲーム開始"""
        if not self.is_game_available(game_type):
            print(f"ゲーム {game_type.value} は利用できません")
            return False
        
        # 現在のゲームを終了
        if self.current_game:
            self.stop_current_game()
        
        # 新しいゲームを作成
        game_class = self.available_games[game_type]
        self.current_game = game_class(self.screen, config)
        self.current_type = game_type
        
        # コールバック設定
        self.current_game.set_callbacks(
            on_success=self._handle_game_success,
            on_failure=self._handle_game_failure,
            on_timeout=self._handle_game_timeout,
            on_score_update=self._handle_score_update
        )
        
        # 統計更新
        self.game_stats[game_type]['played'] += 1
        
        print(f"ミニゲーム開始: {game_type.value}")
        return True
    
    def stop_current_game(self) -> None:
        """現在のゲームを停止"""
        if self.current_game:
            print(f"ミニゲーム停止: {self.current_type.value}")
            self.current_game = None
            self.current_type = None
    
    def update(self, time_delta: float) -> None:
        """更新処理"""
        if self.current_game:
            self.current_game.update(time_delta)
    
    def draw(self, surface: pygame.Surface) -> None:
        """描画処理"""
        if self.current_game:
            self.current_game.draw(surface)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理"""
        if self.current_game:
            return self.current_game.handle_event(event)
        return False
    
    def _handle_game_success(self, score: GameScore) -> None:
        """ゲーム成功処理"""
        if self.current_type:
            stats = self.game_stats[self.current_type]
            stats['won'] += 1
            stats['best_score'] = max(stats['best_score'], score.total_score)
            stats['total_time'] += score.time_taken
            
            print(f"ゲーム成功! スコア: {score.total_score}")
            
            if self.on_game_complete:
                self.on_game_complete(self.current_type, score, True)
    
    def _handle_game_failure(self, score: GameScore) -> None:
        """ゲーム失敗処理"""
        if self.current_type:
            stats = self.game_stats[self.current_type]
            stats['total_time'] += score.time_taken
            
            print(f"ゲーム失敗... スコア: {score.total_score}")
            
            if self.on_game_failed:
                self.on_game_failed(self.current_type, score, False)
    
    def _handle_game_timeout(self, score: GameScore) -> None:
        """ゲームタイムアウト処理"""
        if self.current_type:
            stats = self.game_stats[self.current_type]
            stats['total_time'] += score.time_taken
            
            print(f"ゲームタイムアウト... スコア: {score.total_score}")
            
            if self.on_game_failed:
                self.on_game_failed(self.current_type, score, False)
    
    def _handle_score_update(self, score: GameScore) -> None:
        """スコア更新処理"""
        # リアルタイムスコア更新の処理
        pass
    
    def get_game_stats(self, game_type: MinigameType = None) -> Dict[str, Any]:
        """ゲーム統計取得"""
        if game_type:
            return self.game_stats.get(game_type, {})
        return self.game_stats.copy()
    
    def reset_stats(self, game_type: MinigameType = None) -> None:
        """統計リセット"""
        if game_type:
            if game_type in self.game_stats:
                self.game_stats[game_type] = {
                    'played': 0,
                    'won': 0,
                    'best_score': 0,
                    'total_time': 0.0
                }
        else:
            for game_type in self.game_stats:
                self.game_stats[game_type] = {
                    'played': 0,
                    'won': 0,
                    'best_score': 0,
                    'total_time': 0.0
                }
    
    def set_callbacks(self, on_complete: Callable = None, on_failed: Callable = None) -> None:
        """コールバック設定"""
        self.on_game_complete = on_complete
        self.on_game_failed = on_failed
    
    def get_current_game_info(self) -> Optional[Dict[str, Any]]:
        """現在のゲーム情報取得"""
        if self.current_game:
            info = self.current_game.get_game_info()
            info['type'] = self.current_type.value
            return info
        return None
    
    def pause_current_game(self) -> bool:
        """現在のゲームを一時停止"""
        if self.current_game:
            self.current_game.pause_game()
            return True
        return False
    
    def resume_current_game(self) -> bool:
        """現在のゲームを再開"""
        if self.current_game:
            self.current_game.resume_game()
            return True
        return False
    
    def reset_current_game(self) -> bool:
        """現在のゲームをリセット"""
        if self.current_game:
            self.current_game.reset_game()
            return True
        return False
    
    def create_game_config(self, difficulty: Difficulty = Difficulty.NORMAL,
                          time_limit: float = 60.0, **kwargs) -> GameConfig:
        """ゲーム設定作成"""
        return GameConfig(
            difficulty=difficulty,
            time_limit=time_limit,
            **kwargs
        )
    
    def get_recommended_difficulty(self, game_type: MinigameType) -> Difficulty:
        """推奨難易度取得（統計に基づく）"""
        if game_type not in self.game_stats:
            return Difficulty.NORMAL
        
        stats = self.game_stats[game_type]
        
        if stats['played'] == 0:
            return Difficulty.NORMAL
        
        win_rate = stats['won'] / stats['played']
        
        if win_rate > 0.8:
            return Difficulty.HARD
        elif win_rate < 0.3:
            return Difficulty.EASY
        else:
            return Difficulty.NORMAL
