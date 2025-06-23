"""
ペット詳細UI
現在未使用のため、pygame_gui依存を削除して簡易実装に変更
"""

import pygame
from typing import Optional

from src.utils.font_manager import get_font_manager

class PetDetailUI:
    """ペット詳細UI（簡易実装版）"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.font_manager = get_font_manager()
        self.visible = False
        
        # フォント
        self.title_font = self.font_manager.get_font('japanese', 24)
        self.text_font = self.font_manager.get_font('japanese', 16)
        
        # 色設定
        self.colors = {
            'bg': (40, 40, 40, 200),
            'border': (100, 100, 100),
            'text': (255, 255, 255),
            'button': (70, 70, 70)
        }
        
        # パネル設定
        self.panel_width = 600
        self.panel_height = 400
        self.panel_x = (screen.get_width() - self.panel_width) // 2
        self.panel_y = (screen.get_height() - self.panel_height) // 2
        
        # 現在表示中のペット情報
        self.current_pet = None
    
    def show(self, pet_data=None):
        """詳細画面を表示"""
        self.visible = True
        self.current_pet = pet_data
    
    def hide(self):
        """詳細画面を非表示"""
        self.visible = False
        self.current_pet = None
    
    def is_visible(self) -> bool:
        """表示状態を確認"""
        return self.visible
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理"""
        if not self.visible:
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                # 閉じるボタンの領域
                close_button = pygame.Rect(
                    self.panel_x + self.panel_width - 40, 
                    self.panel_y + 10, 30, 30
                )
                if close_button.collidepoint(event.pos):
                    self.hide()
                    return True
                
                # パネル外クリックで閉じる
                panel_rect = pygame.Rect(self.panel_x, self.panel_y, 
                                       self.panel_width, self.panel_height)
                if not panel_rect.collidepoint(event.pos):
                    self.hide()
                    return True
        
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.hide()
                return True
        
        return True
    
    def update(self, time_delta: float):
        """更新処理"""
        if not self.visible:
            return
        # 必要に応じて更新処理を追加
        pass
    
    def draw(self, surface: pygame.Surface):
        """描画処理"""
        if not self.visible:
            return
        
        # 背景パネル
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.colors['bg'])
        pygame.draw.rect(panel_surface, self.colors['border'], 
                        (0, 0, self.panel_width, self.panel_height), 2)
        surface.blit(panel_surface, (self.panel_x, self.panel_y))
        
        # タイトル
        title_text = self.title_font.render("ペット詳細", True, self.colors['text'])
        surface.blit(title_text, (self.panel_x + 20, self.panel_y + 20))
        
        # 閉じるボタン
        close_button = pygame.Rect(self.panel_x + self.panel_width - 40, 
                                 self.panel_y + 10, 30, 30)
        pygame.draw.rect(surface, self.colors['button'], close_button)
        pygame.draw.rect(surface, self.colors['border'], close_button, 1)
        
        close_text = self.text_font.render("×", True, self.colors['text'])
        close_rect = close_text.get_rect(center=close_button.center)
        surface.blit(close_text, close_rect)
        
        # ペット情報表示
        if self.current_pet:
            self._draw_pet_info(surface)
        else:
            # デフォルト表示
            info_text = self.text_font.render("ペット情報がありません", True, self.colors['text'])
            surface.blit(info_text, (self.panel_x + 20, self.panel_y + 80))
    
    def _draw_pet_info(self, surface: pygame.Surface):
        """ペット情報を描画"""
        y_offset = 80
        line_height = 25
        
        # 簡易的な情報表示
        info_lines = [
            f"名前: {getattr(self.current_pet, 'name', '不明')}",
            f"種類: {getattr(self.current_pet, 'species', '不明')}",
            f"状態: {getattr(self.current_pet, 'status', '不明')}",
            "詳細情報は今後実装予定"
        ]
        
        for i, line in enumerate(info_lines):
            text = self.text_font.render(line, True, self.colors['text'])
            surface.blit(text, (self.panel_x + 20, self.panel_y + y_offset + i * line_height))
    
    def set_pet_data(self, pet_data):
        """ペットデータを設定"""
        self.current_pet = pet_data
        if self.visible:
            # 表示中なら再描画のため何もしない（次のdrawで反映される）
            pass
