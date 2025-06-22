#!/usr/bin/env python3
"""
レイヤードマップデモ
ベースタイル + オブジェクト方式のマップ表示
"""

import sys
import pygame
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.sprite_manager import SpriteManager, SpriteSize
from src.systems.map_object_manager import MapObjectManager, ObjectType

def main():
    print("🗺️ レイヤードマップデモ起動中...")
    
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("レイヤードマップデモ - ベース+オブジェクト方式")
    clock = pygame.time.Clock()
    
    # システム初期化
    sprite_manager = SpriteManager()
    sprite_manager.load_tile_sprites()
    
    object_manager = MapObjectManager(sprite_manager)
    
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
    
    # ベースマップ（地形のみ）
    base_map = [
        "GGGGGGGGGGG",
        "GGGCCCCCGGG",
        "GGGCDDDDCGG",
        "GGGCDDDGCGG",
        "GGGCDDDGCGG",
        "GGGCDDDGCGG",
        "GGGCDDDDCGG",
        "GGGCCCCCGGG",
        "GGGGGGGGGGG"
    ]
    
    # ベースタイルマッピング（移動可能な地形のみ）
    base_tile_mapping = {
        'G': 'grass',      # 草地
        'D': 'ground',     # 地面
        'C': 'concrete'    # コンクリート
    }
    
    # 表示設定
    current_size = SpriteSize.MEDIUM
    size_cycle = [SpriteSize.MEDIUM, SpriteSize.LARGE, SpriteSize.ORIGINAL]
    
    # カメラ設定
    camera_x = 0
    camera_y = 0
    camera_speed = 200
    
    # サンプルオブジェクト作成
    tile_size = sprite_manager.size_mapping[current_size][0]
    object_manager.create_sample_objects(tile_size)
    
    print("✅ レイヤードマップシステム初期化完了")
    print("🎯 新しい構造:")
    print("  - ベースタイル: 草地・地面・コンクリート（移動可能）")
    print("  - オブジェクト: 岩・水・木（障害物として配置）")
    
    running = True
    show_info = True
    
    while running:
        time_delta = clock.tick(60) / 1000.0
        
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
                    
                    # タイルサイズ更新
                    old_tile_size = tile_size
                    tile_size = sprite_manager.size_mapping[current_size][0]
                    
                    # オブジェクト位置をスケール調整
                    scale_factor = tile_size / old_tile_size
                    for obj in object_manager.objects:
                        obj.x = int(obj.x * scale_factor)
                        obj.y = int(obj.y * scale_factor)
                        obj.width = tile_size
                        obj.height = tile_size
                        obj.sprite_size = current_size
                    
                    print(f"🔄 サイズ切り替え: {current_size.value} ({tile_size}x{tile_size})")
                elif event.key == pygame.K_i:
                    show_info = not show_info
        
        # カメラ移動
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            camera_x = max(0, camera_x - camera_speed * time_delta)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            camera_x = min(len(base_map[0]) * tile_size - screen.get_width(), 
                          camera_x + camera_speed * time_delta)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            camera_y = max(0, camera_y - camera_speed * time_delta)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            camera_y = min(len(base_map) * tile_size - screen.get_height(), 
                          camera_y + camera_speed * time_delta)
        
        # 背景
        screen.fill(colors['background'])
        
        # ベースタイル描画（レイヤー1）
        for row_idx, row in enumerate(base_map):
            for col_idx, tile_char in enumerate(row):
                if tile_char in base_tile_mapping:
                    tile_type = base_tile_mapping[tile_char]
                    tile_sprite = sprite_manager.get_tile_sprite(tile_type, current_size)
                    
                    if tile_sprite:
                        x = col_idx * tile_size - camera_x
                        y = row_idx * tile_size - camera_y
                        
                        # 画面内のタイルのみ描画
                        if (-tile_size <= x <= screen.get_width() and 
                            -tile_size <= y <= screen.get_height()):
                            screen.blit(tile_sprite, (x, y))
        
        # オブジェクト描画（レイヤー2）
        object_manager.draw_objects(screen, camera_x, camera_y)
        
        if show_info:
            # 情報パネル
            panel_rect = pygame.Rect(10, 10, 450, 180)
            panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
            panel_surface.fill(colors['panel'])
            screen.blit(panel_surface, panel_rect)
            
            # 情報表示
            info_y = 20
            
            # タイトル
            title_text = font_large.render("レイヤードマップデモ", True, colors['text'])
            screen.blit(title_text, (20, info_y))
            info_y += 35
            
            # 現在のサイズ
            size_text = font_medium.render(f"サイズ: {current_size.value} ({tile_size}x{tile_size})", True, colors['text'])
            screen.blit(size_text, (20, info_y))
            info_y += 25
            
            # レイヤー情報
            layer_text = font_small.render("レイヤー1: ベースタイル（草地・地面・コンクリート）", True, colors['text'])
            screen.blit(layer_text, (20, info_y))
            info_y += 20
            
            layer2_text = font_small.render("レイヤー2: オブジェクト（岩・水・木）", True, colors['text'])
            screen.blit(layer2_text, (20, info_y))
            info_y += 20
            
            # オブジェクト情報
            obj_info = object_manager.get_objects_info()
            obj_text = font_small.render(f"オブジェクト: {obj_info['total_objects']}個 (障害物: {obj_info['obstacle_count']}個)", True, colors['text'])
            screen.blit(obj_text, (20, info_y))
            info_y += 20
            
            # 256x256対応状況
            hybrid_text = font_small.render("256x256画像 → 自動縮小表示", True, (255, 255, 0))
            screen.blit(hybrid_text, (20, info_y))
        
        # 操作説明
        controls = [
            "WASD: カメラ移動",
            "TAB: サイズ切り替え",
            "I: 情報表示切り替え",
            "ESC: 終了"
        ]
        
        for i, control in enumerate(controls):
            text = font_small.render(control, True, colors['text'])
            y_pos = screen.get_height() - 100 + i * 20
            screen.blit(text, (20, y_pos))
        
        # レイヤー説明（右側）
        layer_info = [
            "🗺️ レイヤー構造:",
            "1. ベースタイル（移動可能）",
            "   - 草地 (G)",
            "   - 地面 (D)", 
            "   - コンクリート (C)",
            "",
            "2. オブジェクト（障害物）",
            "   - 岩 🪨",
            "   - 水 💧",
            "   - 木 🌳"
        ]
        
        for i, info in enumerate(layer_info):
            color = (255, 255, 0) if info.startswith("🗺️") else colors['text']
            text = font_small.render(info, True, color)
            screen.blit(text, (screen.get_width() - 250, 20 + i * 18))
        
        pygame.display.flip()
    
    print("🎉 レイヤードマップデモ終了")
    pygame.quit()

if __name__ == "__main__":
    main()
