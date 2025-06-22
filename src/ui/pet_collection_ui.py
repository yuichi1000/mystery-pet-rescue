"""
ペット図鑑UI - デモと同じシンプル表示
"""

import pygame
from typing import List, Optional
from src.utils.font_manager import get_font_manager

class PetCollectionUI:
    """デモと同じシンプルなペット図鑑UI"""
    
    def __init__(self, screen: pygame.Surface, ui_manager=None):
        self.screen = screen
        self.font_manager = get_font_manager()
        self.font = self.font_manager.get_font("default", 24)
        self.visible = False
        
    def draw(self, collected_pets: List):
        """デモと同じシンプルな表示"""
        if not self.visible:
            return
            
        # 背景オーバーレイ
        overlay = pygame.Surface((self.screen.get_width(), self.screen.get_height()))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # デモと同じ表示: "Pets Found: X/Y"
        found_count = len(collected_pets)
        total_count = 4  # デモでは4匹固定
        
        status_text = self.font.render(f"Pets Found: {found_count}/{total_count}", True, (255, 255, 0))
        text_rect = status_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2))
        self.screen.blit(status_text, text_rect)
        
        # 操作説明
        help_text = self.font.render("Press C to close", True, (255, 255, 255))
        help_rect = help_text.get_rect(center=(self.screen.get_width() // 2, self.screen.get_height() // 2 + 50))
        self.screen.blit(help_text, help_rect)
    
    def show(self):
        """図鑑を表示"""
        self.visible = True
        
    def hide(self):
        """図鑑を非表示"""
        self.visible = False
        
    def toggle(self):
        """表示切り替え"""
        self.visible = not self.visible
        
    def update(self, dt: float):
        """更新処理（デモでは不要）"""
        pass
        
    def handle_event(self, event: pygame.event.Event):
        """イベント処理（デモでは不要）"""
        pass
