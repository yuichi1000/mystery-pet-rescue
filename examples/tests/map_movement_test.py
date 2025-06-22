#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マップ上でのプレイヤー移動テスト
シンプルなマップ移動確認用
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
    """マップ移動テスト"""
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Map Movement Test")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # マップシステム作成
    map_system = MapSystem(tile_size=32)
    map_system.create_sample_map()
    
    # プレイヤー作成（マップ中央に配置）
    map_width, map_height = map_system.get_map_size()
    player = Player(map_width // 2, map_height // 2)
    
    running = True
    last_time = pygame.time.get_ticks() / 1000.0
    
    print("マップ移動テスト開始")
    print("WASD: 移動")
    print("ESC: 終了")
    
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
        
        # プレイヤー更新（マップシステム付き）
        player.update(dt, None, map_system)
        
        # カメラをプレイヤーに追従
        player_center_x, player_center_y = player.get_center()
        map_system.set_camera_target(player_center_x, player_center_y)
        map_system.update(dt)
        
        # 描画
        screen.fill((40, 40, 60))
        
        # マップ描画
        map_system.render(screen)
        
        # プレイヤー描画（ワールド座標をスクリーン座標に変換）
        player_x, player_y = player.get_position()
        screen_x, screen_y = map_system.world_to_screen(player_x, player_y)
        
        # プレイヤーを一時的にスクリーン座標に移動して描画
        original_x, original_y = player.x, player.y
        player.x, player.y = screen_x, screen_y
        player.render(screen)
        player.x, player.y = original_x, original_y
        
        # 情報表示
        info_text = font.render(f"Player: ({player_x:.0f}, {player_y:.0f})", True, COLOR_WHITE)
        screen.blit(info_text, (10, 10))
        
        movement_text = font.render(f"Moving: {player.is_moving}", True, COLOR_YELLOW)
        screen.blit(movement_text, (10, 50))
        
        instruction_text = font.render("WASD: Move  ESC: Quit", True, COLOR_GREEN)
        screen.blit(instruction_text, (10, SCREEN_HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(TARGET_FPS)
    
    pygame.quit()
    print("マップ移動テスト終了")

if __name__ == "__main__":
    main()
