#!/usr/bin/env python3
"""
インタラクティブなペット図鑑デモ
マウス操作とキーボード操作に対応
"""

import sys
import os
import pygame
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.pet_collection import PetCollection

class InteractivePetCollection:
    """インタラクティブなペット図鑑"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("🐾 ミステリー・ペット・レスキュー - インタラクティブ図鑑")
        self.clock = pygame.time.Clock()
        
        # フォント
        self.title_font = pygame.font.Font(None, 48)
        self.header_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # 色定義
        self.colors = {
            'background': (240, 248, 255),
            'white': (255, 255, 255),
            'black': (50, 50, 50),
            'gray': (128, 128, 128),
            'light_gray': (200, 200, 200),
            'green': (76, 175, 80),
            'red': (244, 67, 54),
            'blue': (33, 150, 243),
            'orange': (255, 152, 0),
            'purple': (156, 39, 176),
            'yellow': (255, 235, 59)
        }
        
        # レア度の色マッピング
        self.rarity_colors = {
            'common': self.colors['green'],
            'uncommon': self.colors['blue'],
            'rare': self.colors['orange'],
            'legendary': self.colors['purple']
        }
        
        # ペット図鑑システム
        self.pet_collection = PetCollection()
        
        # 表示状態
        self.scroll_y = 0
        self.selected_pet_id = None
        self.show_details = False
        self.filter_mode = "all"  # all, rescued, unrescued
        self.current_pets = self.pet_collection.get_all_pets()
        
        # インタラクション
        self.pet_rects = []
        self.button_rects = {}
        
        print("🐾 インタラクティブペット図鑑起動")
        print("\n🎮 操作方法:")
        print("  - マウス: ペットカードをクリック")
        print("  - 1/2/3: フィルター切り替え (全て/救助済み/未救助)")
        print("  - R: ランダムペット救助")
        print("  - SPACE: 詳細表示切り替え")
        print("  - マウスホイール: スクロール")
        print("  - ESC: 終了")
    
    def update_filter(self):
        """フィルターに基づいてペット一覧を更新"""
        if self.filter_mode == "rescued":
            self.current_pets = self.pet_collection.get_rescued_pets()
        elif self.filter_mode == "unrescued":
            self.current_pets = self.pet_collection.get_unrescued_pets()
        else:
            self.current_pets = self.pet_collection.get_all_pets()
    
    def rescue_random_pet(self):
        """ランダムなペットを救助"""
        unrescued = self.pet_collection.get_unrescued_pets()
        if unrescued:
            import random
            pet = random.choice(unrescued)
            locations = pet.found_locations
            location = random.choice(locations) if locations else "不明な場所"
            time_spent = random.randint(60, 300)
            
            self.pet_collection.rescue_pet(pet.id, location, time_spent)
            print(f"🎉 {pet.name}を{location}で救助しました！ (所要時間: {time_spent}秒)")
            return True
        return False
    
    def draw_text(self, text, font, color, x, y, center=False):
        """テキストを描画"""
        text_surface = font.render(str(text), True, color)
        if center:
            rect = text_surface.get_rect(center=(x, y))
            self.screen.blit(text_surface, rect)
        else:
            self.screen.blit(text_surface, (x, y))
        return text_surface.get_height()
    
    def draw_pet_card(self, pet, x, y, width, height, is_rescued):
        """ペットカードを描画"""
        # カード背景
        card_color = self.colors['white'] if is_rescued else self.colors['light_gray']
        card_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, card_color, card_rect)
        
        # 選択状態の表示
        border_color = self.colors['yellow'] if pet.id == self.selected_pet_id else self.colors['gray']
        border_width = 3 if pet.id == self.selected_pet_id else 2
        pygame.draw.rect(self.screen, border_color, card_rect, border_width)
        
        # レア度インジケーター
        rarity_color = self.rarity_colors.get(pet.rarity, self.colors['gray'])
        pygame.draw.rect(self.screen, rarity_color, (x, y, width, 5))
        
        # ペット情報
        text_y = y + 15
        
        # 名前
        name_color = self.colors['black'] if is_rescued else self.colors['gray']
        text_y += self.draw_text(f"🐾 {pet.name}", self.text_font, name_color, x + 10, text_y)
        
        # 種類・品種
        species_text = f"{pet.species} - {pet.breed}"
        text_y += self.draw_text(species_text, self.small_font, self.colors['gray'], x + 10, text_y)
        
        # 救助状態
        status_text = "✅ 救助済み" if is_rescued else "❌ 未救助"
        status_color = self.colors['green'] if is_rescued else self.colors['red']
        text_y += self.draw_text(status_text, self.small_font, status_color, x + 10, text_y)
        
        # レア度
        rarity_info = self.pet_collection.get_rarity_info(pet.rarity)
        rarity_text = f"⭐ {rarity_info['name']}"
        text_y += self.draw_text(rarity_text, self.small_font, rarity_color, x + 10, text_y)
        
        # 難易度
        difficulty_text = f"🎯 難易度: {'★' * pet.rescue_difficulty}"
        text_y += self.draw_text(difficulty_text, self.small_font, self.colors['orange'], x + 10, text_y)
        
        # 詳細情報（選択時）
        if pet.id == self.selected_pet_id and self.show_details:
            text_y += 5
            # 説明
            desc_lines = self.wrap_text(pet.description, width - 20, self.small_font)
            for line in desc_lines:
                text_y += self.draw_text(line, self.small_font, self.colors['black'], x + 10, text_y)
            
            # 発見場所
            if pet.found_locations:
                text_y += 5
                text_y += self.draw_text("📍 発見場所:", self.small_font, self.colors['blue'], x + 10, text_y)
                for location in pet.found_locations:
                    text_y += self.draw_text(f"  • {location}", self.small_font, self.colors['gray'], x + 10, text_y)
        
        return card_rect
    
    def wrap_text(self, text, max_width, font):
        """テキストを指定幅で折り返し"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def draw_stats_panel(self):
        """統計パネルを描画"""
        stats = self.pet_collection.get_collection_stats()
        
        # パネル背景
        panel_rect = pygame.Rect(900, 100, 350, 250)
        pygame.draw.rect(self.screen, self.colors['white'], panel_rect)
        pygame.draw.rect(self.screen, self.colors['gray'], panel_rect, 2)
        
        # タイトル
        y = 120
        y += self.draw_text("📊 図鑑統計", self.header_font, self.colors['black'], 920, y)
        y += 10
        
        # 基本統計
        completion_text = f"🏆 完成率: {stats['completion_rate']:.1f}%"
        y += self.draw_text(completion_text, self.text_font, self.colors['black'], 920, y)
        
        rescued_text = f"✅ 救助済み: {stats['rescued_pets']}/{stats['total_pets']}匹"
        y += self.draw_text(rescued_text, self.text_font, self.colors['green'], 920, y)
        y += 10
        
        # レア度別統計
        y += self.draw_text("🌟 レア度別:", self.small_font, self.colors['gray'], 920, y)
        for rarity, data in stats['rarity_stats'].items():
            if data['total'] > 0:
                rarity_info = self.pet_collection.get_rarity_info(rarity)
                rarity_color = self.rarity_colors.get(rarity, self.colors['gray'])
                rarity_text = f"  {rarity_info['name']}: {data['rescued']}/{data['total']}"
                y += self.draw_text(rarity_text, self.small_font, rarity_color, 920, y)
        
        y += 10
        # フィルター状態
        filter_text = f"🔍 フィルター: {self.filter_mode}"
        y += self.draw_text(filter_text, self.small_font, self.colors['blue'], 920, y)
    
    def draw_controls(self):
        """操作説明を描画"""
        controls = [
            "🎮 操作方法:",
            "1/2/3: フィルター切り替え",
            "R: ランダム救助",
            "SPACE: 詳細表示",
            "マウス: ペット選択",
            "ESC: 終了"
        ]
        
        y = 400
        for control in controls:
            y += self.draw_text(control, self.small_font, self.colors['gray'], 920, y)
    
    def handle_click(self, pos):
        """マウスクリックを処理"""
        for i, rect in enumerate(self.pet_rects):
            if rect.collidepoint(pos) and i < len(self.current_pets):
                pet = self.current_pets[i]
                if self.selected_pet_id == pet.id:
                    self.show_details = not self.show_details
                else:
                    self.selected_pet_id = pet.id
                    self.show_details = True
                print(f"🐾 選択: {pet.name} ({pet.species})")
                return True
        return False
    
    def run(self):
        """メインループ"""
        running = True
        
        while running:
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_1:
                        self.filter_mode = "all"
                        self.update_filter()
                        print("🔍 フィルター: 全て")
                    elif event.key == pygame.K_2:
                        self.filter_mode = "rescued"
                        self.update_filter()
                        print("🔍 フィルター: 救助済み")
                    elif event.key == pygame.K_3:
                        self.filter_mode = "unrescued"
                        self.update_filter()
                        print("🔍 フィルター: 未救助")
                    elif event.key == pygame.K_r:
                        if self.rescue_random_pet():
                            self.update_filter()
                    elif event.key == pygame.K_SPACE:
                        self.show_details = not self.show_details
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll_y += event.y * 30
                    self.scroll_y = max(0, min(self.scroll_y, 500))
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # 左クリック
                        self.handle_click(event.pos)
            
            # 描画
            self.screen.fill(self.colors['background'])
            
            # タイトル
            self.draw_text("🐾 ペット図鑑", self.title_font, self.colors['black'], 640, 50, center=True)
            
            # ペット一覧
            self.pet_rects = []
            card_width = 400
            card_height = 140 if self.show_details and self.selected_pet_id else 120
            cards_per_row = 2
            start_x = 50
            start_y = 100 - self.scroll_y
            
            for i, pet in enumerate(self.current_pets):
                row = i // cards_per_row
                col = i % cards_per_row
                
                x = start_x + col * (card_width + 20)
                y = start_y + row * (card_height + 20)
                
                # 選択されたペットは高さを調整
                if pet.id == self.selected_pet_id and self.show_details:
                    current_height = card_height + 60
                else:
                    current_height = card_height
                
                # 画面内にある場合のみ描画
                if -current_height <= y <= 720:
                    is_rescued = self.pet_collection.is_pet_rescued(pet.id)
                    rect = self.draw_pet_card(pet, x, y, card_width, current_height, is_rescued)
                    self.pet_rects.append(rect)
                else:
                    self.pet_rects.append(pygame.Rect(0, 0, 0, 0))  # ダミー
            
            # 統計パネル
            self.draw_stats_panel()
            
            # 操作説明
            self.draw_controls()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        print("🎉 インタラクティブペット図鑑終了")
        pygame.quit()

def main():
    """メイン関数"""
    try:
        demo = InteractivePetCollection()
        demo.run()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
