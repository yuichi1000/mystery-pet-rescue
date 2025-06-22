"""
アイテムツールチップ
アイテム情報を表示するツールチップUI
"""

import pygame
from typing import Optional, Tuple
from src.systems.item_system import Item

class ItemTooltip:
    """アイテムツールチップクラス"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.is_visible = False
        self.item: Optional[Item] = None
        self.quantity = 0
        self.position = (0, 0)
        
        # 設定
        self.max_width = 300
        self.padding = 10
        self.line_height = 20
        
        # 色定義
        self.colors = {
            'background': (40, 40, 40, 240),
            'border': (200, 200, 200),
            'title': (255, 255, 255),
            'description': (200, 200, 200),
            'rarity_common': (255, 255, 255),
            'rarity_uncommon': (30, 255, 0),
            'rarity_rare': (0, 112, 255),
            'rarity_legendary': (163, 53, 238)
        }
        
        # フォント
        self.font_title = pygame.font.Font(None, 24)
        self.font_text = pygame.font.Font(None, 18)
    
    def show(self, item: Item, quantity: int, position: Tuple[int, int]) -> None:
        """ツールチップを表示"""
        self.item = item
        self.quantity = quantity
        self.position = position
        self.is_visible = True
    
    def hide(self) -> None:
        """ツールチップを非表示"""
        self.is_visible = False
        self.item = None
    
    def update(self, time_delta: float) -> None:
        """更新処理"""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """描画処理"""
        if not self.is_visible or not self.item:
            return
        
        # ツールチップ内容を準備
        lines = self._prepare_content()
        if not lines:
            return
        
        # サイズを計算
        tooltip_width, tooltip_height = self._calculate_size(lines)
        
        # 位置を調整（画面外に出ないように）
        x, y = self._adjust_position(tooltip_width, tooltip_height)
        
        # 背景を描画
        tooltip_rect = pygame.Rect(x, y, tooltip_width, tooltip_height)
        self._draw_background(surface, tooltip_rect)
        
        # テキストを描画
        self._draw_text(surface, lines, x + self.padding, y + self.padding)
    
    def _prepare_content(self) -> list:
        """ツールチップの内容を準備"""
        if not self.item:
            return []
        
        lines = []
        
        # タイトル（アイテム名 + 数量）
        title = self.item.name
        if self.quantity > 1:
            title += f" x{self.quantity}"
        lines.append(('title', title))
        
        # レア度
        rarity_text = self._get_rarity_text(self.item.rarity)
        lines.append(('rarity', rarity_text))
        
        # 説明
        if self.item.description:
            desc_lines = self._wrap_text(self.item.description, self.max_width - 2 * self.padding)
            for desc_line in desc_lines:
                lines.append(('description', desc_line))
        
        # 使用説明
        if self.item.use_description:
            lines.append(('description', ''))  # 空行
            lines.append(('description', f"使用: {self.item.use_description}"))
        
        return lines
    
    def _get_rarity_text(self, rarity: str) -> str:
        """レア度テキストを取得"""
        rarity_map = {
            'common': 'コモン',
            'uncommon': 'アンコモン',
            'rare': 'レア',
            'legendary': 'レジェンダリー'
        }
        return rarity_map.get(rarity, rarity)
    
    def _wrap_text(self, text: str, max_width: int) -> list:
        """テキストを折り返し"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if self.font_text.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _calculate_size(self, lines: list) -> Tuple[int, int]:
        """ツールチップサイズを計算"""
        max_width = 0
        total_height = 0
        
        for line_type, text in lines:
            if line_type == 'title':
                font = self.font_title
            else:
                font = self.font_text
            
            if text:  # 空行でない場合
                text_width = font.size(text)[0]
                max_width = max(max_width, text_width)
            
            total_height += self.line_height
        
        return (max_width + 2 * self.padding, total_height + 2 * self.padding)
    
    def _adjust_position(self, width: int, height: int) -> Tuple[int, int]:
        """位置を調整"""
        x, y = self.position
        
        # 右端チェック
        if x + width > self.screen.get_width():
            x = self.screen.get_width() - width
        
        # 下端チェック
        if y + height > self.screen.get_height():
            y = self.screen.get_height() - height
        
        # 左端・上端チェック
        x = max(0, x)
        y = max(0, y)
        
        return (x, y)
    
    def _draw_background(self, surface: pygame.Surface, rect: pygame.Rect) -> None:
        """背景を描画"""
        # 半透明背景
        bg_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        bg_surface.fill(self.colors['background'])
        surface.blit(bg_surface, rect)
        
        # 枠線
        pygame.draw.rect(surface, self.colors['border'], rect, 2)
    
    def _draw_text(self, surface: pygame.Surface, lines: list, start_x: int, start_y: int) -> None:
        """テキストを描画"""
        y = start_y
        
        for line_type, text in lines:
            if not text:  # 空行
                y += self.line_height
                continue
            
            # フォントと色を選択
            if line_type == 'title':
                font = self.font_title
                color = self.colors['title']
            elif line_type == 'rarity':
                font = self.font_text
                color = self._get_rarity_color(self.item.rarity)
            else:
                font = self.font_text
                color = self.colors['description']
            
            # テキストを描画
            text_surface = font.render(text, True, color)
            surface.blit(text_surface, (start_x, y))
            y += self.line_height
    
    def _get_rarity_color(self, rarity: str) -> Tuple[int, int, int]:
        """レア度色を取得"""
        color_map = {
            'common': self.colors['rarity_common'],
            'uncommon': self.colors['rarity_uncommon'],
            'rare': self.colors['rarity_rare'],
            'legendary': self.colors['rarity_legendary']
        }
        return color_map.get(rarity, self.colors['rarity_common'])
