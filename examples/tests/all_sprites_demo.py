#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
全スプライト表示デモ
全てのタイルスプライトを表示・確認
"""

import pygame
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.systems.map_system import MapSystem
from src.entities.player import Player
from config.constants import *

def main():
    """全スプライト表示デモ"""
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("All Sprites Demo - Complete Tileset")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    # マップシステム作成（全スプライト付き）
    map_system = MapSystem(tile_size=32)
    map_system.create_sample_map()
    
    # プレイヤー作成（安全な位置に配置）
    safe_x, safe_y = 3 * 32, 3 * 32
    player = Player(safe_x, safe_y)
    
    running = True
    last_time = pygame.time.get_ticks() / 1000.0
    show_sprite_info = True
    
    print("全スプライト表示デモ開始")
    print("全てのタイルが実際のスプライト画像で表示されます")
    print("WASD: 移動")
    print("S: スプライト情報切り替え")
    print("ESC: 終了")
    
    # スプライト読み込み状況確認
    sprite_status = {}
    tile_names = {
        1: "Ground (地面)",
        2: "Stone Wall (石壁)",
        3: "Water (水面)",
        4: "Grass (草地)",
        5: "Tree (木)",
        6: "Rock (岩)"
    }
    
    for tile_id, name in tile_names.items():
        loaded = hasattr(map_system.tileset, 'individual_sprites') and tile_id in map_system.tileset.individual_sprites
        sprite_status[tile_id] = loaded
        print(f"{name}: {'読み込み成功' if loaded else '読み込み失敗'}")
    
    total_loaded = sum(sprite_status.values())
    print(f"総スプライト読み込み: {total_loaded}/{len(tile_names)}個")
    
    while running:
        # デルタタイム計算
        current_time = pygame.time.get_ticks() / 1000.0
        dt = current_time - last_time
        last_time = current_time
        
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_s:
                    show_sprite_info = not show_sprite_info
        
        # プレイヤー更新
        player.update(dt, None, map_system)
        
        # カメラ更新
        player_center_x, player_center_y = player.get_center()
        map_system.set_camera_target(player_center_x, player_center_y)
        map_system.update(dt)
        
        # 描画
        screen.fill((20, 20, 30))
        
        # マップ描画
        map_system.render(screen)
        
        # プレイヤー描画
        player_x, player_y = player.get_position()
        screen_x, screen_y = map_system.world_to_screen(player_x, player_y)
        
        # プレイヤーを一時的にスクリーン座標に移動して描画
        original_x, original_y = player.x, player.y
        player.x, player.y = screen_x, screen_y
        player.render(screen)
        player.x, player.y = original_x, original_y
        
        # スプライト情報表示
        if show_sprite_info:
            info_lines = [
                "=== All Sprites Demo ===",
                f"Total Sprites Loaded: {total_loaded}/{len(tile_names)}",
                f"Player Position: ({player_x:.1f}, {player_y:.1f})",
                "",
                "Sprite Status:"
            ]
            
            # 各スプライトの状態
            for tile_id, name in tile_names.items():
                status = "✅ LOADED" if sprite_status[tile_id] else "❌ MISSING"
                info_lines.append(f"  {name}: {status}")
            
            info_lines.extend([
                "",
                "Map Legend:",
                "• Green areas: Grass tiles (background)",
                "• Gray areas: Stone wall tiles (collision)",
                "• Blue areas: Water tiles (collision)",
                "• Dark green: Tree tiles (collision)",
                "• Dark gray: Rock tiles (collision)",
                "• Brown paths: Ground tiles (decoration)",
                "",
                "Controls:",
                "WASD: Move Player",
                "S: Toggle this info",
                "ESC: Quit"
            ])
            
            y_offset = 10
            for line in info_lines:
                if line:  # 空行でない場合
                    color = (255, 255, 255)
                    if "✅ LOADED" in line:
                        color = (0, 255, 0)  # 緑色で成功を強調
                    elif "❌ MISSING" in line:
                        color = (255, 0, 0)  # 赤色で失敗を強調
                    elif line.startswith("•"):
                        color = (255, 255, 0)  # 黄色で説明を強調
                    elif "Total Sprites Loaded:" in line:
                        if total_loaded == len(tile_names):
                            color = (0, 255, 0)  # 全て成功
                        else:
                            color = (255, 255, 0)  # 一部成功
                    
                    text = font.render(line, True, color)
                    screen.blit(text, (10, y_offset))
                y_offset += 18
        
        # 右下に簡単な情報
        fps_text = font.render(f"FPS: {clock.get_fps():.1f}", True, (255, 255, 255))
        screen.blit(fps_text, (SCREEN_WIDTH - 100, SCREEN_HEIGHT - 30))
        
        sprite_status_text = f"Sprites: {total_loaded}/{len(tile_names)}"
        status_color = (0, 255, 0) if total_loaded == len(tile_names) else (255, 255, 0)
        status_text = font.render(sprite_status_text, True, status_color)
        screen.blit(status_text, (SCREEN_WIDTH - 150, SCREEN_HEIGHT - 60))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("全スプライト表示デモ終了")

if __name__ == "__main__":
    main()
