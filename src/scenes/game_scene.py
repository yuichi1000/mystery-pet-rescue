"""
メインゲームシーン
ペット探索とゲームプレイを管理
"""

import pygame
import pygame_gui
from typing import Optional

from src.core.scene import Scene
from src.systems.pet_collection import PetCollection
from src.ui.pet_collection_ui import PetCollectionUI

class GameScene(Scene):
    """メインゲームシーンクラス"""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.ui_manager = pygame_gui.UIManager((screen.get_width(), screen.get_height()))
        self.pet_collection = PetCollection()
        self.pet_collection_ui = PetCollectionUI(screen, self.ui_manager)
        
        # ゲーム状態
        self.player_pos = [400, 300]
        self.background_color = (135, 206, 235)  # スカイブルー
        
        # UI要素
        self.collection_button = None
        self.info_label = None
        
        self._create_ui()
    
    def _create_ui(self) -> None:
        """UI要素を作成"""
        # 図鑑ボタン
        self.collection_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, 10, 100, 40),
            text='ペット図鑑',
            manager=self.ui_manager
        )
        
        # 情報表示
        stats = self.pet_collection.get_collection_stats()
        info_text = f"図鑑: {stats['rescued_pets']}/{stats['total_pets']}"
        
        self.info_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(120, 10, 200, 40),
            text=info_text,
            manager=self.ui_manager
        )
    
    def enter(self) -> None:
        """シーンに入る時の処理"""
        # 統計情報を更新
        stats = self.pet_collection.get_collection_stats()
        info_text = f"図鑑: {stats['rescued_pets']}/{stats['total_pets']}"
        if self.info_label:
            self.info_label.set_text(info_text)
    
    def exit(self) -> None:
        """シーンから出る時の処理"""
        self.pet_collection_ui.hide()
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """イベント処理"""
        # ペット図鑑UIのイベント処理
        if self.pet_collection_ui.handle_event(event):
            return None
        
        # UIマネージャーのイベント処理
        self.ui_manager.process_events(event)
        
        # ボタンイベント
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.collection_button:
                self.pet_collection_ui.show()
                return None
        
        # キーボードイベント
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:  # Cキーで図鑑を開く
                self.pet_collection_ui.show()
            elif event.key == pygame.K_ESCAPE:
                return "menu"  # メニューに戻る
            
            # プレイヤー移動（デモ用）
            elif event.key == pygame.K_w or event.key == pygame.K_UP:
                self.player_pos[1] -= 10
            elif event.key == pygame.K_s or event.key == pygame.K_DOWN:
                self.player_pos[1] += 10
            elif event.key == pygame.K_a or event.key == pygame.K_LEFT:
                self.player_pos[0] -= 10
            elif event.key == pygame.K_d or event.key == pygame.K_RIGHT:
                self.player_pos[0] += 10
            
            # テスト用：ペット救助シミュレーション
            elif event.key == pygame.K_r:
                self._simulate_pet_rescue()
        
        return None
    
    def _simulate_pet_rescue(self) -> None:
        """ペット救助をシミュレート（テスト用）"""
        # 未救助のペットを1匹救助
        unrescued_pets = self.pet_collection.get_unrescued_pets()
        if unrescued_pets:
            pet = unrescued_pets[0]
            success = self.pet_collection.rescue_pet(
                pet.id, 
                "住宅街の公園", 
                30  # 30秒で救助
            )
            if success:
                # 統計情報を更新
                stats = self.pet_collection.get_collection_stats()
                info_text = f"図鑑: {stats['rescued_pets']}/{stats['total_pets']}"
                if self.info_label:
                    self.info_label.set_text(info_text)
                print(f"{pet.name}を救助しました！")
    
    def update(self, time_delta: float) -> Optional[str]:
        """更新処理"""
        self.ui_manager.update(time_delta)
        self.pet_collection_ui.update(time_delta)
        
        # 画面境界チェック
        screen_width, screen_height = self.screen.get_size()
        self.player_pos[0] = max(20, min(screen_width - 20, self.player_pos[0]))
        self.player_pos[1] = max(60, min(screen_height - 20, self.player_pos[1]))
        
        return None
    
    def draw(self, surface: pygame.Surface) -> None:
        """描画処理"""
        # 背景を塗りつぶし
        surface.fill(self.background_color)
        
        # プレイヤーを描画（簡単な円）
        pygame.draw.circle(surface, (255, 100, 100), self.player_pos, 15)
        
        # 操作説明を描画
        font = pygame.font.Font(None, 24)
        instructions = [
            "WASD/矢印キー: 移動",
            "C: ペット図鑑を開く",
            "R: ペット救助（テスト用）",
            "ESC: メニューに戻る"
        ]
        
        for i, instruction in enumerate(instructions):
            text = font.render(instruction, True, (255, 255, 255))
            surface.blit(text, (10, surface.get_height() - 100 + i * 25))
        
        # UIを描画
        self.ui_manager.draw_ui(surface)
        self.pet_collection_ui.draw(surface)
