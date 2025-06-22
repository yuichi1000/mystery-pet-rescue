#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
最もシンプルなマップ移動テスト
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
    """シンプルマップ移動テスト"""
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simple Map Movement Test")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # マップシステム作成
    map_system = MapSystem(tile_size=32)
    map_system.create_sample_map()
    
    # プレイヤー作成（安全な位置に配置）
    player = Player(200, 200)  # 固定位置
    
    running = True
    last_time = pygame.time.get_ticks() / 1000.0
    
    print("シンプルマップ移動テスト開始")
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
        
        # プレイヤー更新
        old_pos = (player.x, player.y)
        player.update(dt, None, map_system)
        new_pos = (player.x, player.y)
        
        # 移動チェック
        moved = old_pos != new_pos
        
        # カメラ更新
        player_center_x, player_center_y = player.get_center()
        map_system.set_camera_target(player_center_x, player_center_y)
        map_system.update(dt)
        
        # 描画
        screen.fill((50, 50, 70))
        
        # マップ描画
        map_system.render(screen)
        
        # プレイヤー描画
        player_x, player_y = player.get_position()
        screen_x, screen_y = map_system.world_to_screen(player_x, player_y)
        
        # プレイヤー矩形
        player_rect = pygame.Rect(screen_x, screen_y, player.width, player.height)
        pygame.draw.rect(screen, (0, 255, 0), player_rect)
        pygame.draw.rect(screen, (255, 255, 255), player_rect, 2)
        
        # 情報表示
        info_lines = [
            f"Position: ({player_x:.1f}, {player_y:.1f})",
            f"Moving: {player.is_moving}",
            f"Velocity: ({player.velocity_x:.1f}, {player.velocity_y:.1f})",
            f"Speed: {player.current_speed:.1f}",
            f"Moved: {moved}",
            f"FPS: {clock.get_fps():.1f}"
        ]
        
        for i, line in enumerate(info_lines):
            color = (255, 255, 255)
            if "Moving: True" in line or "Moved: True" in line:
                color = (0, 255, 0)
            text = font.render(line, True, color)
            screen.blit(text, (10, 10 + i * 30))
        
        # 操作説明
        instruction = font.render("WASD: Move  ESC: Quit", True, (255, 255, 0))
        screen.blit(instruction, (10, SCREEN_HEIGHT - 40))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("シンプルマップ移動テスト終了")

if __name__ == "__main__":
    main()
