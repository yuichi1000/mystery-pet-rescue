"""
インベントリシーン
インベントリUIの表示と管理を行う
"""

import pygame
import pygame_gui
from typing import Optional

from src.core.scene import Scene
from src.ui.inventory_ui import InventoryUI
from src.systems.item_system import Inventory, ItemSystem

class InventoryScene(Scene):
    """インベントリシーンクラス"""
    
    def __init__(self, screen: pygame.Surface, inventory: Inventory = None):
        super().__init__(screen)
        self.ui_manager = pygame_gui.UIManager((screen.get_width(), screen.get_height()))
        
        # インベントリシステム
        self.item_system = ItemSystem()
        self.inventory = inventory or Inventory(item_system=self.item_system)
        
        # インベントリUI
        self.inventory_ui = InventoryUI(screen, self.ui_manager, self.inventory)
        
        # 背景色
        self.background_color = (50, 50, 50)
        
        # テスト用アイテムを追加
        self._add_test_items()
    
    def _add_test_items(self) -> None:
        """テスト用アイテムを追加"""
        test_items = [
            ("dog_treat", 3),
            ("cat_toy", 2),
            ("house_key", 1),
            ("magnifying_glass", 1),
            ("rabbit_carrot", 5),
            ("bird_seed", 8),
            ("flashlight", 1),
            ("pet_collar", 2)
        ]
        
        for item_id, quantity in test_items:
            self.inventory.add_item(item_id, quantity)
    
    def enter(self) -> None:
        """シーンに入る時の処理"""
        self.inventory_ui.show()
    
    def exit(self) -> None:
        """シーンから出る時の処理"""
        self.inventory_ui.hide()
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """イベント処理"""
        # インベントリUIのイベント処理
        if self.inventory_ui.handle_event(event):
            return None
        
        # ESCキーで前のシーンに戻る
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "menu"  # メニューシーンに戻る
            elif event.key == pygame.K_i:
                # Iキーでインベントリ切り替え
                self.inventory_ui.toggle()
        
        return None
    
    def update(self, time_delta: float) -> Optional[str]:
        """更新処理"""
        self.inventory_ui.update(time_delta)
        return None
    
    def draw(self, surface: pygame.Surface) -> None:
        """描画処理"""
        # 背景を塗りつぶし
        surface.fill(self.background_color)
        
        # タイトル表示
        font = pygame.font.Font(None, 48)
        title_text = font.render("インベントリシステム", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(surface.get_width() // 2, 50))
        surface.blit(title_text, title_rect)
        
        # 操作説明
        font_small = pygame.font.Font(None, 24)
        instructions = [
            "左クリック: アイテム選択",
            "Ctrl+左クリック: 複数選択",
            "ドラッグ: アイテム移動",
            "使用ボタン: アイテム使用",
            "組み合わせボタン: アイテム組み合わせ",
            "ESC: メニューに戻る"
        ]
        
        y = 100
        for instruction in instructions:
            text = font_small.render(instruction, True, (200, 200, 200))
            surface.blit(text, (20, y))
            y += 25
        
        # インベントリUIを描画
        self.inventory_ui.draw(surface)
