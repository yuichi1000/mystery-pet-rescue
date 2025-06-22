"""
ゲームシーン
メインゲームプレイを管理
"""

import pygame
import time
from typing import Optional, List, Dict, Any
from src.core.scene import Scene
from src.entities.player import Player
from src.entities.pet import Pet, PetData, PetType
from src.systems.puzzle_system import PuzzleSystem
from src.systems.map_system import MapSystem
from src.ui.game_ui import GameUI, NotificationType, QuickSlotItem
from src.ui.puzzle_ui import PuzzleUI
from src.utils.asset_manager import get_asset_manager
from src.utils.font_manager import get_font_manager

class GameScene(Scene):
    """ゲームシーン"""
    
    def __init__(self, screen: pygame.Surface, flow_manager=None):
        super().__init__(screen)
        self.flow_manager = flow_manager
        
        # ゲーム要素の初期化
        self._initialize_game_elements()
        
        # ゲーム状態
        self.paused = False
        self.game_over = False
        self.victory = False
        self.pets_rescued = []
        
        # 統計情報
        self.start_time = time.time()
        self.total_pets = len(self.pets)
    
    def _initialize_game_elements(self):
        """ゲーム要素を初期化"""
        # アセットマネージャーとフォントマネージャー
        self.asset_manager = get_asset_manager()
        self.font_manager = get_font_manager()
        
        # プレイヤー初期化
        self.player = Player(x=100, y=100)
        
        # マップシステム初期化
        self.map_system = MapSystem()
        
        # デフォルトマップを読み込み
        if not self.map_system.load_map("residential.json"):
            print("⚠️ マップファイルが見つからないため、デフォルトマップを使用します")
        
        # ペット初期化
        self.pets = self._create_pets()
        
        # パズルシステム初期化
        self.puzzle_system = PuzzleSystem()
        self.puzzle_ui = PuzzleUI(self.screen, self.puzzle_system)
        self.current_puzzle = None
        
        # UI初期化
        self.game_ui = GameUI(self.screen)
        
        # カメラオフセット
        self.camera_x = 0
        self.camera_y = 0
    
    def _create_pets(self) -> List[Pet]:
        """ペットを作成"""
        pets = []
        
        # 犬
        dog_data = PetData(
            pet_id="dog_001",
            name="ポチ",
            pet_type=PetType.DOG,
            personality="friendly",
            rarity="common",
            description="人懐っこい茶色の犬"
        )
        dog = Pet(dog_data, x=300, y=200)
        pets.append(dog)
        
        # 猫
        cat_data = PetData(
            pet_id="cat_001", 
            name="ミケ",
            pet_type=PetType.CAT,
            personality="shy",
            rarity="common",
            description="三毛猫の女の子"
        )
        cat = Pet(cat_data, x=500, y=300)
        pets.append(cat)
        
        # うさぎ
        rabbit_data = PetData(
            pet_id="rabbit_001",
            name="ミミ",
            pet_type=PetType.RABBIT,
            personality="gentle",
            rarity="uncommon",
            description="白いうさぎ"
        )
        rabbit = Pet(rabbit_data, x=200, y=400)
        pets.append(rabbit)
        
        # 鳥
        bird_data = PetData(
            pet_id="bird_001",
            name="ピーちゃん",
            pet_type=PetType.BIRD,
            personality="energetic",
            rarity="rare",
            description="カラフルなインコ"
        )
        bird = Pet(bird_data, x=400, y=150)
        pets.append(bird)
        
        return pets
    
    def enter(self) -> None:
        """シーンに入る時の処理"""
        self.start_time = time.time()
        self.pets_rescued = []
        self.game_over = False
        self.victory = False
        self.paused = False
        
        # UIに初期状態を設定
        self.game_ui.add_notification("ペットを探しましょう！", NotificationType.INFO)
        self._update_ui_stats()
    
    def exit(self) -> None:
        """シーンから出る時の処理"""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.current_puzzle:
                    # パズル中の場合はパズルを終了
                    self.current_puzzle = None
                    self.puzzle_ui.hide()
                else:
                    # ゲームを一時停止してメニューに戻る
                    return "menu"
            
            elif event.key == pygame.K_p:
                # ポーズ切り替え
                self.paused = not self.paused
                if self.paused:
                    self.game_ui.add_notification("ゲーム一時停止", NotificationType.INFO)
                else:
                    self.game_ui.add_notification("ゲーム再開", NotificationType.INFO)
        
        elif event.type == pygame.USEREVENT + 1:
            # ゲーム完了タイマー
            if self.victory:
                return "result"
        
        # パズル中の場合はパズルUIにイベントを渡す
        if self.current_puzzle:
            puzzle_result = self.puzzle_ui.handle_event(event)
            if puzzle_result == "solved":
                self._handle_puzzle_solved()
            elif puzzle_result == "failed":
                self._handle_puzzle_failed()
            elif puzzle_result == "cancelled":
                self.current_puzzle = None
                self.puzzle_ui.hide()
        else:
            # 通常のゲームイベント処理
            self.player.handle_event(event)
            self.game_ui.handle_input(event)
        
        return None
    
    def update(self, time_delta: float) -> Optional[str]:
        """更新処理"""
        if self.paused or self.game_over:
            return None
        
        # プレイヤー更新
        keys_pressed = pygame.key.get_pressed()
        self.player.update(time_delta, keys_pressed, self.map_system)
        
        # カメラ更新
        self._update_camera()
        
        # ペットとの衝突判定
        self._check_pet_interactions()
        
        # パズル更新
        if self.current_puzzle:
            self.puzzle_ui.update(time_delta)
        
        # UI更新
        self.game_ui.update(time_delta)
        self._update_ui_stats()
        
        # 勝利条件チェック
        if len(self.pets_rescued) >= self.total_pets and not self.victory:
            self.victory = True
            self.game_ui.add_notification("全てのペットを救出しました！", NotificationType.SUCCESS)
            # 2秒後に結果画面に移行
            pygame.time.set_timer(pygame.USEREVENT + 1, 2000)
        
        return None
    
    def draw(self, surface: pygame.Surface) -> None:
        """描画処理"""
        # 背景クリア
        surface.fill((50, 100, 50))  # 緑っぽい背景
        
        # マップ描画
        self.map_system.draw(surface, self.camera_x, self.camera_y)
        
        # ペット描画
        for pet in self.pets:
            if pet.data.pet_id not in self.pets_rescued:
                pet.draw(surface, (self.camera_x, self.camera_y))
        
        # プレイヤー描画
        camera_offset = (self.camera_x, self.camera_y)
        self.player.draw(surface, camera_offset)
        
        # パズルUI描画
        if self.current_puzzle:
            self.puzzle_ui.draw(surface)
        
        # ゲームUI描画
        player_stats = {
            'health': self.player.stats.health,
            'max_health': self.player.stats.max_health,
            'stamina': self.player.stats.stamina,
            'max_stamina': self.player.stats.max_stamina
        }
        self.game_ui.draw(player_stats, [], (self.player.x, self.player.y))
        
        # ポーズ表示
        if self.paused:
            self._draw_pause_overlay(surface)
    
    def _update_camera(self):
        """カメラ位置を更新"""
        # プレイヤーを中心にカメラを配置
        target_x = self.player.x - self.screen.get_width() // 2
        target_y = self.player.y - self.screen.get_height() // 2
        
        # スムーズなカメラ移動
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        
        # カメラ範囲制限（必要に応じて）
        self.camera_x = max(0, min(self.camera_x, 1000))
        self.camera_y = max(0, min(self.camera_y, 1000))
    
    def _check_pet_interactions(self):
        """ペットとの相互作用をチェック"""
        player_rect = pygame.Rect(self.player.x - 20, self.player.y - 20, 40, 40)
        
        for pet in self.pets:
            if pet.data.pet_id in self.pets_rescued:
                continue
            
            pet_rect = pygame.Rect(pet.x - 20, pet.y - 20, 40, 40)
            
            if player_rect.colliderect(pet_rect):
                # ペットとの接触時にパズル開始
                if not self.current_puzzle:
                    self._start_pet_puzzle(pet)
    
    def _start_pet_puzzle(self, pet: Pet):
        """ペットパズルを開始"""
        # ペットタイプに応じたパズルIDを決定
        puzzle_id = f"pet_{pet.data.pet_type.value}_puzzle"
        puzzle_data = self.puzzle_system.get_puzzle_data(puzzle_id)
        
        if puzzle_data:
            puzzle_data['pet_id'] = pet.data.pet_id  # ペットIDを追加
            self.current_puzzle = puzzle_data
            self.puzzle_ui.show_puzzle(puzzle_data)
        else:
            # パズルが見つからない場合は簡単な相互作用
            self.game_ui.add_notification(f"{pet.data.name}と仲良くなりました！", NotificationType.SUCCESS)
            self._rescue_pet(pet)
        self.game_ui.add_notification(f"{pet.data.name}を見つけました！", NotificationType.INFO)
    
    def _handle_puzzle_solved(self):
        """パズル解決時の処理"""
        if self.current_puzzle:
            pet_id = self.current_puzzle.get('pet_id')
            if pet_id:
                self.pets_rescued.append(pet_id)
                self.game_ui.add_notification("ペットを救出しました！", NotificationType.SUCCESS)
                
                # フローマネージャーに通知
                if self.flow_manager:
                    self.flow_manager.notify_pet_rescued(pet_id)
        
        self.current_puzzle = None
        self.puzzle_ui.hide()
    
    def _handle_puzzle_failed(self):
        """パズル失敗時の処理"""
        self.game_ui.add_notification("もう一度挑戦してみましょう", NotificationType.WARNING)
        self.current_puzzle = None
        self.puzzle_ui.hide()
    
    def _update_ui_stats(self):
        """UI統計情報を更新"""
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        stats = {
            'pets_rescued': len(self.pets_rescued),
            'total_pets': self.total_pets,
            'time': f"{minutes:02d}:{seconds:02d}"
        }
        
        self.game_ui.update_stats(stats)
    
    def _draw_pause_overlay(self, surface: pygame.Surface):
        """ポーズオーバーレイを描画"""
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # ポーズテキスト
        font = self.font_manager.get_font("default", 48)
        pause_text = font.render("PAUSED", True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(surface.get_width()//2, surface.get_height()//2))
        surface.blit(pause_text, pause_rect)
        
        # 操作説明
        help_font = self.font_manager.get_font("default", 24)
        help_text = help_font.render("P: 再開, ESC: メニューに戻る", True, (200, 200, 200))
        help_rect = help_text.get_rect(center=(surface.get_width()//2, surface.get_height()//2 + 60))
        surface.blit(help_text, help_rect)
