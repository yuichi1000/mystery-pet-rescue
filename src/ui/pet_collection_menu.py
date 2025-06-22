"""
ペット図鑑メニュー
発見したペットの管理と表示
"""

import pygame
import json
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path

from src.utils.font_manager import get_font_manager

@dataclass
class PetData:
    """ペットデータ"""
    id: str
    name: str
    species: str
    description: str
    rarity: str
    found_date: str = ""
    found_location: str = ""
    is_discovered: bool = False
    image_path: str = ""

class PetCollectionMenu:
    """ペット図鑑メニュークラス"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # フォントマネージャー
        self.font_manager = get_font_manager()
        
        # UI状態
        self.selected_pet = 0
        self.view_mode = "grid"  # "grid" or "detail"
        self.filter_rarity = "all"  # "all", "common", "rare", "legendary"
        self.scroll_offset = 0
        
        # 色設定
        self.colors = {
            'background': (34, 139, 34),
            'panel': (60, 120, 60),
            'selected': (100, 200, 100),
            'text': (255, 255, 255),
            'rarity_common': (169, 169, 169),
            'rarity_rare': (65, 105, 225),
            'rarity_legendary': (255, 215, 0),
            'undiscovered': (100, 100, 100)
        }
        
        # ペットデータを読み込み
        self.pets_data = self._load_pets_data()
        self.collection_data = self._load_collection_data()
        
        # レイアウト設定
        self.grid_cols = 4
        self.grid_rows = 3
        self.pet_card_size = (150, 120)
        
        print(f"📖 ペット図鑑初期化完了: {len(self.pets_data)}種類")
    
    def _load_pets_data(self) -> List[PetData]:
        """ペットデータを読み込み"""
        pets_file = "data/pets_database.json"
        default_pets = [
            {
                "id": "cat_001",
                "name": "ミケ",
                "species": "三毛猫",
                "description": "人懐っこい三毛猫。好奇心旺盛で、いつも何かを探している。",
                "rarity": "common",
                "image_path": "assets/images/pets/cat_001.png"
            },
            {
                "id": "dog_001", 
                "name": "ポチ",
                "species": "柴犬",
                "description": "忠実な柴犬。飼い主を探して街を彷徨っている。",
                "rarity": "common",
                "image_path": "assets/images/pets/dog_001.png"
            },
            {
                "id": "rabbit_001",
                "name": "ウサ吉",
                "species": "ウサギ",
                "description": "ふわふわの毛が特徴的なウサギ。とても臆病な性格。",
                "rarity": "rare",
                "image_path": "assets/images/pets/rabbit_001.png"
            },
            {
                "id": "bird_001",
                "name": "ピーちゃん",
                "species": "インコ",
                "description": "色鮮やかな羽を持つインコ。人の言葉を真似するのが得意。",
                "rarity": "rare",
                "image_path": "assets/images/pets/bird_001.png"
            },
            {
                "id": "cat_002",
                "name": "シロ",
                "species": "白猫",
                "description": "真っ白な毛が美しい猫。とても神秘的な雰囲気を持つ。",
                "rarity": "legendary",
                "image_path": "assets/images/pets/cat_002.png"
            }
        ]
        
        try:
            if Path(pets_file).exists():
                with open(pets_file, 'r', encoding='utf-8') as f:
                    pets_json = json.load(f)
                    return [PetData(**pet) for pet in pets_json.get('pets', default_pets)]
        except Exception as e:
            print(f"⚠️ ペットデータ読み込みエラー: {e}")
        
        return [PetData(**pet) for pet in default_pets]
    
    def _load_collection_data(self) -> Dict[str, Dict[str, Any]]:
        """コレクションデータを読み込み"""
        collection_file = "saves/pet_collection.json"
        try:
            if Path(collection_file).exists():
                with open(collection_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ コレクションデータ読み込みエラー: {e}")
        
        return {}
    
    def _save_collection_data(self):
        """コレクションデータを保存"""
        collection_file = "saves/pet_collection.json"
        try:
            Path(collection_file).parent.mkdir(parents=True, exist_ok=True)
            with open(collection_file, 'w', encoding='utf-8') as f:
                json.dump(self.collection_data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"❌ コレクションデータ保存エラー: {e}")
    
    def update(self, events: List[pygame.event.Event]) -> Optional[str]:
        """ペット図鑑を更新"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                result = self._handle_keyboard_input(event.key)
                if result:
                    return result
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左クリック
                    self._handle_mouse_click(event.pos)
                elif event.button == 4:  # マウスホイール上
                    self._scroll(-1)
                elif event.button == 5:  # マウスホイール下
                    self._scroll(1)
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_hover(event.pos)
        
        return None
    
    def _handle_keyboard_input(self, key: int) -> Optional[str]:
        """キーボード入力処理"""
        if key == pygame.K_ESCAPE:
            return "back"
        
        elif key == pygame.K_TAB:
            self.view_mode = "detail" if self.view_mode == "grid" else "grid"
            print(f"🔄 表示モード切り替え: {self.view_mode}")
        
        elif key == pygame.K_f:
            self._cycle_filter()
        
        elif self.view_mode == "grid":
            self._handle_grid_navigation(key)
        
        elif self.view_mode == "detail":
            self._handle_detail_navigation(key)
        
        return None
    
    def _handle_grid_navigation(self, key: int):
        """グリッド表示のナビゲーション"""
        visible_pets = self._get_filtered_pets()
        if not visible_pets:
            return
        
        if key == pygame.K_LEFT:
            if self.selected_pet % self.grid_cols > 0:
                self.selected_pet -= 1
        
        elif key == pygame.K_RIGHT:
            if self.selected_pet % self.grid_cols < self.grid_cols - 1 and self.selected_pet < len(visible_pets) - 1:
                self.selected_pet += 1
        
        elif key == pygame.K_UP:
            if self.selected_pet >= self.grid_cols:
                self.selected_pet -= self.grid_cols
        
        elif key == pygame.K_DOWN:
            if self.selected_pet + self.grid_cols < len(visible_pets):
                self.selected_pet += self.grid_cols
        
        elif key == pygame.K_RETURN:
            self.view_mode = "detail"
    
    def _handle_detail_navigation(self, key: int):
        """詳細表示のナビゲーション"""
        visible_pets = self._get_filtered_pets()
        if not visible_pets:
            return
        
        if key == pygame.K_LEFT:
            self.selected_pet = (self.selected_pet - 1) % len(visible_pets)
        
        elif key == pygame.K_RIGHT:
            self.selected_pet = (self.selected_pet + 1) % len(visible_pets)
        
        elif key == pygame.K_RETURN:
            self.view_mode = "grid"
    
    def _handle_mouse_click(self, pos):
        """マウスクリック処理"""
        if self.view_mode == "grid":
            self._handle_grid_click(pos)
        
        # フィルターボタンのクリック処理
        filter_buttons = self._get_filter_button_rects()
        for rarity, rect in filter_buttons.items():
            if rect.collidepoint(pos):
                self.filter_rarity = rarity
                print(f"🔍 フィルター変更: {rarity}")
                break
    
    def _handle_grid_click(self, pos):
        """グリッドクリック処理"""
        visible_pets = self._get_filtered_pets()
        grid_start_x = 50
        grid_start_y = 150
        
        for i, pet in enumerate(visible_pets):
            if i >= self.grid_cols * self.grid_rows:
                break
            
            row = i // self.grid_cols
            col = i % self.grid_cols
            
            pet_x = grid_start_x + col * (self.pet_card_size[0] + 20)
            pet_y = grid_start_y + row * (self.pet_card_size[1] + 20)
            pet_rect = pygame.Rect(pet_x, pet_y, *self.pet_card_size)
            
            if pet_rect.collidepoint(pos):
                self.selected_pet = i
                self.view_mode = "detail"
                break
    
    def _handle_mouse_hover(self, pos):
        """マウスホバー処理"""
        if self.view_mode == "grid":
            visible_pets = self._get_filtered_pets()
            grid_start_x = 50
            grid_start_y = 150
            
            for i, pet in enumerate(visible_pets):
                if i >= self.grid_cols * self.grid_rows:
                    break
                
                row = i // self.grid_cols
                col = i % self.grid_cols
                
                pet_x = grid_start_x + col * (self.pet_card_size[0] + 20)
                pet_y = grid_start_y + row * (self.pet_card_size[1] + 20)
                pet_rect = pygame.Rect(pet_x, pet_y, *self.pet_card_size)
                
                if pet_rect.collidepoint(pos):
                    self.selected_pet = i
                    break
    
    def _scroll(self, direction: int):
        """スクロール処理"""
        self.scroll_offset += direction * 30
        self.scroll_offset = max(0, self.scroll_offset)
    
    def _cycle_filter(self):
        """フィルターを循環"""
        filters = ["all", "common", "rare", "legendary"]
        current_index = filters.index(self.filter_rarity)
        self.filter_rarity = filters[(current_index + 1) % len(filters)]
        print(f"🔍 フィルター: {self.filter_rarity}")
    
    def _get_filtered_pets(self) -> List[PetData]:
        """フィルターされたペットリストを取得"""
        if self.filter_rarity == "all":
            return self.pets_data
        else:
            return [pet for pet in self.pets_data if pet.rarity == self.filter_rarity]
    
    def _get_filter_button_rects(self) -> Dict[str, pygame.Rect]:
        """フィルターボタンの矩形を取得"""
        buttons = {}
        filters = ["all", "common", "rare", "legendary"]
        button_width = 100
        start_x = self.screen_width - 450
        
        for i, filter_name in enumerate(filters):
            rect = pygame.Rect(start_x + i * (button_width + 10), 100, button_width, 30)
            buttons[filter_name] = rect
        
        return buttons
    
    def _is_pet_discovered(self, pet_id: str) -> bool:
        """ペットが発見済みかチェック"""
        return pet_id in self.collection_data
    
    def discover_pet(self, pet_id: str, location: str = ""):
        """ペットを発見"""
        if pet_id not in self.collection_data:
            import datetime
            self.collection_data[pet_id] = {
                "found_date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "found_location": location
            }
            self._save_collection_data()
            print(f"🎉 新しいペットを発見: {pet_id}")
    
    def get_collection_stats(self) -> Dict[str, int]:
        """コレクション統計を取得"""
        total_pets = len(self.pets_data)
        discovered_pets = len(self.collection_data)
        
        rarity_stats = {"common": 0, "rare": 0, "legendary": 0}
        discovered_rarity = {"common": 0, "rare": 0, "legendary": 0}
        
        for pet in self.pets_data:
            rarity_stats[pet.rarity] += 1
            if self._is_pet_discovered(pet.id):
                discovered_rarity[pet.rarity] += 1
        
        return {
            "total_pets": total_pets,
            "discovered_pets": discovered_pets,
            "completion_rate": int((discovered_pets / total_pets) * 100) if total_pets > 0 else 0,
            "rarity_stats": rarity_stats,
            "discovered_rarity": discovered_rarity
        }
    
    def draw(self):
        """ペット図鑑を描画"""
        # 背景
        self.screen.fill(self.colors['background'])
        
        # タイトル
        title_surface = self.font_manager.render_text("ペット図鑑", 36, self.colors['text'])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title_surface, title_rect)
        
        # 統計情報
        self._draw_stats()
        
        # フィルターボタン
        self._draw_filter_buttons()
        
        # メイン表示
        if self.view_mode == "grid":
            self._draw_grid_view()
        else:
            self._draw_detail_view()
        
        # 操作説明
        self._draw_controls()
    
    def _draw_stats(self):
        """統計情報を描画"""
        stats = self.get_collection_stats()
        
        stats_text = f"発見: {stats['discovered_pets']}/{stats['total_pets']} ({stats['completion_rate']}%)"
        stats_surface = self.font_manager.render_text(stats_text, 20, self.colors['text'])
        self.screen.blit(stats_surface, (50, 100))
    
    def _draw_filter_buttons(self):
        """フィルターボタンを描画"""
        filter_buttons = self._get_filter_button_rects()
        filter_names = {
            "all": "すべて",
            "common": "コモン",
            "rare": "レア",
            "legendary": "レジェンド"
        }
        
        for filter_key, rect in filter_buttons.items():
            # ボタン背景
            is_selected = filter_key == self.filter_rarity
            bg_color = self.colors['selected'] if is_selected else self.colors['panel']
            pygame.draw.rect(self.screen, bg_color, rect)
            pygame.draw.rect(self.screen, self.colors['text'], rect, 2)
            
            # ボタンテキスト
            text = filter_names.get(filter_key, filter_key)
            text_surface = self.font_manager.render_text(text, 14, self.colors['text'])
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_grid_view(self):
        """グリッド表示を描画"""
        visible_pets = self._get_filtered_pets()
        grid_start_x = 50
        grid_start_y = 150
        
        for i, pet in enumerate(visible_pets):
            if i >= self.grid_cols * self.grid_rows:
                break
            
            row = i // self.grid_cols
            col = i % self.grid_cols
            
            pet_x = grid_start_x + col * (self.pet_card_size[0] + 20)
            pet_y = grid_start_y + row * (self.pet_card_size[1] + 20)
            
            self._draw_pet_card(pet, pet_x, pet_y, i == self.selected_pet)
    
    def _draw_pet_card(self, pet: PetData, x: int, y: int, is_selected: bool):
        """ペットカードを描画"""
        card_rect = pygame.Rect(x, y, *self.pet_card_size)
        is_discovered = self._is_pet_discovered(pet.id)
        
        # カード背景
        if is_selected:
            bg_color = self.colors['selected']
        elif is_discovered:
            bg_color = self.colors['panel']
        else:
            bg_color = self.colors['undiscovered']
        
        pygame.draw.rect(self.screen, bg_color, card_rect)
        pygame.draw.rect(self.screen, self.colors['text'], card_rect, 2)
        
        if is_discovered:
            # ペット名
            name_surface = self.font_manager.render_text(pet.name, 16, self.colors['text'])
            name_rect = name_surface.get_rect(center=(x + self.pet_card_size[0] // 2, y + 20))
            self.screen.blit(name_surface, name_rect)
            
            # 種族
            species_surface = self.font_manager.render_text(pet.species, 12, self.colors['text'])
            species_rect = species_surface.get_rect(center=(x + self.pet_card_size[0] // 2, y + 40))
            self.screen.blit(species_surface, species_rect)
            
            # レアリティ
            rarity_color = self.colors.get(f'rarity_{pet.rarity}', self.colors['text'])
            rarity_surface = self.font_manager.render_text(pet.rarity.upper(), 10, rarity_color)
            rarity_rect = rarity_surface.get_rect(center=(x + self.pet_card_size[0] // 2, y + self.pet_card_size[1] - 15))
            self.screen.blit(rarity_surface, rarity_rect)
        else:
            # 未発見
            unknown_surface = self.font_manager.render_text("???", 24, self.colors['text'])
            unknown_rect = unknown_surface.get_rect(center=card_rect.center)
            self.screen.blit(unknown_surface, unknown_rect)
    
    def _draw_detail_view(self):
        """詳細表示を描画"""
        visible_pets = self._get_filtered_pets()
        if not visible_pets or self.selected_pet >= len(visible_pets):
            return
        
        pet = visible_pets[self.selected_pet]
        is_discovered = self._is_pet_discovered(pet.id)
        
        # 詳細パネル
        detail_rect = pygame.Rect(100, 150, self.screen_width - 200, self.screen_height - 250)
        pygame.draw.rect(self.screen, self.colors['panel'], detail_rect)
        pygame.draw.rect(self.screen, self.colors['text'], detail_rect, 3)
        
        if is_discovered:
            # ペット情報
            info_y = detail_rect.y + 30
            
            # 名前
            name_surface = self.font_manager.render_text(pet.name, 32, self.colors['text'])
            self.screen.blit(name_surface, (detail_rect.x + 30, info_y))
            info_y += 50
            
            # 種族
            species_text = f"種族: {pet.species}"
            species_surface = self.font_manager.render_text(species_text, 20, self.colors['text'])
            self.screen.blit(species_surface, (detail_rect.x + 30, info_y))
            info_y += 35
            
            # レアリティ
            rarity_color = self.colors.get(f'rarity_{pet.rarity}', self.colors['text'])
            rarity_text = f"レアリティ: {pet.rarity.upper()}"
            rarity_surface = self.font_manager.render_text(rarity_text, 18, rarity_color)
            self.screen.blit(rarity_surface, (detail_rect.x + 30, info_y))
            info_y += 35
            
            # 説明
            desc_lines = self._wrap_text(pet.description, 16, detail_rect.width - 60)
            for line in desc_lines:
                desc_surface = self.font_manager.render_text(line, 16, self.colors['text'])
                self.screen.blit(desc_surface, (detail_rect.x + 30, info_y))
                info_y += 25
            
            # 発見情報
            if pet.id in self.collection_data:
                collection_info = self.collection_data[pet.id]
                info_y += 20
                
                found_text = f"発見日時: {collection_info.get('found_date', '不明')}"
                found_surface = self.font_manager.render_text(found_text, 14, self.colors['text'])
                self.screen.blit(found_surface, (detail_rect.x + 30, info_y))
                info_y += 25
                
                if collection_info.get('found_location'):
                    location_text = f"発見場所: {collection_info['found_location']}"
                    location_surface = self.font_manager.render_text(location_text, 14, self.colors['text'])
                    self.screen.blit(location_surface, (detail_rect.x + 30, info_y))
        else:
            # 未発見表示
            unknown_surface = self.font_manager.render_text("このペットはまだ発見されていません", 24, self.colors['text'])
            unknown_rect = unknown_surface.get_rect(center=detail_rect.center)
            self.screen.blit(unknown_surface, unknown_rect)
    
    def _wrap_text(self, text: str, font_size: int, max_width: int) -> List[str]:
        """テキストを指定幅で改行"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_width = self.font_manager.get_text_size(test_line, font_size)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _draw_controls(self):
        """操作説明を描画"""
        controls = [
            "TAB: 表示切り替え",
            "F: フィルター切り替え",
            "矢印キー: 選択",
            "Enter: 詳細表示",
            "ESC: 戻る"
        ]
        
        start_y = self.screen_height - 120
        for i, control in enumerate(controls):
            control_surface = self.font_manager.render_text(control, 12, self.colors['text'])
            self.screen.blit(control_surface, (50, start_y + i * 18))
