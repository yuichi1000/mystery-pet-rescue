"""
メインゲームシステム
全システムを統合したゲームループ管理
"""

import pygame
import sys
import time
from typing import Dict, List, Optional, Any
from enum import Enum
from pathlib import Path

from src.core.menu_system import MenuSystem, MenuState
from src.ui.game_ui import GameUI, NotificationType, QuickSlotItem
from src.entities.player import Player
from src.entities.pet import Pet, PetData, PetType
from src.systems.map_system import MapSystem
from src.utils.asset_manager import get_asset_manager
from src.utils.font_manager import get_font_manager

class GameState(Enum):
    """ゲーム状態"""
    MENU = "menu"
    PLAYING = "playing"
    PUZZLE = "puzzle"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"

class Game:
    """メインゲームクラス"""
    
    def __init__(self):
        # Pygame初期化
        pygame.init()
        pygame.mixer.init()
        
        # 画面設定
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("ミステリー・ペット・レスキュー")
        
        # ゲーム状態
        self.current_state = GameState.MENU
        self.running = True
        self.clock = pygame.time.Clock()
        self.target_fps = 60
        
        # システム管理
        self.asset_manager = get_asset_manager()
        self.font_manager = get_font_manager()
        
        # メニューシステム
        self.menu_system = MenuSystem(self.screen)
        
        # ゲーム内UI
        self.game_ui = GameUI(self.screen)
        self.game_ui.set_map_system(self.map_system)
        
        # プレイヤー
        self.player = None
        
        # ペット管理
        self.pets: List[Pet] = []
        self.rescued_pets: List[Pet] = []
        
        # 謎解きシステム（削除済み）
        # self.puzzle_system = PuzzleSystem()
        self.puzzle_ui = None
        
        # マップシステム
        self.map_system = MapSystem()
        
        # ゲーム進行管理
        self.game_objectives = []
        self.current_objective_index = 0
        self.pets_to_rescue = 3  # 救出目標数
        
        # カメラ
        self.camera_x = 0
        self.camera_y = 0
        
        # ゲーム統計
        self.game_start_time = time.time()
        self.total_play_time = 0.0
        
        # デバッグ
        self.debug_mode = False
        self.show_fps = True
        
        print("🎮 メインゲームシステム初期化完了")
    
    def initialize_game(self):
        """ゲーム初期化"""
        print("🔄 ゲーム初期化中...")
        
        # アセット事前読み込み
        self.asset_manager.preload_all_assets()
        
        # プレイヤー作成
        self.player = Player(400, 300)
        
        # ペット作成
        self._create_pets()
        
        # 謎解きUI初期化（削除済み）
        # self.puzzle_ui = PuzzleUI(self.screen, self.puzzle_system)
        
        # マップ読み込み（現在は使用されていない - scenes/game.pyで管理）
        # self.map_system.load_map("realistic_city_v1.json")
        
        # プレイヤー位置をスポーン地点に設定
        spawn_point = self.map_system.get_spawn_point("player")
        if spawn_point:
            self.player.set_position(spawn_point[0], spawn_point[1])
        
        # ペット位置をマップデータに基づいて設定
        self._position_pets_from_map()
        
        # ゲーム目標設定
        self._setup_objectives()
        
        # ゲームUI初期設定
        self._setup_game_ui()
        
        print("✅ ゲーム初期化完了")
    
    def _create_pets(self):
        """ペットを作成"""
        pet_configs = [
            {
                "data": PetData("pet_cat_001", "ミケ", PetType.CAT, "好奇心旺盛", "common", "人懐っこい三毛猫"),
                "position": (600, 200)
            },
            {
                "data": PetData("pet_dog_001", "ポチ", PetType.DOG, "忠実", "common", "忠実な柴犬"),
                "position": (800, 400)
            },
            {
                "data": PetData("pet_cat_002", "シロ", PetType.CAT, "神秘的", "rare", "真っ白な美しい猫"),
                "position": (300, 500)
            },
            {
                "data": PetData("pet_dog_002", "タロウ", PetType.DOG, "元気", "common", "元気いっぱいの子犬"),
                "position": (900, 150)
            }
        ]
        
        for config in pet_configs:
            pet = Pet(config["data"], config["position"][0], config["position"][1])
            self.pets.append(pet)
        
        print(f"🐾 ペット生成完了: {len(self.pets)}匹")
    
    def _position_pets_from_map(self):
        """マップデータに基づいてペットを配置"""
        pet_locations = self.map_system.get_pet_locations()
        
        for i, pet in enumerate(self.pets):
            if i < len(pet_locations):
                x, y = pet_locations[i]
                pet.x = x
                pet.y = y
                pet.rect.x = int(x)
                pet.rect.y = int(y)
                print(f"🐾 {pet.data.name}をマップ位置に配置: ({x}, {y})")
            else:
                print(f"⚠️ {pet.data.name}の配置位置が不足しています")
    
    def _setup_objectives(self):
        """ゲーム目標を設定"""
        self.game_objectives = [
            {
                "title": "ペットを見つけよう",
                "description": f"迷子のペットを{self.pets_to_rescue}匹見つけて救出する",
                "target": self.pets_to_rescue,
                "current": 0,
                "type": "rescue_pets"
            },
            {
                "title": "すべてのペットを救出",
                "description": "残りのペットもすべて救出する",
                "target": len(self.pets),
                "current": 0,
                "type": "rescue_all"
            }
        ]
    
    def _setup_game_ui(self):
        """ゲームUI初期設定"""
        # クイックスロットアイテム設定
        quick_items = [
            QuickSlotItem("treat", "おやつ", "", 5, 0.0, 2.0),
            QuickSlotItem("toy", "おもちゃ", "", 3, 0.0, 5.0),
            QuickSlotItem("rope", "ロープ", "", 1, 0.0, 0.0),
            QuickSlotItem("flashlight", "懐中電灯", "", 1, 0.0, 10.0),
            QuickSlotItem("whistle", "笛", "", 1, 0.0, 3.0),
            QuickSlotItem("food", "ペットフード", "", 8, 0.0, 1.0)
        ]
        
        for i, item in enumerate(quick_items):
            self.game_ui.set_quick_slot(i, item)
        
        # 初期目標設定
        if self.game_objectives:
            obj = self.game_objectives[self.current_objective_index]
            self.game_ui.set_objective(obj["title"], obj["description"], obj["target"])
        
        # 初期通知
        self.game_ui.add_notification("ゲーム開始！迷子のペットを探しましょう", NotificationType.INFO, 4.0)
    
    def run(self):
        """メインゲームループ"""
        print("🚀 ゲーム開始")
        
        while self.running:
            time_delta = self.clock.tick(self.target_fps) / 1000.0
            
            # イベント処理
            events = pygame.event.get()
            self._handle_events(events)
            
            # 更新
            self._update(time_delta)
            
            # 描画
            self._draw()
            
            pygame.display.flip()
        
        # クリーンアップ
        self._cleanup()
    
    def _handle_events(self, events: List[pygame.event.Event]):
        """イベント処理"""
        for event in events:
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.VIDEORESIZE:
                # 解像度変更対応
                self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                self.screen_width = event.w
                self.screen_height = event.h
                
                # UI システムに通知
                if hasattr(self, 'game_ui'):
                    self.game_ui.resize(event.w, event.h)
                if hasattr(self, 'menu_system'):
                    self.menu_system.resize(event.w, event.h)
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F1:
                    self.debug_mode = not self.debug_mode
                elif event.key == pygame.K_F2:
                    self.show_fps = not self.show_fps
                elif event.key == pygame.K_ESCAPE:
                    if self.current_state == GameState.PLAYING:
                        self._pause_game()
                    elif self.current_state == GameState.PUZZLE:
                        self._exit_puzzle()
                    elif self.current_state == GameState.PAUSED:
                        self._resume_game()  # ポーズ中にESCでゲーム再開
        
        # 状態別イベント処理
        if self.current_state == GameState.MENU:
            result = self.menu_system.update(0, events)
            if result == MenuState.GAME:
                self._start_game()
            elif result == MenuState.QUIT:
                self.running = False
        
        elif self.current_state == GameState.PLAYING:
            # ゲーム内UI入力処理
            for event in events:
                self.game_ui.handle_input(event)
        
        elif self.current_state == GameState.PUZZLE:
            if self.puzzle_ui:
                result = self.puzzle_ui.update(0, events)
                if result == "quit":
                    self._exit_puzzle()
        
        elif self.current_state == GameState.PAUSED:
            # ポーズメニューの処理
            result = self.menu_system.update(0, events)
            if result == MenuState.GAME:
                self._resume_game()
            elif result == MenuState.TITLE:
                self._return_to_menu()
            elif result == MenuState.QUIT:
                self.running = False
    
    def _update(self, time_delta: float):
        """更新処理"""
        # 総プレイ時間更新
        if self.current_state == GameState.PLAYING:
            self.total_play_time += time_delta
        
        # 状態別更新
        if self.current_state == GameState.PLAYING:
            self._update_gameplay(time_delta)
        elif self.current_state == GameState.PUZZLE:
            if self.puzzle_ui:
                self.puzzle_ui.update(time_delta, [])
    
    def _update_gameplay(self, time_delta: float):
        """ゲームプレイ更新"""
        if not self.player:
            return
        
        # キー入力取得
        keys = pygame.key.get_pressed()
        keys_pressed = set()
        
        # 移動キー
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            keys_pressed.add(pygame.K_LEFT)
            keys_pressed.add(pygame.K_a)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            keys_pressed.add(pygame.K_RIGHT)
            keys_pressed.add(pygame.K_d)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            keys_pressed.add(pygame.K_UP)
            keys_pressed.add(pygame.K_w)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            keys_pressed.add(pygame.K_DOWN)
            keys_pressed.add(pygame.K_s)
        if keys[pygame.K_LSHIFT]:
            keys_pressed.add(pygame.K_LSHIFT)
        
        # プレイヤー更新
        self.player.update(time_delta, keys_pressed, self.map_system)
        
        # ペット更新
        player_pos = self.player.get_position()
        for pet in self.pets:
            if pet not in self.rescued_pets:
                pet.update(time_delta, player_pos, self.map_system)
        
        # カメラ更新
        self._update_camera()
        
        # ゲームUI更新
        self.game_ui.update(time_delta)
        
        # ペット救出チェック
        self._check_pet_interactions()
        
        # 目標達成チェック
        self._check_objectives()
    
    def _update_camera(self):
        """カメラ更新"""
        if not self.player:
            return
        
        # プレイヤーを中心にカメラ配置
        player_center = self.player.get_center()
        target_x = player_center[0] - self.screen_width // 2
        target_y = player_center[1] - self.screen_height // 2
        
        # スムーズなカメラ移動
        camera_speed = 5.0
        self.camera_x += (target_x - self.camera_x) * camera_speed * (1/60)
        self.camera_y += (target_y - self.camera_y) * camera_speed * (1/60)
        
        # カメラ範囲制限（マップサイズに基づく）
        world_width, world_height = self.map_system.get_map_size()
        if world_width > 0 and world_height > 0:
            self.camera_x = max(0, min(world_width - self.screen_width, self.camera_x))
            self.camera_y = max(0, min(world_height - self.screen_height, self.camera_y))
    
    def _check_pet_interactions(self):
        """ペットとの相互作用チェック"""
        if not self.player:
            return
        
        player_pos = self.player.get_position()
        
        for pet in self.pets:
            if pet in self.rescued_pets:
                continue
            
            # スペースキーでの相互作用
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                if pet.interact(player_pos):
                    # 救出成功
                    if pet.rescue():
                        self.rescued_pets.append(pet)
                        self.game_ui.add_notification(f"{pet.data.name}を救出しました！", NotificationType.SUCCESS, 3.0)
                        
                        # 目標進捗更新
                        if self.current_objective_index < len(self.game_objectives):
                            obj = self.game_objectives[self.current_objective_index]
                            obj["current"] = len(self.rescued_pets)
                            self.game_ui.update_objective_progress(obj["current"])
    
    def _check_objectives(self):
        """目標達成チェック"""
        if self.current_objective_index >= len(self.game_objectives):
            return
        
        current_obj = self.game_objectives[self.current_objective_index]
        
        if current_obj["current"] >= current_obj["target"]:
            # 目標達成
            self.game_ui.add_notification("目標達成！", NotificationType.ACHIEVEMENT, 3.0)
            
            # 次の目標に進む
            self.current_objective_index += 1
            
            if self.current_objective_index < len(self.game_objectives):
                # 次の目標設定
                next_obj = self.game_objectives[self.current_objective_index]
                self.game_ui.set_objective(next_obj["title"], next_obj["description"], next_obj["target"])
                self.game_ui.add_notification(f"新しい目標: {next_obj['title']}", NotificationType.INFO, 4.0)
            else:
                # 全目標達成
                self._game_victory()
    
    def _draw(self):
        """描画処理"""
        # 背景クリア
        self.screen.fill((50, 100, 50))
        
        # 状態別描画
        if self.current_state == GameState.MENU:
            self.menu_system.draw()
        
        elif self.current_state == GameState.PLAYING:
            self._draw_gameplay()
        
        elif self.current_state == GameState.PUZZLE:
            if self.puzzle_ui:
                self.puzzle_ui.draw()
        
        elif self.current_state == GameState.PAUSED:
            # ゲーム画面を暗くして表示
            self._draw_gameplay()
            
            # 半透明オーバーレイ
            overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            self.screen.blit(overlay, (0, 0))
            
            # ポーズメニュー描画
            self._draw_pause_menu()
        
        # デバッグ情報
        if self.debug_mode:
            self._draw_debug_info()
        
        # FPS表示
        if self.show_fps:
            self._draw_fps()
    
    def _draw_gameplay(self):
        """ゲームプレイ描画"""
        # 簡易マップ描画
        self._draw_world()
        
        # プレイヤー描画
        if self.player:
            self.player.draw(self.screen, (self.camera_x, self.camera_y))
        
        # ペット描画
        for pet in self.pets:
            if pet not in self.rescued_pets:
                pet.draw(self.screen, (self.camera_x, self.camera_y))
        
        # ゲームUI描画
        if self.player:
            player_stats = {
                'health': self.player.stats.health,
                'max_health': self.player.stats.max_health,
                'stamina': self.player.stats.stamina,
                'max_stamina': self.player.stats.max_stamina
            }
            
            active_pets = [pet for pet in self.pets if pet not in self.rescued_pets]
            self.game_ui.draw(player_stats, active_pets, self.player.get_position())
    
    def _draw_world(self):
        """世界描画"""
        # マップシステムで描画
        self.map_system.draw(self.screen, self.camera_x, self.camera_y)
    
    def _draw_debug_info(self):
        """デバッグ情報描画"""
        debug_info = [
            f"State: {self.current_state.value}",
            f"Player: {self.player.get_position() if self.player else 'None'}",
            f"Camera: ({int(self.camera_x)}, {int(self.camera_y)})",
            f"Pets: {len(self.pets)} total, {len(self.rescued_pets)} rescued",
            f"Play Time: {int(self.total_play_time)}s",
            f"Objective: {self.current_objective_index + 1}/{len(self.game_objectives)}"
        ]
        
        # デバッグパネル背景
        panel_height = len(debug_info) * 20 + 20
        debug_panel = pygame.Rect(10, 10, 300, panel_height)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), debug_panel)
        pygame.draw.rect(self.screen, (255, 255, 255), debug_panel, 2)
        
        # デバッグテキスト
        for i, info in enumerate(debug_info):
            text_surface = self.font_manager.render_text(info, 14, (255, 255, 255))
            self.screen.blit(text_surface, (15, 15 + i * 20))
    
    def _draw_fps(self):
        """FPS表示"""
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        fps_surface = self.font_manager.render_text(fps_text, 16, (255, 255, 0))
        self.screen.blit(fps_surface, (self.screen_width - 100, 10))
    
    def _draw_pause_menu(self):
        """ポーズメニューを描画"""
        # ポーズメニューパネル
        menu_width = 400
        menu_height = 300
        menu_x = (self.screen_width - menu_width) // 2
        menu_y = (self.screen_height - menu_height) // 2
        
        # パネル背景
        menu_panel = pygame.Rect(menu_x, menu_y, menu_width, menu_height)
        pygame.draw.rect(self.screen, (50, 50, 50), menu_panel)
        pygame.draw.rect(self.screen, (255, 255, 255), menu_panel, 3)
        
        # タイトル
        title_surface = self.font_manager.render_text("ポーズ", 32, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, menu_y + 50))
        self.screen.blit(title_surface, title_rect)
        
        # メニューオプション
        menu_options = [
            "ゲーム再開 (ESC)",
            "設定",
            "セーブ",
            "タイトルに戻る"
        ]
        
        for i, option in enumerate(menu_options):
            option_y = menu_y + 120 + i * 40
            option_surface = self.font_manager.render_text(option, 20, (255, 255, 255))
            option_rect = option_surface.get_rect(center=(self.screen_width // 2, option_y))
            self.screen.blit(option_surface, option_rect)
        
        # 操作説明
        help_text = "ESC: ゲーム再開 / マウス: メニュー選択"
        help_surface = self.font_manager.render_text(help_text, 16, (200, 200, 200))
        help_rect = help_surface.get_rect(center=(self.screen_width // 2, menu_y + menu_height - 30))
        self.screen.blit(help_surface, help_rect)
    
    # ゲーム状態管理メソッド
    def _start_game(self):
        """ゲーム開始"""
        if not self.player:
            self.initialize_game()
        
        self.current_state = GameState.PLAYING
        self.game_start_time = time.time()
        print("🎮 ゲーム開始")
    
    def _pause_game(self):
        """ゲーム一時停止"""
        self.current_state = GameState.PAUSED
        # ポーズメニューの状態を直接設定
        self.menu_system.current_state = MenuState.PAUSE
        print("⏸️ ゲーム一時停止")
    
    def _resume_game(self):
        """ゲーム再開"""
        self.current_state = GameState.PLAYING
        # メニューシステムの状態もリセット
        self.menu_system.current_state = MenuState.GAME
        print("▶️ ゲーム再開")
    
    def _return_to_menu(self):
        """メニューに戻る"""
        self.current_state = GameState.MENU
        self.menu_system.current_state = MenuState.TITLE
        self.menu_system.state_stack.clear()
        print("🏠 メニューに戻る")
    
    def _enter_puzzle(self, puzzle_id: str):
        """謎解きモードに入る"""
        self.current_state = GameState.PUZZLE
        if self.puzzle_ui:
            self.puzzle_ui.start_puzzle(puzzle_id)
        print(f"🧩 謎解き開始: {puzzle_id}")
    
    def _exit_puzzle(self):
        """謎解きモードを終了"""
        self.current_state = GameState.PLAYING
        print("🎮 ゲームに戻る")
    
    def _game_victory(self):
        """ゲーム勝利"""
        self.current_state = GameState.VICTORY
        self.game_ui.add_notification("おめでとうございます！全てのペットを救出しました！", NotificationType.ACHIEVEMENT, 5.0)
        print("🎉 ゲーム勝利！")
    
    def _cleanup(self):
        """クリーンアップ"""
        if hasattr(self, 'menu_system'):
            self.menu_system.cleanup()
        
        pygame.quit()
        print("🧹 ゲーム終了・クリーンアップ完了")

def main():
    """メイン関数"""
    print("🚀 ミステリー・ペット・レスキュー起動中...")
    
    try:
        game = Game()
        game.run()
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
