"""
ゲームフロー管理システム
タイトル→ゲーム→結果の流れを管理
"""

import pygame
import time
from typing import Dict, Any, Optional
from src.core.scene import Scene
from src.scenes.menu import MenuScene
from src.scenes.game import GameScene
from src.scenes.result import ResultScene
from src.systems.audio_system import AudioSystem
from src.utils.language_manager import get_text

class GameFlowManager:
    """ゲームフロー管理クラス"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.current_scene: Optional[Scene] = None
        self.scenes: Dict[str, Scene] = {}
        self.running = True
        
        # 音楽システム初期化
        self.audio_system = AudioSystem()
        
        # ゲーム状態
        self.game_start_time = 0
        self.game_result = {
            'pets_rescued': 0,
            'total_pets': 4,
            'time_taken': 0,
            'score': 0
        }
        
        # シーンを初期化
        self._initialize_scenes()
        
        # 最初のシーンを設定
        self.change_scene("menu")
    
    def update_window_title(self):
        """ウィンドウタイトルを現在の言語に応じて更新"""
        title = get_text("game_title")
        pygame.display.set_caption(title)
        print(f"🪟 ウィンドウタイトル更新: '{title}'")
    
    def _initialize_scenes(self):
        """シーンを初期化"""
        # メニューシーンは常に利用可能
        menu_scene = MenuScene(self.screen)
        menu_scene.set_game_flow_manager(self)  # 参照を設定
        self.scenes["menu"] = menu_scene
        
        # ゲームシーンと結果シーンは必要に応じて作成
        # （ゲーム開始時に最新の状態で作成するため）
    
    def change_scene(self, scene_name: str) -> bool:
        """
        シーンを変更
        
        Args:
            scene_name: 変更先のシーン名
            
        Returns:
            bool: 変更成功時True
        """
        if scene_name == "quit":
            self.running = False
            self.audio_system.stop_bgm()
            self.audio_system.stop_all_sfx()  # 全効果音停止
            return True
        
        # 現在のシーンを終了
        if self.current_scene:
            self.current_scene.exit()
        
        # シーン切り替え時に効果音を停止
        self.audio_system.stop_all_sfx()
        
        # 新しいシーンを作成または取得
        if scene_name == "game":
            # ゲーム開始時の処理
            self.game_start_time = time.time()
            self.game_result = {
                'pets_rescued': 0,
                'total_pets': 4,
                'time_taken': 0,
                'score': 0
            }
            self.scenes["game"] = GameScene(self.screen, self)
            # ゲームBGM再生
            self.audio_system.play_bgm("residential_bgm")
            
        elif scene_name == "result":
            # ゲーム終了時の処理
            if "game" in self.scenes:
                game_scene = self.scenes["game"]
                self.game_result = self._collect_game_result(game_scene)
            self.scenes["result"] = ResultScene(self.screen, self.game_result)
            
            # 結果に応じてBGM再生
            if self.game_result.get('pets_rescued', 0) >= self.game_result.get('total_pets', 4):
                # 勝利BGM
                self.audio_system.play_bgm("victory_bgm")
            else:
                # ゲームオーバーBGM
                self.audio_system.play_bgm("gameover_bgm")
            
        elif scene_name == "menu":
            # メニューBGM再生
            self.audio_system.play_bgm("menu_bgm")
        
        # シーンが存在しない場合はメニューに戻る
        if scene_name not in self.scenes:
            scene_name = "menu"
            self.audio_system.play_bgm("menu_bgm")
        
        # 新しいシーンを設定
        self.current_scene = self.scenes[scene_name]
        self.current_scene.enter()
        
        return True
    
    def _collect_game_result(self, game_scene) -> Dict[str, Any]:
        """
        ゲームシーンから結果を収集
        
        Args:
            game_scene: ゲームシーンインスタンス
            
        Returns:
            Dict[str, Any]: ゲーム結果
        """
        # GameSceneの新しいget_game_result()メソッドを使用
        if hasattr(game_scene, 'get_game_result'):
            return game_scene.get_game_result()
        
        # フォールバック：従来の方法
        game_time = time.time() - self.game_start_time
        
        pets_rescued = 0
        total_pets = 4
        
        if hasattr(game_scene, 'pets_rescued'):
            pets_rescued = len(game_scene.pets_rescued)
        
        if hasattr(game_scene, 'pets'):
            total_pets = len(game_scene.pets)
        
        # スコア計算
        base_score = pets_rescued * 1000
        time_bonus = max(0, 300 - int(game_time)) * 10  # 5分以内でボーナス
        completion_bonus = 2000 if pets_rescued == total_pets else 0
        total_score = base_score + time_bonus + completion_bonus
        
        return {
            'pets_rescued': pets_rescued,
            'total_pets': total_pets,
            'time_taken': game_time,
            'score': total_score
        }
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        if not self.current_scene:
            return
        
        # 現在のシーンにイベントを渡す
        next_scene = self.current_scene.handle_event(event)
        
        # シーン変更が要求された場合
        if next_scene:
            self.change_scene(next_scene)
    
    def update(self, time_delta: float):
        """更新処理"""
        if not self.current_scene:
            return
        
        # 現在のシーンを更新
        next_scene = self.current_scene.update(time_delta)
        
        # シーン変更が要求された場合
        if next_scene:
            self.change_scene(next_scene)
    
    def draw(self, surface: pygame.Surface):
        """描画処理"""
        if self.current_scene:
            self.current_scene.draw(surface)
    
    def is_running(self) -> bool:
        """ゲームが実行中かどうか"""
        return self.running
    
    def get_current_scene_name(self) -> str:
        """現在のシーン名を取得"""
        for name, scene in self.scenes.items():
            if scene == self.current_scene:
                return name
        return "unknown"
    
    def notify_game_complete(self, result_data: Dict[str, Any]):
        """
        ゲーム完了通知
        ゲームシーンからの完了通知を受け取る
        
        Args:
            result_data: ゲーム結果データ
        """
        self.game_result.update(result_data)
        self.change_scene("result")
    
    def notify_pet_rescued(self, pet_id: str):
        """
        ペット救出通知
        
        Args:
            pet_id: 救出されたペットのID
        """
        self.game_result['pets_rescued'] += 1
        
        # 全ペット救出チェック
        if self.game_result['pets_rescued'] >= self.game_result['total_pets']:
            # 少し遅延してから結果画面に移行
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000)  # 2秒後
    
    def get_game_stats(self) -> Dict[str, Any]:
        """現在のゲーム統計を取得"""
        current_time = time.time() - self.game_start_time if self.game_start_time > 0 else 0
        
        return {
            'pets_rescued': self.game_result['pets_rescued'],
            'total_pets': self.game_result['total_pets'],
            'time_elapsed': current_time,
            'score': self.game_result['score']
        }
    
    def game_over(self, reason: str = "unknown"):
        """
        ゲームオーバー処理
        
        Args:
            reason: 敗北理由 ("time_up", "no_lives", "other")
        """
        print(f"💀 ゲームオーバー: {reason}")
        
        # 現在のゲームシーンから結果を収集
        if hasattr(self.current_scene, 'get_game_result'):
            result_data = self.current_scene.get_game_result()
            result_data['defeat_reason'] = reason
            
            # 結果画面に遷移（ただし、新しい実装では直接メニューに戻る）
            print("🏠 ゲームオーバー後、メニューに戻ります")
            # 実際の処理はGameSceneで行われるため、ここでは何もしない
        else:
            print("⚠️ ゲーム結果を取得できませんでした")
            self.change_scene("menu")
