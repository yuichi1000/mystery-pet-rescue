"""
インベントリUI
グリッド表示、ドラッグ&ドロップ、アイテム使用・組み合わせ機能を提供
"""

import pygame
import pygame_gui
from typing import List, Optional, Dict, Any, Tuple
from enum import Enum

from src.systems.item_system import Inventory, Item, ItemSystem
from src.ui.item_tooltip import ItemTooltip

class DragState(Enum):
    """ドラッグ状態"""
    NONE = "none"
    DRAGGING = "dragging"
    HOVERING = "hovering"

class InventoryUI:
    """インベントリUIクラス"""
    
    def __init__(self, screen: pygame.Surface, ui_manager: pygame_gui.UIManager, 
                 inventory: Inventory = None):
        self.screen = screen
        self.ui_manager = ui_manager
        self.inventory = inventory or Inventory()
        self.item_system = self.inventory.item_system
        
        # UI設定
        self.slot_size = 48
        self.slot_margin = 4
        self.grid_cols = 5
        self.grid_rows = 4
        self.panel_width = self.grid_cols * (self.slot_size + self.slot_margin) + self.slot_margin
        self.panel_height = self.grid_rows * (self.slot_size + self.slot_margin) + 100
        
        # 位置設定
        self.panel_x = (screen.get_width() - self.panel_width) // 2
        self.panel_y = (screen.get_height() - self.panel_height) // 2
        
        # UI要素
        self.container = None
        self.title_label = None
        self.close_button = None
        self.use_button = None
        self.combine_button = None
        self.info_label = None
        
        # 状態管理
        self.is_visible = False
        self.selected_slots: List[int] = []
        self.drag_state = DragState.NONE
        self.dragging_slot = -1
        self.drag_offset = (0, 0)
        self.hover_slot = -1
        
        # スロット矩形
        self.slot_rects: List[pygame.Rect] = []
        
        # ツールチップ
        self.tooltip = ItemTooltip(screen)
        
        # 色定義
        self.colors = {
            'background': (40, 40, 40, 200),
            'slot_empty': (60, 60, 60),
            'slot_filled': (80, 80, 80),
            'slot_selected': (100, 150, 200),
            'slot_hover': (120, 120, 120),
            'slot_border': (200, 200, 200),
            'text': (255, 255, 255),
            'rarity_common': (255, 255, 255),
            'rarity_uncommon': (30, 255, 0),
            'rarity_rare': (0, 112, 255),
            'rarity_legendary': (163, 53, 238)
        }
        
        self._create_ui()
        self._calculate_slot_positions()
    
    def _create_ui(self) -> None:
        """UI要素を作成"""
        # メインコンテナ
        self.container = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(self.panel_x, self.panel_y, 
                                    self.panel_width, self.panel_height),
            starting_layer_height=10,
            manager=self.ui_manager
        )
        
        # タイトル
        self.title_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, 10, self.panel_width - 20, 30),
            text='インベントリ',
            manager=self.ui_manager,
            container=self.container
        )
        
        # 閉じるボタン
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(self.panel_width - 40, 10, 30, 30),
            text='×',
            manager=self.ui_manager,
            container=self.container
        )
        
        # 使用ボタン
        self.use_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(10, self.panel_height - 70, 80, 30),
            text='使用',
            manager=self.ui_manager,
            container=self.container
        )
        
        # 組み合わせボタン
        self.combine_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(100, self.panel_height - 70, 80, 30),
            text='組み合わせ',
            manager=self.ui_manager,
            container=self.container
        )
        
        # 情報ラベル
        self.info_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, self.panel_height - 35, 
                                    self.panel_width - 20, 25),
            text='アイテムを選択してください',
            manager=self.ui_manager,
            container=self.container
        )
        
        # 初期状態では非表示
        self.hide()
    
    def _calculate_slot_positions(self) -> None:
        """スロット位置を計算"""
        self.slot_rects = []
        start_x = self.panel_x + self.slot_margin
        start_y = self.panel_y + 50  # タイトル分のオフセット
        
        for i in range(self.inventory.size):
            row = i // self.grid_cols
            col = i % self.grid_cols
            
            x = start_x + col * (self.slot_size + self.slot_margin)
            y = start_y + row * (self.slot_size + self.slot_margin)
            
            self.slot_rects.append(pygame.Rect(x, y, self.slot_size, self.slot_size))
    
    def show(self) -> None:
        """インベントリを表示"""
        self.is_visible = True
        if self.container:
            self.container.show()
    
    def hide(self) -> None:
        """インベントリを非表示"""
        self.is_visible = False
        if self.container:
            self.container.hide()
        self.selected_slots.clear()
        self.drag_state = DragState.NONE
    
    def toggle(self) -> None:
        """表示/非表示を切り替え"""
        if self.is_visible:
            self.hide()
        else:
            self.show()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理"""
        if not self.is_visible:
            return False
        
        # UIマネージャーのイベント処理
        self.ui_manager.process_events(event)
        
        # ボタンクリック処理
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.close_button:
                self.hide()
                return True
            elif event.ui_element == self.use_button:
                self._use_selected_item()
                return True
            elif event.ui_element == self.combine_button:
                self._combine_selected_items()
                return True
        
        # マウスイベント処理
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                return self._handle_mouse_down(event.pos)
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:  # 左クリック
                return self._handle_mouse_up(event.pos)
        elif event.type == pygame.MOUSEMOTION:
            return self._handle_mouse_motion(event.pos)
        
        return False
    
    def _handle_mouse_down(self, pos: Tuple[int, int]) -> bool:
        """マウスダウン処理"""
        slot_index = self._get_slot_at_pos(pos)
        
        if slot_index >= 0:
            slot = self.inventory.get_slot(slot_index)
            
            if slot and not slot.is_empty():
                # ドラッグ開始
                self.drag_state = DragState.DRAGGING
                self.dragging_slot = slot_index
                slot_rect = self.slot_rects[slot_index]
                self.drag_offset = (pos[0] - slot_rect.x, pos[1] - slot_rect.y)
                
                # 選択状態を更新
                if pygame.key.get_pressed()[pygame.K_LCTRL]:
                    # Ctrlキー押下時は複数選択
                    if slot_index in self.selected_slots:
                        self.selected_slots.remove(slot_index)
                    else:
                        self.selected_slots.append(slot_index)
                else:
                    # 通常選択
                    self.selected_slots = [slot_index]
                
                self._update_info_display()
                return True
            else:
                # 空スロットクリック時は選択解除
                self.selected_slots.clear()
                self._update_info_display()
        
        return False
    
    def _handle_mouse_up(self, pos: Tuple[int, int]) -> bool:
        """マウスアップ処理"""
        if self.drag_state == DragState.DRAGGING:
            target_slot = self._get_slot_at_pos(pos)
            
            if target_slot >= 0 and target_slot != self.dragging_slot:
                # アイテム移動
                if self.inventory.move_item(self.dragging_slot, target_slot):
                    self.selected_slots = [target_slot]
                    self._update_info_display()
            
            self.drag_state = DragState.NONE
            self.dragging_slot = -1
            return True
        
        return False
    
    def _handle_mouse_motion(self, pos: Tuple[int, int]) -> bool:
        """マウス移動処理"""
        if self.drag_state == DragState.DRAGGING:
            return True
        
        # ホバー処理
        old_hover = self.hover_slot
        self.hover_slot = self._get_slot_at_pos(pos)
        
        if old_hover != self.hover_slot:
            if self.hover_slot >= 0:
                slot = self.inventory.get_slot(self.hover_slot)
                if slot and not slot.is_empty():
                    item = self.item_system.get_item(slot.item_id)
                    if item:
                        self.tooltip.show(item, slot.quantity, pos)
                else:
                    self.tooltip.hide()
            else:
                self.tooltip.hide()
        
        return False
    
    def _get_slot_at_pos(self, pos: Tuple[int, int]) -> int:
        """指定位置のスロットインデックスを取得"""
        for i, rect in enumerate(self.slot_rects):
            if rect.collidepoint(pos):
                return i
        return -1
    
    def _use_selected_item(self) -> None:
        """選択されたアイテムを使用"""
        if len(self.selected_slots) == 1:
            slot_index = self.selected_slots[0]
            if self.inventory.use_item(slot_index):
                self._update_info_display()
                print("アイテムを使用しました。")
            else:
                print("アイテムを使用できませんでした。")
    
    def _combine_selected_items(self) -> None:
        """選択されたアイテムを組み合わせ"""
        if len(self.selected_slots) < 2:
            print("組み合わせには2つ以上のアイテムが必要です。")
            return
        
        # 選択されたアイテムのIDを取得
        item_ids = []
        for slot_index in self.selected_slots:
            slot = self.inventory.get_slot(slot_index)
            if slot and not slot.is_empty():
                item_ids.append(slot.item_id)
        
        # 組み合わせ可能かチェック
        result_item_id = self.item_system.combine_items(item_ids)
        if result_item_id:
            # 材料アイテムを削除
            for slot_index in self.selected_slots:
                slot = self.inventory.get_slot(slot_index)
                if slot and not slot.is_empty():
                    self.inventory.remove_item(slot.item_id, 1)
            
            # 結果アイテムを追加
            remaining = self.inventory.add_item(result_item_id, 1)
            if remaining > 0:
                print("インベントリが満杯で結果アイテムを追加できませんでした。")
            else:
                result_item = self.item_system.get_item(result_item_id)
                print(f"{result_item.name}を作成しました！")
            
            self.selected_slots.clear()
            self._update_info_display()
        else:
            print("これらのアイテムは組み合わせできません。")
    
    def _update_info_display(self) -> None:
        """情報表示を更新"""
        if not self.selected_slots:
            self.info_label.set_text("アイテムを選択してください")
            return
        
        if len(self.selected_slots) == 1:
            slot_index = self.selected_slots[0]
            slot = self.inventory.get_slot(slot_index)
            if slot and not slot.is_empty():
                item = self.item_system.get_item(slot.item_id)
                if item:
                    text = f"{item.name} x{slot.quantity}"
                    self.info_label.set_text(text)
                    return
        else:
            # 複数選択時
            item_names = []
            for slot_index in self.selected_slots:
                slot = self.inventory.get_slot(slot_index)
                if slot and not slot.is_empty():
                    item = self.item_system.get_item(slot.item_id)
                    if item:
                        item_names.append(item.name)
            
            if item_names:
                text = f"選択中: {', '.join(item_names)}"
                self.info_label.set_text(text)
                return
        
        self.info_label.set_text("アイテムを選択してください")
    
    def _get_rarity_color(self, rarity: str) -> Tuple[int, int, int]:
        """レア度に応じた色を取得"""
        color_map = {
            'common': self.colors['rarity_common'],
            'uncommon': self.colors['rarity_uncommon'],
            'rare': self.colors['rarity_rare'],
            'legendary': self.colors['rarity_legendary']
        }
        return color_map.get(rarity, self.colors['rarity_common'])
    
    def update(self, time_delta: float) -> None:
        """更新処理"""
        if self.is_visible:
            self.ui_manager.update(time_delta)
            self.tooltip.update(time_delta)
    
    def draw(self, surface: pygame.Surface) -> None:
        """描画処理"""
        if not self.is_visible:
            return
        
        # UIマネージャーの描画
        self.ui_manager.draw_ui(surface)
        
        # スロットの描画
        self._draw_slots(surface)
        
        # ドラッグ中のアイテム描画
        if self.drag_state == DragState.DRAGGING:
            self._draw_dragging_item(surface)
        
        # ツールチップの描画
        self.tooltip.draw(surface)
    
    def _draw_slots(self, surface: pygame.Surface) -> None:
        """スロットを描画"""
        for i, rect in enumerate(self.slot_rects):
            slot = self.inventory.get_slot(i)
            
            # スロット背景色を決定
            if i == self.hover_slot and self.drag_state != DragState.DRAGGING:
                color = self.colors['slot_hover']
            elif i in self.selected_slots:
                color = self.colors['slot_selected']
            elif slot and not slot.is_empty():
                color = self.colors['slot_filled']
            else:
                color = self.colors['slot_empty']
            
            # スロット背景を描画
            pygame.draw.rect(surface, color, rect)
            pygame.draw.rect(surface, self.colors['slot_border'], rect, 2)
            
            # アイテムを描画
            if slot and not slot.is_empty() and i != self.dragging_slot:
                self._draw_item_in_slot(surface, slot, rect)
    
    def _draw_item_in_slot(self, surface: pygame.Surface, slot, rect: pygame.Rect) -> None:
        """スロット内のアイテムを描画"""
        item = self.item_system.get_item(slot.item_id)
        if not item:
            return
        
        # アイテムアイコンの描画（仮の実装）
        icon_rect = pygame.Rect(rect.x + 4, rect.y + 4, rect.width - 8, rect.height - 8)
        
        # レア度に応じた枠色
        rarity_color = self._get_rarity_color(item.rarity)
        pygame.draw.rect(surface, rarity_color, icon_rect, 2)
        
        # アイテム名の最初の文字を表示（アイコンの代替）
        font = pygame.font.Font(None, 24)
        text = font.render(item.name[0], True, self.colors['text'])
        text_rect = text.get_rect(center=icon_rect.center)
        surface.blit(text, text_rect)
        
        # 数量表示
        if slot.quantity > 1:
            font_small = pygame.font.Font(None, 16)
            qty_text = font_small.render(str(slot.quantity), True, self.colors['text'])
            qty_pos = (rect.right - 15, rect.bottom - 15)
            surface.blit(qty_text, qty_pos)
    
    def _draw_dragging_item(self, surface: pygame.Surface) -> None:
        """ドラッグ中のアイテムを描画"""
        if self.dragging_slot < 0:
            return
        
        slot = self.inventory.get_slot(self.dragging_slot)
        if not slot or slot.is_empty():
            return
        
        mouse_pos = pygame.mouse.get_pos()
        drag_rect = pygame.Rect(
            mouse_pos[0] - self.drag_offset[0],
            mouse_pos[1] - self.drag_offset[1],
            self.slot_size,
            self.slot_size
        )
        
        # 半透明で描画
        temp_surface = pygame.Surface((self.slot_size, self.slot_size), pygame.SRCALPHA)
        temp_surface.set_alpha(128)
        
        # 背景
        pygame.draw.rect(temp_surface, self.colors['slot_filled'], 
                        (0, 0, self.slot_size, self.slot_size))
        pygame.draw.rect(temp_surface, self.colors['slot_border'], 
                        (0, 0, self.slot_size, self.slot_size), 2)
        
        # アイテム描画
        item_rect = pygame.Rect(4, 4, self.slot_size - 8, self.slot_size - 8)
        item = self.item_system.get_item(slot.item_id)
        if item:
            rarity_color = self._get_rarity_color(item.rarity)
            pygame.draw.rect(temp_surface, rarity_color, item_rect, 2)
            
            font = pygame.font.Font(None, 24)
            text = font.render(item.name[0], True, self.colors['text'])
            text_rect = text.get_rect(center=item_rect.center)
            temp_surface.blit(text, text_rect)
        
        surface.blit(temp_surface, drag_rect)
    
    def add_item(self, item_id: str, quantity: int = 1) -> int:
        """アイテムを追加"""
        return self.inventory.add_item(item_id, quantity)
    
    def remove_item(self, item_id: str, quantity: int = 1) -> int:
        """アイテムを削除"""
        return self.inventory.remove_item(item_id, quantity)
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """アイテムを持っているかチェック"""
        return self.inventory.has_item(item_id, quantity)
