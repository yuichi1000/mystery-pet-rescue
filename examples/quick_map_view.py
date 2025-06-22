#!/usr/bin/env python3
"""
クイックマップビュー
256x256ハイブリッド対応の簡単確認
"""

import sys
import pygame
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.sprite_manager import SpriteManager, SpriteSize

def main():
    print("🗺️ クイックマップビュー起動")
    
    pygame.init()
    screen = pygame.display.set_mode((1000, 700))
    pygame.display.set_caption("クイックマップビュー - 256x256確認")
    clock = pygame.time.Clock()
    
    # スプライトマネージャー
    sprite_manager = SpriteManager()
    sprite_manager.load_tile_sprites()
    
    # フォント
    font = pygame.font.Font(None, 24)
    
    # 簡単なマップ
    mini_map = [
        "GGGWWWGGG",
        "GCCWWWCCG", 
        "GCDDDDDCG",
        "WCDTTTDCW",
        "WCDTRTDCW",
        "WCDTTTDCW",
        "GCDDDDDCG",
        "GCCWWWCCG",
        "GGGWWWGGG"
    ]
    
    tile_map = {
        'G': 'grass', 'W': 'water', 'C': 'concrete',
        'D': 'ground', 'T': 'tree', 'R': 'rock'
    }
    
    current_size = SpriteSize.MEDIUM
    sizes = [SpriteSize.MEDIUM, SpriteSize.LARGE, SpriteSize.ORIGINAL]
    
    print("✅ 初期化完了")
    print("TAB: サイズ切り替え, ESC: 終了")
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_TAB:
                    idx = sizes.index(current_size)
                    current_size = sizes[(idx + 1) % len(sizes)]
                    print(f"🔄 サイズ: {current_size.value}")
        
        screen.fill((135, 206, 235))  # 空色
        
        # マップ描画
        tile_size = sprite_manager.size_mapping[current_size][0]
        start_x = (screen.get_width() - len(mini_map[0]) * tile_size) // 2
        start_y = (screen.get_height() - len(mini_map) * tile_size) // 2
        
        for row_idx, row in enumerate(mini_map):
            for col_idx, char in enumerate(row):
                if char in tile_map:
                    tile_sprite = sprite_manager.get_tile_sprite(tile_map[char], current_size)
                    if tile_sprite:
                        x = start_x + col_idx * tile_size
                        y = start_y + row_idx * tile_size
                        screen.blit(tile_sprite, (x, y))
        
        # 情報表示
        info_texts = [
            f"現在のサイズ: {current_size.value} ({tile_size}x{tile_size})",
            f"マップサイズ: {len(mini_map[0]) * tile_size}x{len(mini_map) * tile_size}",
            "256x256画像 → 自動縮小表示中",
            "",
            "TAB: サイズ切り替え",
            "ESC: 終了"
        ]
        
        for i, text in enumerate(info_texts):
            if text:
                color = (255, 255, 0) if "256x256" in text else (255, 255, 255)
                text_surface = font.render(text, True, color)
                screen.blit(text_surface, (20, 20 + i * 25))
        
        pygame.display.flip()
        clock.tick(60)
    
    print("🎉 クイックマップビュー終了")
    pygame.quit()

if __name__ == "__main__":
    main()
