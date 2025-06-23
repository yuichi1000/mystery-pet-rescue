"""
ペット図鑑UI - デモと全く同じ表示
"""

import pygame
from typing import List, Optional
from src.utils.font_manager import get_font_manager

class PetCollectionUI:
    """デモと全く同じペット図鑑UI"""
    
    def __init__(self, screen: pygame.Surface, ui_manager=None):
        self.screen = screen
        self.font_manager = get_font_manager()
        # デモと同じフォントサイズ
        self.small_font = self.font_manager.get_font("default", 24)
        self.visible = False
        
    def draw(self, collected_pets: List):
        """デモと全く同じ表示 - 画面左上に常時表示"""
        # デモでは専用画面ではなく、ゲーム画面の左上に常時表示
        found_count = len(collected_pets)
        total_count = 4  # デモでは4匹固定
        
        # デモと同じ位置・色・フォント
        status_text = self.small_font.render(f"Pets Found: {found_count}/{total_count}", True, (255, 255, 0))
        self.screen.blit(status_text, (20, 70))  # デモと同じ位置
        
    def show(self):
        """図鑑を表示（デモでは常時表示なので何もしない）"""
        self.visible = True
        
    def hide(self):
        """図鑑を非表示"""
        self.visible = False
        
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理"""
        if not self.visible:
            return False
        # 今後実装
        return False
        
    def update(self, time_delta: float):
        """更新処理"""
        if not self.visible:
            return
        # 今後実装
        pass
        self.visible = True
        
    def hide(self):
        """図鑑を非表示（デモでは常時表示なので何もしない）"""
        self.visible = False
        
    def toggle(self):
        """表示切り替え（デモでは常時表示なので何もしない）"""
        self.visible = not self.visible
        
    def update(self, dt: float):
        """更新処理（デモでは不要）"""
        pass
        
    def handle_event(self, event: pygame.event.Event):
        """イベント処理（デモでは不要）"""
        pass
