"""
インベントリUI
純粋なPygameで実装
"""

import pygame
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

from src.systems.inventory import Inventory, Item
from src.utils.font_manager import get_font_manager

class InventoryUIState(Enum):
    """インベントリUI状態"""
    HIDDEN = "hidden"
    VISIBLE = "visible"
    ITEM_SELECTED = "item_selected"

class InventoryUI:
    """インベントリUIクラス（純粋なPygame実装）"""
    
    def __init__(self, screen: pygame.Surface, inventory: Inventory = None):
        self.screen = screen
        self.inventory = inventory or Inventory()
        self.font_manager = get_font_manager()
        
        # UI状態
        self.state = InventoryUIState.HIDDEN
        self.selected_item_index = -1
        
        # UI設定
        self.panel_width = 400
        self.panel_height = 500
        self.panel_x = (screen.get_width() - self.panel_width) // 2
        self.panel_y = (screen.get_height() - self.panel_height) // 2
        
        # アイテムグリッド設定
        self.grid_cols = 4
        self.grid_rows = 6
        self.item_size = 64
        self.item_margin = 8
        self.grid_start_x = 20
        self.grid_start_y = 60
        
        # 色設定
        self.colors = {
            'panel_bg': (40, 40, 40, 200),
            'panel_border': (100, 100, 100),
            'button_normal': (70, 70, 70),
            'button_hover': (90, 90, 90),
            'button_pressed': (50, 50, 50),
            'text': (255, 255, 255),
            'item_selected': (255, 255, 0),
            'item_border': (150, 150, 150)
        }
        
        # ボタン領域
        self.buttons = {
            'close': pygame.Rect(self.panel_x + self.panel_width - 40, self.panel_y + 10, 30, 30),
            'use': pygame.Rect(self.panel_x + 10, self.panel_y + self.panel_height - 70, 80, 30),
            'combine': pygame.Rect(self.panel_x + 100, self.panel_y + self.panel_height - 70, 80, 30)
        }
        
        # フォント
        self.title_font = self.font_manager.get_font('japanese', 24)
        self.button_font = self.font_manager.get_font('japanese', 16)
        self.info_font = self.font_manager.get_font('japanese', 14)
        
        # 情報テキスト
        self.info_text = "アイテムを選択してください"
    
    def show(self):
        """インベントリを表示"""
        self.state = InventoryUIState.VISIBLE
        self.selected_item_index = -1
        self.info_text = "アイテムを選択してください"
    
    def hide(self):
        """インベントリを非表示"""
        self.state = InventoryUIState.HIDDEN
        self.selected_item_index = -1
    
    def is_visible(self) -> bool:
        """表示状態を確認"""
        return self.state != InventoryUIState.HIDDEN
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理"""
        if not self.is_visible():
            return False
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                return self._handle_click(event.pos)
        
        return True
    
    def _handle_click(self, pos: Tuple[int, int]) -> bool:
        """クリック処理"""
        # ボタンクリック確認
        for button_name, button_rect in self.buttons.items():
            if button_rect.collidepoint(pos):
                self._handle_button_click(button_name)
                return True
        
        # アイテムクリック確認
        item_index = self._get_item_at_pos(pos)
        if item_index >= 0:
            self._select_item(item_index)
            return True
        
        # パネル外クリックで閉じる
        panel_rect = pygame.Rect(self.panel_x, self.panel_y, self.panel_width, self.panel_height)
        if not panel_rect.collidepoint(pos):
            self.hide()
            return True
        
        return True
    
    def _handle_button_click(self, button_name: str):
        """ボタンクリック処理"""
        if button_name == 'close':
            self.hide()
        elif button_name == 'use' and self.selected_item_index >= 0:
            self._use_selected_item()
        elif button_name == 'combine' and self.selected_item_index >= 0:
            self._combine_selected_item()
    
    def _get_item_at_pos(self, pos: Tuple[int, int]) -> int:
        """指定位置のアイテムインデックスを取得"""
        rel_x = pos[0] - (self.panel_x + self.grid_start_x)
        rel_y = pos[1] - (self.panel_y + self.grid_start_y)
        
        if rel_x < 0 or rel_y < 0:
            return -1
        
        col = rel_x // (self.item_size + self.item_margin)
        row = rel_y // (self.item_size + self.item_margin)
        
        if col >= self.grid_cols or row >= self.grid_rows:
            return -1
        
        index = row * self.grid_cols + col
        if index < len(self.inventory.items):
            return index
        
        return -1
    
    def _select_item(self, index: int):
        """アイテム選択"""
        if 0 <= index < len(self.inventory.items):
            self.selected_item_index = index
            self.state = InventoryUIState.ITEM_SELECTED
            item = self.inventory.items[index]
            self.info_text = f"{item.name}: {item.description}"
    
    def _use_selected_item(self):
        """選択アイテムを使用"""
        if 0 <= self.selected_item_index < len(self.inventory.items):
            item = self.inventory.items[self.selected_item_index]
            # アイテム使用ロジック（今後実装）
            self.info_text = f"{item.name}を使用しました"
    
    def _combine_selected_item(self):
        """選択アイテムを組み合わせ"""
        if 0 <= self.selected_item_index < len(self.inventory.items):
            item = self.inventory.items[self.selected_item_index]
            # アイテム組み合わせロジック（今後実装）
            self.info_text = f"{item.name}を組み合わせモードにしました"
    
    def update(self, time_delta: float):
        """更新処理"""
        if not self.is_visible():
            return
        
        # 必要に応じて更新処理を追加
        pass
    
    def draw(self, surface: pygame.Surface):
        """描画処理"""
        if not self.is_visible():
            return
        
        # パネル背景
        panel_surface = pygame.Surface((self.panel_width, self.panel_height), pygame.SRCALPHA)
        panel_surface.fill(self.colors['panel_bg'])
        pygame.draw.rect(panel_surface, self.colors['panel_border'], 
                        (0, 0, self.panel_width, self.panel_height), 2)
        surface.blit(panel_surface, (self.panel_x, self.panel_y))
        
        # タイトル
        title_text = self.title_font.render("インベントリ", True, self.colors['text'])
        surface.blit(title_text, (self.panel_x + 10, self.panel_y + 15))
        
        # アイテムグリッド
        self._draw_items(surface)
        
        # ボタン
        self._draw_buttons(surface)
        
        # 情報テキスト
        info_text = self.info_font.render(self.info_text, True, self.colors['text'])
        surface.blit(info_text, (self.panel_x + 10, self.panel_y + self.panel_height - 35))
    
    def _draw_items(self, surface: pygame.Surface):
        """アイテム描画"""
        for i, item in enumerate(self.inventory.items):
            row = i // self.grid_cols
            col = i % self.grid_cols
            
            x = self.panel_x + self.grid_start_x + col * (self.item_size + self.item_margin)
            y = self.panel_y + self.grid_start_y + row * (self.item_size + self.item_margin)
            
            # アイテム枠
            item_rect = pygame.Rect(x, y, self.item_size, self.item_size)
            border_color = self.colors['item_selected'] if i == self.selected_item_index else self.colors['item_border']
            pygame.draw.rect(surface, (60, 60, 60), item_rect)
            pygame.draw.rect(surface, border_color, item_rect, 2)
            
            # アイテム名（簡易表示）
            item_text = self.button_font.render(item.name[:8], True, self.colors['text'])
            text_rect = item_text.get_rect(center=(x + self.item_size//2, y + self.item_size//2))
            surface.blit(item_text, text_rect)
    
    def _draw_buttons(self, surface: pygame.Surface):
        """ボタン描画"""
        button_texts = {
            'close': '×',
            'use': '使用',
            'combine': '組み合わせ'
        }
        
        for button_name, button_rect in self.buttons.items():
            # ボタン背景
            pygame.draw.rect(surface, self.colors['button_normal'], button_rect)
            pygame.draw.rect(surface, self.colors['panel_border'], button_rect, 1)
            
            # ボタンテキスト
            text = self.button_font.render(button_texts[button_name], True, self.colors['text'])
            text_rect = text.get_rect(center=button_rect.center)
            surface.blit(text, text_rect)
    
    def add_item(self, item: Item) -> bool:
        """アイテム追加"""
        return self.inventory.add_item(item)
    
    def remove_item(self, item_id: str) -> bool:
        """アイテム削除"""
        return self.inventory.remove_item(item_id)
    
    def get_selected_item(self) -> Optional[Item]:
        """選択中のアイテムを取得"""
        if 0 <= self.selected_item_index < len(self.inventory.items):
            return self.inventory.items[self.selected_item_index]
        return None
