"""
ペット図鑑シーン
図鑑の表示とナビゲーションを管理
"""

import pygame
import pygame_gui
from typing import Optional

from src.core.scene import Scene
from src.ui.pet_collection_ui import PetCollectionUI

class PetCollectionScene(Scene):
    """ペット図鑑シーンクラス"""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        self.ui_manager = pygame_gui.UIManager((screen.get_width(), screen.get_height()))
        self.pet_collection_ui = PetCollectionUI(screen, self.ui_manager)
        
        # 背景色
        self.background_color = (240, 248, 255)  # アリスブルー
        
    def enter(self) -> None:
        """シーンに入る時の処理"""
        self.pet_collection_ui.show()
    
    def exit(self) -> None:
        """シーンから出る時の処理"""
        self.pet_collection_ui.hide()
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """イベント処理"""
        # UI要素のイベント処理
        if self.pet_collection_ui.handle_event(event):
            return None
        
        # UIマネージャーのイベント処理
        self.ui_manager.process_events(event)
        
        # ESCキーで前のシーンに戻る
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"  # メニューシーンに戻る
        
        return None
    
    def update(self, time_delta: float) -> Optional[str]:
        """更新処理"""
        self.ui_manager.update(time_delta)
        self.pet_collection_ui.update(time_delta)
        return None
    
    def draw(self, surface: pygame.Surface) -> None:
        """描画処理"""
        # 背景を塗りつぶし
        surface.fill(self.background_color)
        
        # UIを描画
        self.ui_manager.draw_ui(surface)
        self.pet_collection_ui.draw([])
