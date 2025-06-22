#!/usr/bin/env python3
"""
マップ表示テスト（256x256ハイブリッド対応確認）
実際のマップ表示を詳細に確認
"""

import sys
import pygame
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.sprite_manager import SpriteManager, SpriteSize

def main():
    print("🗺️ マップ表示テスト起動中...")
    
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("マップ表示テスト - 256x256ハイブリッド確認")
    clock = pygame.time.Clock()
    
    # スプライトマネージャー初期化
    sprite_manager = SpriteManager()
    sprite_manager.load_tile_sprites()
    
    # フォント
    font_large = pygame.font.Font(None, 36)
    font_medium = pygame.font.Font(None, 24)
    font_small = pygame.font.Font(None, 18)
    
    # 色定義
    colors = {
        'background': (135, 206, 235),
        'text': (255, 255, 255),
        'panel': (0, 0, 0, 150)
    }
    
    # マップデータ
    game_map = [
        "GGGTTGGG",
        "GCCCCCCG",
        "GCDDDCCG",
        "GCRWWRCG",
        "GCRWWRCG",
        "GCDDDCCG",
        "GCCCCCCG",
        "GGGTTGGG"
    ]
    
    # タイルマッピング
    tile_mapping = {
        'G': 'grass',
        'D': 'ground', 
        'C': 'concrete',
        'W': 'water',
        'T': 'tree',
        'R': 'rock'
    }
    
    # 表示設定
    current_size = SpriteSize.MEDIUM
    size_cycle = [SpriteSize.MEDIUM, SpriteSize.LARGE, SpriteSize.ORIGINAL]
    
    # 統計情報
    sprite_info = sprite_manager.get_sprite_info()
    
    print("📊 スプライト読み込み状況:")
    print(f"  キャッシュ済みスプライト: {sprite_info['cached_sprites']}個")
    print(f"  タイルスプライト: {sprite_info['tile_sprites']}個")
    print(f"  利用可能サイズ: {sprite_info['available_sizes']}")
    
    running = True
    show_info = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB:
                    # サイズ切り替え
                    current_index = size_cycle.index(current_size)
                    current_size = size_cycle[(current_index + 1) % len(size_cycle)]
                    print(f"🔄 タイルサイズ切り替え: {current_size.value}")
                elif event.key == pygame.K_i:
                    show_info = not show_info
        
        # 背景
        screen.fill(colors['background'])
        
        # 現在のタイルサイズ
        tile_size = sprite_manager.size_mapping[current_size][0]
        
        # マップ描画
        start_x = (screen.get_width() - len(game_map[0]) * tile_size) // 2
        start_y = (screen.get_height() - len(game_map) * tile_size) // 2
        
        for row_idx, row in enumerate(game_map):
            for col_idx, tile_char in enumerate(row):
                if tile_char in tile_mapping:
                    tile_type = tile_mapping[tile_char]
                    tile_sprite = sprite_manager.get_tile_sprite(tile_type, current_size)
                    
                    if tile_sprite:
                        x = start_x + col_idx * tile_size
                        y = start_y + row_idx * tile_size
                        screen.blit(tile_sprite, (x, y))
        
        if show_info:
            # 情報パネル
            panel_rect = pygame.Rect(10, 10, 500, 200)
            panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
            panel_surface.fill(colors['panel'])
            screen.blit(panel_surface, panel_rect)
            
            # 情報表示
            info_y = 20
            
            # タイトル
            title_text = font_large.render("マップ表示テスト（256x256対応）", True, colors['text'])
            screen.blit(title_text, (20, info_y))
            info_y += 40
            
            # 現在のサイズ
            size_text = font_medium.render(f"現在のサイズ: {current_size.value} ({tile_size}x{tile_size})", True, colors['text'])
            screen.blit(size_text, (20, info_y))
            info_y += 25
            
            # マップ情報
            map_width = len(game_map[0]) * tile_size
            map_height = len(game_map) * tile_size
            map_text = font_small.render(f"マップサイズ: {map_width}x{map_height}", True, colors['text'])
            screen.blit(map_text, (20, info_y))
            info_y += 20
            
            # スプライト情報
            sprite_text = font_small.render(f"読み込み済みタイル: {sprite_info['tile_sprites']}種類", True, colors['text'])
            screen.blit(sprite_text, (20, info_y))
            info_y += 20
            
            # 256x256対応状況
            hybrid_text = font_small.render("256x256画像 → 自動縮小表示", True, (255, 255, 0))
            screen.blit(hybrid_text, (20, info_y))
        
        # 操作説明（右下）
        controls = [
            "TAB: サイズ切り替え",
            "I: 情報表示切り替え", 
            "ESC: 終了"
        ]
        
        for i, control in enumerate(controls):
            text = font_small.render(control, True, colors['text'])
            y_pos = screen.get_height() - 80 + i * 20
            screen.blit(text, (screen.get_width() - 200, y_pos))
        
        # サイズ比較表示（右上）
        comparison_x = screen.get_width() - 300
        comparison_y = 20
        
        comparison_title = font_medium.render("サイズ比較", True, colors['text'])
        screen.blit(comparison_title, (comparison_x, comparison_y))
        comparison_y += 30
        
        # 各サイズの草地タイルを表示
        for size in size_cycle:
            grass_sprite = sprite_manager.get_tile_sprite('grass', size)
            if grass_sprite:
                # 現在選択中のサイズをハイライト
                if size == current_size:
                    highlight_rect = pygame.Rect(comparison_x - 5, comparison_y - 5, 
                                               grass_sprite.get_width() + 10, 
                                               grass_sprite.get_height() + 30)
                    pygame.draw.rect(screen, (255, 255, 0), highlight_rect, 3)
                
                # スプライト表示
                screen.blit(grass_sprite, (comparison_x, comparison_y))
                
                # サイズ情報
                size_info = f"{size.value}\n{grass_sprite.get_width()}x{grass_sprite.get_height()}"
                for j, line in enumerate(size_info.split('\n')):
                    size_label = font_small.render(line, True, colors['text'])
                    screen.blit(size_label, (comparison_x + grass_sprite.get_width() + 10, 
                                           comparison_y + j * 15))
                
                comparison_y += grass_sprite.get_height() + 40
        
        pygame.display.flip()
        clock.tick(60)
    
    print("🎉 マップ表示テスト終了")
    pygame.quit()

if __name__ == "__main__":
    main()
