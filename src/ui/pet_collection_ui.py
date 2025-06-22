"""
ペット図鑑UI
図鑑の表示、検索、フィルター機能を提供
"""

import pygame
import pygame_gui
from typing import List, Optional, Dict, Any
from enum import Enum

from src.systems.pet_collection import PetCollection, PetInfo, PetRescueRecord
from src.ui.pet_detail_ui import PetDetailUI

class FilterType(Enum):
    """フィルタータイプ"""
    ALL = "all"
    RESCUED = "rescued"
    UNRESCUED = "unrescued"
    SPECIES = "species"
    RARITY = "rarity"

class PetCollectionUI:
    """ペット図鑑UIクラス"""
    
    def __init__(self, screen: pygame.Surface, ui_manager: pygame_gui.UIManager):
        self.screen = screen
        self.ui_manager = ui_manager
        self.pet_collection = PetCollection()
        self.pet_detail_ui = PetDetailUI(screen, ui_manager)
        
        # UI要素
        self.container = None
        self.search_entry = None
        self.filter_dropdown = None
        self.species_dropdown = None
        self.rarity_dropdown = None
        self.pet_list = None
        self.stats_label = None
        self.close_button = None
        
        # 状態管理
        self.is_visible = False
        self.current_filter = FilterType.ALL
        self.current_pets: List[PetInfo] = []
        self.selected_pet_id: Optional[str] = None
        
        self._create_ui()
        self._update_pet_list()
    
    def _create_ui(self) -> None:
        """UI要素を作成"""
        screen_width, screen_height = self.screen.get_size()
        
        # メインコンテナ
        self.container = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(50, 50, screen_width - 100, screen_height - 100),
            starting_layer_height=10,
            manager=self.ui_manager
        )
        
        # タイトル
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 10, 200, 30),
            text='ペット図鑑',
            manager=self.ui_manager,
            container=self.container
        )
        
        # 閉じるボタン
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(-80, 10, 60, 30),
            text='閉じる',
            manager=self.ui_manager,
            container=self.container,
            anchors={'right': 'right'}
        )
        
        # 検索ボックス
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 50, 60, 25),
            text='検索:',
            manager=self.ui_manager,
            container=self.container
        )
        
        self.search_entry = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(80, 50, 200, 25),
            manager=self.ui_manager,
            container=self.container
        )
        
        # フィルタードロップダウン
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(300, 50, 60, 25),
            text='フィルター:',
            manager=self.ui_manager,
            container=self.container
        )
        
        self.filter_dropdown = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(370, 50, 120, 25),
            options_list=['すべて', '救助済み', '未救助', '種類別', 'レア度別'],
            starting_option='すべて',
            manager=self.ui_manager,
            container=self.container
        )
        
        # 種類別フィルター（初期は非表示）
        self.species_dropdown = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(500, 50, 100, 25),
            options_list=['犬', '猫', 'うさぎ', '鳥'],
            starting_option='犬',
            manager=self.ui_manager,
            container=self.container,
            visible=False
        )
        
        # レア度別フィルター（初期は非表示）
        self.rarity_dropdown = pygame_gui.elements.UIDropDownMenu(
            relative_rect=pygame.Rect(500, 50, 100, 25),
            options_list=['コモン', 'アンコモン', 'レア', 'レジェンダリー'],
            starting_option='コモン',
            manager=self.ui_manager,
            container=self.container,
            visible=False
        )
        
        # 統計情報
        self.stats_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 85, 400, 25),
            text='',
            manager=self.ui_manager,
            container=self.container
        )
        
        # ペットリスト
        self.pet_list = pygame_gui.elements.UISelectionList(
            relative_rect=pygame.Rect(20, 120, -40, -40),
            item_list=[],
            manager=self.ui_manager,
            container=self.container,
            anchors={'right': 'right', 'bottom': 'bottom'}
        )
        
        # 初期状態では非表示
        self.container.visible = False
    
    def _update_pet_list(self) -> None:
        """ペットリストを更新"""
        # 現在のフィルターに基づいてペットを取得
        if self.current_filter == FilterType.ALL:
            self.current_pets = self.pet_collection.get_all_pets()
        elif self.current_filter == FilterType.RESCUED:
            self.current_pets = self.pet_collection.get_rescued_pets()
        elif self.current_filter == FilterType.UNRESCUED:
            self.current_pets = self.pet_collection.get_unrescued_pets()
        
        # 検索クエリがある場合はさらにフィルター
        if self.search_entry and self.search_entry.get_text().strip():
            query = self.search_entry.get_text().strip()
            self.current_pets = [pet for pet in self.current_pets 
                               if query.lower() in pet.name.lower() or 
                                  query.lower() in pet.species.lower() or
                                  query.lower() in pet.breed.lower()]
        
        # リスト項目を作成
        list_items = []
        for pet in self.current_pets:
            rescued_status = "✓" if self.pet_collection.is_pet_rescued(pet.id) else "✗"
            rarity_info = self.pet_collection.get_rarity_info(pet.rarity)
            
            item_text = f"{rescued_status} {pet.name} ({pet.species}) - {rarity_info['name']}"
            list_items.append(item_text)
        
        # リストを更新
        if self.pet_list:
            self.pet_list.set_item_list(list_items)
        
        # 統計情報を更新
        self._update_stats()
    
    def _update_stats(self) -> None:
        """統計情報を更新"""
        stats = self.pet_collection.get_collection_stats()
        stats_text = (f"図鑑完成度: {stats['rescued_pets']}/{stats['total_pets']} "
                     f"({stats['completion_rate']:.1f}%)")
        
        if self.stats_label:
            self.stats_label.set_text(stats_text)
    
    def _handle_filter_change(self, selected_option: str) -> None:
        """フィルター変更を処理"""
        # 追加フィルターを非表示
        if self.species_dropdown:
            self.species_dropdown.visible = False
        if self.rarity_dropdown:
            self.rarity_dropdown.visible = False
        
        if selected_option == 'すべて':
            self.current_filter = FilterType.ALL
        elif selected_option == '救助済み':
            self.current_filter = FilterType.RESCUED
        elif selected_option == '未救助':
            self.current_filter = FilterType.UNRESCUED
        elif selected_option == '種類別':
            self.current_filter = FilterType.SPECIES
            if self.species_dropdown:
                self.species_dropdown.visible = True
        elif selected_option == 'レア度別':
            self.current_filter = FilterType.RARITY
            if self.rarity_dropdown:
                self.rarity_dropdown.visible = True
        
        self._apply_current_filter()
    
    def _apply_current_filter(self) -> None:
        """現在のフィルターを適用"""
        if self.current_filter == FilterType.SPECIES and self.species_dropdown:
            species_map = {'犬': '犬', '猫': '猫', 'うさぎ': 'うさぎ', '鳥': '鳥'}
            selected_species = species_map.get(self.species_dropdown.selected_option, '犬')
            self.current_pets = self.pet_collection.filter_pets_by_species(selected_species)
        elif self.current_filter == FilterType.RARITY and self.rarity_dropdown:
            rarity_map = {
                'コモン': 'common',
                'アンコモン': 'uncommon', 
                'レア': 'rare',
                'レジェンダリー': 'legendary'
            }
            selected_rarity = rarity_map.get(self.rarity_dropdown.selected_option, 'common')
            self.current_pets = self.pet_collection.filter_pets_by_rarity(selected_rarity)
        else:
            self._update_pet_list()
            return
        
        # 検索クエリがある場合はさらにフィルター
        if self.search_entry and self.search_entry.get_text().strip():
            query = self.search_entry.get_text().strip()
            self.current_pets = [pet for pet in self.current_pets 
                               if query.lower() in pet.name.lower() or 
                                  query.lower() in pet.species.lower() or
                                  query.lower() in pet.breed.lower()]
        
        # リスト項目を作成
        list_items = []
        for pet in self.current_pets:
            rescued_status = "✓" if self.pet_collection.is_pet_rescued(pet.id) else "✗"
            rarity_info = self.pet_collection.get_rarity_info(pet.rarity)
            
            item_text = f"{rescued_status} {pet.name} ({pet.species}) - {rarity_info['name']}"
            list_items.append(item_text)
        
        # リストを更新
        if self.pet_list:
            self.pet_list.set_item_list(list_items)
        
        # 統計情報を更新
        self._update_stats()
    
    def show(self) -> None:
        """図鑑を表示"""
        self.is_visible = True
        if self.container:
            self.container.visible = True
        self._update_pet_list()
    
    def hide(self) -> None:
        """図鑑を非表示"""
        self.is_visible = False
        if self.container:
            self.container.visible = False
        self.pet_detail_ui.hide()
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベントを処理"""
        if not self.is_visible:
            return False
        
        # 詳細画面が表示中の場合は詳細画面にイベントを渡す
        if self.pet_detail_ui.is_visible:
            if self.pet_detail_ui.handle_event(event):
                return True
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.close_button:
                self.hide()
                return True
        
        elif event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if event.ui_element == self.filter_dropdown:
                self._handle_filter_change(event.text)
                return True
            elif event.ui_element == self.species_dropdown:
                self._apply_current_filter()
                return True
            elif event.ui_element == self.rarity_dropdown:
                self._apply_current_filter()
                return True
        
        elif event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if event.ui_element == self.search_entry:
                self._update_pet_list()
                return True
        
        elif event.type == pygame_gui.UI_SELECTION_LIST_NEW_SELECTION:
            if event.ui_element == self.pet_list:
                # 選択されたペットの詳細を表示
                selected_index = self.pet_list.get_single_selection()
                if selected_index is not None and selected_index < len(self.current_pets):
                    selected_pet = self.current_pets[selected_index]
                    self.selected_pet_id = selected_pet.id
                    self.pet_detail_ui.show_pet_detail(selected_pet.id)
                return True
        
        return False
    
    def update(self, time_delta: float) -> None:
        """UIを更新"""
        if self.is_visible:
            # 詳細画面も更新
            if self.pet_detail_ui.is_visible:
                self.pet_detail_ui.update(time_delta)
    
    def draw(self, surface: pygame.Surface) -> None:
        """UIを描画"""
        if self.is_visible:
            # 詳細画面も描画
            if self.pet_detail_ui.is_visible:
                self.pet_detail_ui.draw(surface)
