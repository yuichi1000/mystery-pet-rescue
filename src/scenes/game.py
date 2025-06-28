"""
ゲームシーン
メインゲームプレイを管理（新マップローダー統合版）
"""

import pygame
import time
from typing import Optional, List, Dict, Any
from src.core.scene import Scene
from src.entities.player import Player
from src.entities.pet import Pet, PetData, PetType
from src.systems.puzzle_system import PuzzleSystem
from src.systems.map_system import MapSystem
from src.systems.audio_system import get_audio_system
from src.systems.timer_system import TimerSystem
from src.systems.map_data_loader import get_map_data_loader
from src.systems.pet_data_loader import get_pet_data_loader
from src.ui.game_ui import GameUI, NotificationType, QuickSlotItem
from src.utils.asset_manager import get_asset_manager
from src.utils.font_manager import get_font_manager

class GameScene(Scene):
    """ゲームシーン"""
    
    def __init__(self, screen: pygame.Surface, flow_manager=None):
        super().__init__(screen)
        self.flow_manager = flow_manager
        
        # 新しいデータローダーの初期化
        self.map_loader = get_map_data_loader()
        self.pet_data_loader = get_pet_data_loader()
        
        # Version 1.0マップを読み込み
        if not self.map_loader.load_map('residential_v1'):
            print("⚠️ 新マップ読み込み失敗、従来マップを使用")
        else:
            print("✅ Version 1.0マップ読み込み成功")
        
        # ゲーム要素の初期化
        self._initialize_game_elements()
        
        # ゲーム状態
        self.paused = False
        self.game_over = False
        self.victory = False
        self.pets_rescued = []
        
        # ゲーム制限
        self.time_limit = 300.0  # 5分制限
        self.remaining_time = self.time_limit
        self.player_lives = 3  # プレイヤーのライフ
        
        # 統計情報
        self.start_time = time.time()
        self.total_pets = len(self.pets)
    
    def _initialize_game_elements(self):
        """ゲーム要素を初期化"""
        # アセットマネージャーとフォントマネージャー
        self.asset_manager = get_asset_manager()
        self.font_manager = get_font_manager()
        
        # 背景画像の読み込み
        self.background_image = None
        self._load_background()
        
        # プレイヤー初期化
        self.player = Player(x=100, y=100)
        
        # マップシステム初期化
        self.map_system = MapSystem()
        
        # 新しいマップデータを使用してMapSystemを更新
        current_map = self.map_loader.get_current_map()
        if current_map:
            print(f"🗺️ MapSystemを新データで更新: {current_map.dimensions.width}x{current_map.dimensions.height}")
            # MapSystemに新しいサイズを設定
            self.map_system._update_from_new_map_data(current_map)
        else:
            # フォールバック: 従来のマップを読み込み
            if not self.map_system.load_map("residential.json"):
                print("⚠️ マップファイルが見つからないため、デフォルトマップを使用します")
        
        # ペット初期化
        self.pets = self._create_pets()
        
        # パズルシステム初期化
        self.puzzle_system = PuzzleSystem()
        self.current_puzzle = None
        
        # UI初期化
        self.game_ui = GameUI(self.screen)
        self.game_ui.set_map_system(self.map_system)
        
        # 音響システム初期化
        self.audio_system = get_audio_system()
        
        # タイマーシステム初期化（5分）
        self.timer_system = TimerSystem(300.0)
        self.timer_system.set_hint_callback(self._on_timer_hint)
        self.timer_system.set_time_warning_callback(self._on_time_warning)
        self.timer_system.set_time_up_callback(self._on_time_up)
        
        # GameUIにタイマーシステムを設定
        self.game_ui.set_timer_system(self.timer_system)
        
        # カメラオフセット
        self.camera_x = 0
        self.camera_y = 0
    
    def _load_background(self):
        """背景画像を読み込み"""
        try:
            self.background_image = self.asset_manager.get_image("backgrounds/game_background.png")
            if self.background_image:
                print(f"✅ ゲーム背景画像読み込み成功: {self.background_image.get_size()}")
                # 画面サイズに合わせてスケール
                screen_size = (self.screen.get_width(), self.screen.get_height())
                self.background_image = pygame.transform.scale(self.background_image, screen_size)
                print(f"✅ ゲーム背景画像スケール完了: {screen_size}")
            else:
                print("⚠️ ゲーム背景画像が見つかりません")
        except Exception as e:
            print(f"❌ ゲーム背景画像読み込みエラー: {e}")
            self.background_image = None
    
    def _create_pets(self) -> List[Pet]:
        """ペットを作成（フォールバック強制版）"""
        pets = []
        
        print("🐾 フォールバック強制でペット生成中...")
        
        # 犬
        dog_data = PetData(
            pet_id="dog_001",
            name="ポチ",
            pet_type=PetType.DOG,
            personality="friendly",
            rarity="common",
            description="忠実な柴犬"
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
        rabbit = Pet(rabbit_data, x=700, y=400)
        pets.append(rabbit)
        
        # 鳥
        bird_data = PetData(
            pet_id="bird_001",
            name="ピーちゃん",
            pet_type=PetType.BIRD,
            personality="active",
            rarity="rare",
            description="カラフルな小鳥"
        )
        bird = Pet(bird_data, x=400, y=150)
        pets.append(bird)
        
        print(f"✅ フォールバックペット生成完了: {len(pets)}匹")
        for pet in pets:
            print(f"  🐾 {pet.data.name} ({pet.data.pet_type.value}) at ({pet.x}, {pet.y})")
        
        return pets
    
    
    def enter(self) -> None:
        """シーンに入る時の処理"""
        self.start_time = time.time()
        self.pets_rescued = []
        self.game_over = False
        self.victory = False
        self.paused = False
        
        # タイマー開始
        self.timer_system.start()
        
        # BGM開始
        self.audio_system.play_bgm("residential_bgm")
        
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
                else:
                    # ゲームを一時停止してメニューに戻る
                    return "menu"
            
            elif event.key == pygame.K_p:
                # ポーズ切り替え
                self.paused = not self.paused
                if self.paused:
                    self.timer_system.pause()
                    self.game_ui.add_notification("ゲーム一時停止", NotificationType.INFO)
                else:
                    self.timer_system.start()
                    self.game_ui.add_notification("ゲーム再開", NotificationType.INFO)
            
            elif event.key == pygame.K_c:
                # デモではCキーでペット図鑑切り替えはなし
                pass
        
        elif event.type == pygame.USEREVENT + 1:
            # ゲーム完了タイマー（旧）
            if self.victory:
                return "result"
        
        elif event.type == pygame.USEREVENT + 2:
            # ゲーム勝利タイマー（新）
            if self.victory:
                print("🎉 勝利画面に移行")
                return "result"
        
        elif event.type == pygame.USEREVENT + 3:
            # ゲーム敗北タイマー
            if self.game_over:
                print("💀 敗北画面に移行")
                return "result"
        
        # パズル中の場合はパズルUIにイベントを渡す
        if self.current_puzzle:
            # パズル機能削除済み - 何もしない
            pass
        else:
            # 通常のゲームイベント処理
            self.player.handle_event(event)
            self.game_ui.handle_input(event)
        
        return None
    
    def update(self, time_delta: float) -> Optional[str]:
        """更新処理"""
        if self.paused or self.game_over:
            return None
        
        # タイマー更新
        self.timer_system.update()
        
        # 時間切れチェック
        if self.timer_system.is_finished():
            self.game_over = True
            return None
        
        # Phase 1: プレイヤー基本更新
        keys_pressed: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        self.player.update(time_delta, keys_pressed, self.map_system)
        
        # ペット更新（デモで動いていた処理を追加）
        player_pos = (self.player.x, self.player.y)
        for pet in self.pets:
            if pet.data.pet_id not in self.pets_rescued:
                pet.update(time_delta, player_pos, self.map_system)
        
        # カメラ更新
        self._update_camera()
        
        # ペットとの衝突判定
        self._check_pet_interactions()
        
        # パズル更新（削除済み）
        # if self.current_puzzle:
        #     self.puzzle_ui.update(time_delta, [])
        
        # UI更新
        self.game_ui.update(time_delta)
        self._update_ui_stats()
        
        # 時間更新
        if not self.paused and not self.victory and not self.game_over:
            self.remaining_time -= time_delta
        
        # 敗北条件チェック
        if not self.game_over and not self.victory:
            if self.remaining_time <= 0:
                self.game_over = True
                self.game_ui.add_notification("時間切れです！", NotificationType.ERROR)
                print("⏰ 時間切れで敗北")
                pygame.time.set_timer(pygame.USEREVENT + 3, 2000)  # 敗北画面へ
            elif self.player_lives <= 0:
                self.game_over = True
                self.game_ui.add_notification("ライフが尽きました！", NotificationType.ERROR)
                print("💔 ライフ切れで敗北")
                pygame.time.set_timer(pygame.USEREVENT + 3, 2000)  # 敗北画面へ
        
        # 勝利条件チェック（ペットが存在する場合のみ）
        if self.total_pets > 0 and len(self.pets_rescued) >= self.total_pets and not self.victory and not self.game_over:
            self.victory = True
            
            # タイマー停止
            self.timer_system.pause()
            
            # タイムボーナス計算
            time_bonus = self.timer_system.calculate_time_bonus()
            bonus_message = f"タイムボーナス: {time_bonus}点"
            
            self.game_ui.add_notification("全てのペットを救出しました！", NotificationType.SUCCESS)
            self.game_ui.add_notification(bonus_message, NotificationType.INFO)
            print("🎉 勝利条件達成！")
            
            # 勝利BGMに変更
            self.audio_system.play_bgm("victory_bgm")
            
            # GameMainに勝利を通知
            if self.flow_manager and hasattr(self.flow_manager, '_game_victory'):
                # 2秒後に結果画面に移行
                pygame.time.set_timer(pygame.USEREVENT + 2, 2000)
        
        return None
    
    def draw(self, surface: pygame.Surface) -> None:
        """描画処理（マップ優先版）"""
        # まず背景色でクリア
        surface.fill((50, 100, 50))  # 緑っぽい背景
        
        # マップ描画（最優先）
        self.map_system.draw(surface, self.camera_x, self.camera_y)
        
        # 背景画像は使用しない（マップが背景の役割）
        # if self.background_image:
        #     surface.blit(self.background_image, (0, 0))
        
        # ペット描画（救出済みは非表示）
        for pet in self.pets:
            if pet.data.pet_id not in self.pets_rescued and not getattr(pet, 'rescued', False):
                pet.draw(surface, (self.camera_x, self.camera_y))
        
        # プレイヤー描画
        camera_offset = (self.camera_x, self.camera_y)
        self.player.draw(surface, camera_offset)
        
        # パズルUI描画（削除済み）
        # if self.current_puzzle:
        #     self.puzzle_ui.draw()
        
        # ゲームUI描画
        player_stats = {
            'health': self.player.stats.health,
            'max_health': self.player.stats.max_health,
            'stamina': self.player.stats.stamina,
            'max_stamina': self.player.stats.max_stamina
        }
        self.game_ui.draw(player_stats, [], (self.player.x, self.player.y))
        
        # タイマー表示
        time_string = self.timer_system.get_time_string()
        is_warning = self.timer_system.is_warning_time()
        self.game_ui.draw_timer(time_string, is_warning)
        
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
        
        # カメラ範囲制限（実際のマップサイズに基づく）
        if self.map_system and self.map_system.map_surface:
            map_width, map_height = self.map_system.map_surface.get_size()
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            
            # カメラがマップの境界を超えないように制限
            max_camera_x = max(0, map_width - screen_width)
            max_camera_y = max(0, map_height - screen_height)
            
            self.camera_x = max(0, min(self.camera_x, max_camera_x))
            self.camera_y = max(0, min(self.camera_y, max_camera_y))
            
            # デバッグ情報（境界付近でのみ表示）
            if (self.camera_x <= 0 or self.camera_x >= max_camera_x or 
                self.camera_y <= 0 or self.camera_y >= max_camera_y):
                print(f"📷 カメラ境界制限: ({self.camera_x:.1f}, {self.camera_y:.1f}) - マップ: {map_width}x{map_height}")
        else:
            # フォールバック: 従来の制限
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
                # ペット発見通知（1回のみ）
                if not hasattr(pet, 'discovered'):
                    pet.discovered = True
                    self.audio_system.play_sfx("pet_found")
                    self.game_ui.add_notification(f"{pet.data.name}を見つけました！", NotificationType.INFO)
                    self.game_ui.add_notification("Eキーで救出できます", NotificationType.INFO)
                
                # Eキーで救出
                keys = pygame.key.get_pressed()
                if keys[pygame.K_e]:
                    self._rescue_pet(pet)
    
    def _rescue_pet(self, pet: Pet):
        """ペットを救出（パズルなし）"""
        if pet.data.pet_id not in self.pets_rescued:
            self.pets_rescued.append(pet.data.pet_id)
            self.game_ui.add_notification(f"{pet.data.name}を救出しました！", NotificationType.SUCCESS)
            self.audio_system.play_sfx("pet_rescued")
            
            # ペットを非表示にする
            pet.rescued = True
    
    def _calculate_final_score(self) -> int:
        """最終スコアを計算"""
        base_score = 0
        
        # ペット救出ボーナス
        pets_rescued_count = len(self.pets_rescued)
        base_score += pets_rescued_count * 1000
        
        # 完全クリアボーナス
        if pets_rescued_count >= self.total_pets:
            base_score += 2000
        
        # タイムボーナス（新システム）
        if self.victory:
            time_bonus = self.timer_system.calculate_time_bonus()
            base_score += time_bonus
        
        # ライフボーナス
        if self.victory:
            life_bonus = self.player_lives * 50
            base_score += life_bonus
        
        # 効率ボーナス（短時間でクリア）
        elapsed_time = time.time() - self.start_time
        if self.victory and elapsed_time < 180:  # 3分以内
            base_score += 200
        
        return max(0, base_score)
    
    def get_game_result(self) -> Dict[str, Any]:
        """ゲーム結果を取得"""
        elapsed_time = time.time() - self.start_time
        final_score = self._calculate_final_score()
        
        return {
            'victory': self.victory,
            'game_over': self.game_over,
            'pets_rescued': len(self.pets_rescued),
            'total_pets': self.total_pets,
            'time_taken': elapsed_time,
            'remaining_time': max(0, self.remaining_time),
            'player_lives': self.player_lives,
            'score': final_score,
            'completion_rate': (len(self.pets_rescued) / self.total_pets) * 100 if self.total_pets > 0 else 0
        }
    
    def _update_ui_stats(self):
        """UI統計情報を更新"""
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        # 残り時間の計算
        remaining_minutes = int(self.remaining_time // 60)
        remaining_seconds = int(self.remaining_time % 60)
        
        stats = {
            'pets_rescued': len(self.pets_rescued),
            'total_pets': self.total_pets,
            'time': f"{minutes:02d}:{seconds:02d}",
            'remaining_time': f"{remaining_minutes:02d}:{remaining_seconds:02d}",
            'lives': self.player_lives,
            'health': getattr(self.player, 'health', 100),
            'stamina': getattr(self.player, 'stamina', 100)
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
    
    def _on_timer_hint(self, hint_message: str, minute: int):
        """タイマーヒントコールバック"""
        self.game_ui.add_notification(f"ヒント: {hint_message}", NotificationType.INFO)
        
        # ヒント効果音再生
        if self.audio_system:
            self.audio_system.play_sfx("hint")
    
    def _on_time_warning(self):
        """時間警告コールバック"""
        # 警告は一度だけ表示
        if not hasattr(self, '_warning_shown'):
            self.game_ui.add_notification("残り時間が少なくなりました！", NotificationType.WARNING)
            self._warning_shown = True
            
            # 警告効果音再生
            if self.audio_system:
                self.audio_system.play_sfx("time_warning")
    
    def _on_time_up(self):
        """時間切れコールバック"""
        self.game_ui.add_notification("時間切れ！ゲームオーバー", NotificationType.ERROR)
        
        # ゲームオーバー効果音再生
        if self.audio_system:
            self.audio_system.play_sfx("game_over")
        
        # ゲームオーバー処理
        if self.flow_manager:
            self.flow_manager.game_over("time_up")
    
    def start_game(self):
        """ゲーム開始（タイマー開始）"""
        self.timer_system.start()
        self.game_ui.add_notification("ペットを探しましょう！", NotificationType.INFO)
