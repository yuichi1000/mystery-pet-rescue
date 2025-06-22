#!/usr/bin/env python3
"""
ゲームマップデモ（256x256ハイブリッド対応）
実際のアセットを使用したゲームマップの表示
"""

import sys
import pygame
import os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.sprite_manager import SpriteManager, SpriteSize

def main():
    print("🗺️ ゲームマップデモ起動中...")
    
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("ゲームマップデモ - 256x256ハイブリッド対応")
    clock = pygame.time.Clock()
    
    # スプライトマネージャー初期化
    sprite_manager = SpriteManager()
    
    # フォント
    font_large = pygame.font.Font(None, 36)
    font_medium = pygame.font.Font(None, 24)
    font_small = pygame.font.Font(None, 18)
    
    # 色定義
    colors = {
        'background': (135, 206, 235),  # スカイブルー
        'text': (255, 255, 255),
        'shadow': (0, 0, 0, 128),
        'panel': (0, 0, 0, 100)
    }
    
    # タイルスプライト読み込み
    sprite_manager.load_tile_sprites()
    
    # ゲームマップデータ（ベースタイル + オブジェクト方式）
    base_map = [
        "GGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGG",
        "GGGCCCCCCCCCCCCCGGG",
        "GGGCDDDDDDDDDDCCGGG",
        "GGGCDGGGGGGGGGDCGGG",
        "GGGCDGGGGGGGGGDCGGG",
        "GGGCDGGGGGGGGGDCGGG",
        "GGGCDGGGGGGGGGDCGGG",
        "GGGCDGGGGGGGGGDCGGG",
        "GGGCDGGGGGGGGGDCGGG",
        "GGGCDGGGGGGGGGDCGGG",
        "GGGCDDDDDDDDDDCCGGG",
        "GGGCCCCCCCCCCCCCGGG",
        "GGGGGGGGGGGGGGGGGGG",
        "GGGGGGGGGGGGGGGGGGG"
    ]
    
    # オブジェクト配置マップ（障害物）
    object_map = [
        "                   ",
        " TT             TT ",
        "                   ",
        "                   ",
        "   RRRRRRRRR       ",
        "   RWWWWWWWR       ",
        "   RWWWWWWWR       ",
        "   RWWWWWWWR       ",
        "   RWWWWWWWR       ",
        "   RRRRRRRRR       ",
        "                   ",
        "                   ",
        "                   ",
        " TT             TT ",
        "                   "
    ]
    
    # ベースタイルマッピング（移動可能）
    base_tile_mapping = {
        'G': 'grass',
        'D': 'ground',
        'C': 'concrete'
    }
    
    # オブジェクトマッピング（障害物）
    object_mapping = {
        'T': 'tree',
        'R': 'rock', 
        'W': 'water'
    }
    
    # 表示設定
    current_size = SpriteSize.MEDIUM  # デフォルト64x64
    size_cycle = [SpriteSize.MEDIUM, SpriteSize.LARGE, SpriteSize.ORIGINAL]
    
    # タイルサイズ計算
    tile_size = sprite_manager.size_mapping[current_size][0]
    map_width = len(base_map[0]) * tile_size
    map_height = len(base_map) * tile_size
    
    # カメラ位置
    camera_x = 0
    camera_y = 0
    camera_speed = 200
    
    print(f"🗺️ マップサイズ: {map_width}x{map_height}")
    print("✅ 256x256ハイブリッド対応初期化完了")
    
    running = True
    
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
                    tile_size = sprite_manager.size_mapping[current_size][0]
                    map_width = len(base_map[0]) * tile_size
                    map_height = len(base_map) * tile_size
                    print(f"🔄 タイルサイズ切り替え: {current_size.value} ({tile_size}x{tile_size})")
        
        # カメラ移動
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            camera_x = max(0, camera_x - camera_speed * time_delta)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            camera_x = min(map_width - screen.get_width(), camera_x + camera_speed * time_delta)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            camera_y = max(0, camera_y - camera_speed * time_delta)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            camera_y = min(map_height - screen.get_height(), camera_y + camera_speed * time_delta)
        
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
                        if -tile_size <= x <= screen.get_width() and -tile_size <= y <= screen.get_height():
                            screen.blit(tile_sprite, (x, y))
        
        # オブジェクト描画（レイヤー2）
        for row_idx, row in enumerate(object_map):
            for col_idx, obj_char in enumerate(row):
                if obj_char in object_mapping:
                    obj_type = object_mapping[obj_char]
                    obj_sprite = sprite_manager.get_tile_sprite(obj_type, current_size)
                    
                    if obj_sprite:
                        x = col_idx * tile_size - camera_x
                        y = row_idx * tile_size - camera_y
                        
                        # 画面内のオブジェクトのみ描画
                        if -tile_size <= x <= screen.get_width() and -tile_size <= y <= screen.get_height():
                            screen.blit(obj_sprite, (x, y))
        
        # UI表示
        # 情報パネル背景
        panel_rect = pygame.Rect(10, 10, 400, 120)
        panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        panel_surface.fill(colors['panel'])
        screen.blit(panel_surface, panel_rect)
        
        # タイトル
        title_text = font_large.render("ゲームマップデモ（256x256対応）", True, colors['text'])
        screen.blit(title_text, (20, 20))
        
        # 現在のサイズ情報
        size_info = f"タイルサイズ: {current_size.value} ({tile_size}x{tile_size})"
        size_text = font_medium.render(size_info, True, colors['text'])
        screen.blit(size_text, (20, 50))
        
        # 256x256対応状況
        status_text = "256x256画像 → 自動縮小表示中"
        status_surface = font_small.render(status_text, True, colors['text'])
        screen.blit(status_surface, (20, 75))
        
        # 操作説明
        controls = [
            "WASD / 矢印キー: カメラ移動",
            "TAB: タイルサイズ切り替え",
            "ESC: 終了"
        ]
        
        for i, control in enumerate(controls):
            text = font_small.render(control, True, colors['text'])
            y_pos = screen.get_height() - 80 + i * 20
            screen.blit(text, (20, y_pos))
        
        # カメラ・サイズ情報
        info_panel = pygame.Rect(screen.get_width() - 250, 10, 240, 100)
        info_surface = pygame.Surface((info_panel.width, info_panel.height), pygame.SRCALPHA)
        info_surface.fill(colors['panel'])
        screen.blit(info_surface, info_panel)
        
        camera_info = f"カメラ: ({int(camera_x)}, {int(camera_y)})"
        camera_text = font_small.render(camera_info, True, colors['text'])
        screen.blit(camera_text, (screen.get_width() - 240, 20))
        
        map_info = f"マップ: {map_width}x{map_height}"
        map_text = font_small.render(map_info, True, colors['text'])
        screen.blit(map_text, (screen.get_width() - 240, 40))
        
        # 利用可能サイズ表示
        sizes_info = f"サイズ: {' / '.join([s.value for s in size_cycle])}"
        sizes_text = font_small.render(sizes_info, True, colors['text'])
        screen.blit(sizes_text, (screen.get_width() - 240, 60))
        
        # 現在選択中のサイズをハイライト
        current_info = f"現在: {current_size.value}"
        current_text = font_small.render(current_info, True, (255, 255, 0))
        screen.blit(current_text, (screen.get_width() - 240, 80))
        
        pygame.display.flip()
    
    print("🎉 ゲームマップデモ終了")
    pygame.quit()

if __name__ == "__main__":
    main()
