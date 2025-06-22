#!/usr/bin/env python3
"""
ペット図鑑システムのシンプルデモ
Pygameのみを使用してペット図鑑を表示
"""

import sys
import os
import pygame
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.pet_collection import PetCollection

class SimplePetCollectionDemo:
    """シンプルなペット図鑑デモ"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("ミステリー・ペット・レスキュー - ペット図鑑")
        self.clock = pygame.time.Clock()
        
        # フォント
        self.title_font = pygame.font.Font(None, 48)
        self.header_font = pygame.font.Font(None, 36)
        self.text_font = pygame.font.Font(None, 24)
        self.small_font = pygame.font.Font(None, 20)
        
        # 色定義
        self.colors = {
            'background': (240, 248, 255),  # アリスブルー
            'white': (255, 255, 255),
            'black': (50, 50, 50),
            'gray': (128, 128, 128),
            'light_gray': (200, 200, 200),
            'green': (76, 175, 80),
            'red': (244, 67, 54),
            'blue': (33, 150, 243),
            'orange': (255, 152, 0),
            'purple': (156, 39, 176)
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
        
        # テスト用にいくつかのペットを救助済みにする
        self.pet_collection.rescue_pet("dog_001", "住宅街の公園", 120)
        self.pet_collection.rescue_pet("cat_001", "路地裏", 180)
        self.pet_collection.rescue_pet("rabbit_001", "茂みの中", 240)
        
        # 表示状態
        self.scroll_y = 0
        self.selected_pet_id = None
        
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
        pygame.draw.rect(self.screen, card_color, (x, y, width, height))
        pygame.draw.rect(self.screen, self.colors['gray'], (x, y, width, height), 2)
        
        # レア度インジケーター
        rarity_color = self.rarity_colors.get(pet.rarity, self.colors['gray'])
        pygame.draw.rect(self.screen, rarity_color, (x, y, width, 5))
        
        # ペット情報
        text_y = y + 15
        
        # 名前
        name_color = self.colors['black'] if is_rescued else self.colors['gray']
        text_y += self.draw_text(pet.name, self.text_font, name_color, x + 10, text_y)
        
        # 種類・品種
        species_text = f"{pet.species} - {pet.breed}"
        text_y += self.draw_text(species_text, self.small_font, self.colors['gray'], x + 10, text_y)
        
        # 救助状態
        status_text = "✅ 救助済み" if is_rescued else "❌ 未救助"
        status_color = self.colors['green'] if is_rescued else self.colors['red']
        text_y += self.draw_text(status_text, self.small_font, status_color, x + 10, text_y)
        
        # レア度
        rarity_info = self.pet_collection.get_rarity_info(pet.rarity)
        rarity_text = f"レア度: {rarity_info['name']}"
        text_y += self.draw_text(rarity_text, self.small_font, rarity_color, x + 10, text_y)
        
        # 難易度
        difficulty_text = f"難易度: {'★' * pet.rescue_difficulty}"
        self.draw_text(difficulty_text, self.small_font, self.colors['orange'], x + 10, text_y)
        
        return pygame.Rect(x, y, width, height)
    
    def draw_stats_panel(self):
        """統計パネルを描画"""
        stats = self.pet_collection.get_collection_stats()
        
        # パネル背景
        panel_rect = pygame.Rect(900, 100, 350, 200)
        pygame.draw.rect(self.screen, self.colors['white'], panel_rect)
        pygame.draw.rect(self.screen, self.colors['gray'], panel_rect, 2)
        
        # タイトル
        y = 120
        y += self.draw_text("📊 図鑑統計", self.header_font, self.colors['black'], 920, y)
        y += 10
        
        # 基本統計
        completion_text = f"完成率: {stats['completion_rate']:.1f}%"
        y += self.draw_text(completion_text, self.text_font, self.colors['black'], 920, y)
        
        rescued_text = f"救助済み: {stats['rescued_pets']}/{stats['total_pets']}匹"
        y += self.draw_text(rescued_text, self.text_font, self.colors['black'], 920, y)
        y += 10
        
        # レア度別統計
        y += self.draw_text("レア度別:", self.small_font, self.colors['gray'], 920, y)
        for rarity, data in stats['rarity_stats'].items():
            if data['total'] > 0:
                rarity_info = self.pet_collection.get_rarity_info(rarity)
                rarity_color = self.rarity_colors.get(rarity, self.colors['gray'])
                rarity_text = f"  {rarity_info['name']}: {data['rescued']}/{data['total']}"
                y += self.draw_text(rarity_text, self.small_font, rarity_color, 920, y)
    
    def run(self):
        """メインループ"""
        print("🐾 ペット図鑑システム起動")
        print("\n🎮 操作方法:")
        print("  - マウスホイール: スクロール")
        print("  - ESC: 終了")
        
        running = True
        
        while running:
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                elif event.type == pygame.MOUSEWHEEL:
                    self.scroll_y += event.y * 30
                    self.scroll_y = max(0, min(self.scroll_y, 500))  # スクロール制限
            
            # 描画
            self.screen.fill(self.colors['background'])
            
            # タイトル
            self.draw_text("🐾 ペット図鑑", self.title_font, self.colors['black'], 640, 50, center=True)
            
            # ペット一覧
            all_pets = self.pet_collection.get_all_pets()
            card_width = 400
            card_height = 120
            cards_per_row = 2
            start_x = 50
            start_y = 100 - self.scroll_y
            
            for i, pet in enumerate(all_pets):
                row = i // cards_per_row
                col = i % cards_per_row
                
                x = start_x + col * (card_width + 20)
                y = start_y + row * (card_height + 20)
                
                # 画面内にある場合のみ描画
                if -card_height <= y <= 720:
                    is_rescued = self.pet_collection.is_pet_rescued(pet.id)
                    self.draw_pet_card(pet, x, y, card_width, card_height, is_rescued)
            
            # 統計パネル
            self.draw_stats_panel()
            
            # 操作説明
            help_y = 680
            self.draw_text("ESC: 終了 | マウスホイール: スクロール", self.small_font, self.colors['gray'], 10, help_y)
            
            pygame.display.flip()
            self.clock.tick(60)
        
        print("🎉 ペット図鑑システム終了")
        pygame.quit()

def main():
    """メイン関数"""
    try:
        demo = SimplePetCollectionDemo()
        demo.run()
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
