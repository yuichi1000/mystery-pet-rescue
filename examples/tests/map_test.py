#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マップシステム基本テスト
マップ読み込みと基本機能をテスト
"""

import pygame
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.systems.map_system import MapSystem
from config.constants import *

def test_map_system():
    """マップシステムの基本テスト"""
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Map System Test")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # マップシステム作成
    map_system = MapSystem(tile_size=32)
    
    # サンプルマップ作成
    map_system.create_sample_map()
    
    # テスト用プレイヤー位置
    player_x, player_y = 100.0, 100.0
    player_size = 32
    
    running = True
    test_results = []
    
    print("マップシステム基本テスト開始")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # テスト実行
                    test_results = run_tests(map_system)
        
        # 描画
        screen.fill((40, 40, 60))
        
        # マップ描画
        map_system.render(screen)
        
        # テスト用プレイヤー描画
        screen_x, screen_y = map_system.world_to_screen(player_x, player_y)
        player_rect = pygame.Rect(screen_x, screen_y, player_size, player_size)
        pygame.draw.rect(screen, (0, 255, 0), player_rect)
        pygame.draw.rect(screen, (255, 255, 255), player_rect, 2)
        
        # テスト結果表示
        title_text = font.render("Map System Test", True, (255, 255, 255))
        screen.blit(title_text, (10, 10))
        
        instruction_text = font.render("SPACE: Run Tests  ESC: Quit", True, (255, 255, 0))
        screen.blit(instruction_text, (10, 50))
        
        # テスト結果
        if test_results:
            y_offset = 90
            for result in test_results:
                color = (0, 255, 0) if result.startswith("✓") else (255, 0, 0)
                result_text = font.render(result, True, color)
                screen.blit(result_text, (10, y_offset))
                y_offset += 30
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("マップシステム基本テスト終了")

def run_tests(map_system):
    """テストを実行"""
    results = []
    
    # テスト1: マップサイズ取得
    try:
        width, height = map_system.get_map_size()
        if width > 0 and height > 0:
            results.append("✓ Map size test passed")
        else:
            results.append("✗ Map size test failed")
    except Exception as e:
        results.append(f"✗ Map size test error: {e}")
    
    # テスト2: タイルサイズ取得
    try:
        tile_size = map_system.get_tile_size()
        if tile_size == 32:
            results.append("✓ Tile size test passed")
        else:
            results.append("✗ Tile size test failed")
    except Exception as e:
        results.append(f"✗ Tile size test error: {e}")
    
    # テスト3: 衝突判定テスト
    try:
        # 壁との衝突（境界）
        collision1 = map_system.check_collision(0, 0, 32, 32)
        # 空きスペース
        collision2 = map_system.check_collision(100, 100, 32, 32)
        
        if collision1 and not collision2:
            results.append("✓ Collision detection test passed")
        else:
            results.append("✗ Collision detection test failed")
    except Exception as e:
        results.append(f"✗ Collision test error: {e}")
    
    # テスト4: カメラシステム
    try:
        map_system.set_camera_target(200, 200)
        map_system.update(0.016)  # 1フレーム分
        results.append("✓ Camera system test passed")
    except Exception as e:
        results.append(f"✗ Camera test error: {e}")
    
    # テスト5: 座標変換
    try:
        world_x, world_y = 100, 100
        screen_x, screen_y = map_system.world_to_screen(world_x, world_y)
        back_x, back_y = map_system.screen_to_world(screen_x, screen_y)
        
        if abs(back_x - world_x) < 1 and abs(back_y - world_y) < 1:
            results.append("✓ Coordinate conversion test passed")
        else:
            results.append("✗ Coordinate conversion test failed")
    except Exception as e:
        results.append(f"✗ Coordinate test error: {e}")
    
    return results

if __name__ == "__main__":
    test_map_system()
