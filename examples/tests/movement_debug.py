#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移動デバッグテスト
キャラクターが動かない問題を詳細に調査
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
    """移動デバッグテスト"""
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Movement Debug Test")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 20)
    
    # マップシステム作成
    map_system = MapSystem(tile_size=32)
    map_system.create_sample_map()
    
    # プレイヤー作成（安全な位置に配置）
    # マップの中央付近の空いている場所
    safe_x, safe_y = 5 * 32, 5 * 32  # タイル座標(5,5)の位置
    player = Player(safe_x, safe_y)
    
    running = True
    last_time = pygame.time.get_ticks() / 1000.0
    frame_count = 0
    
    print("移動デバッグテスト開始")
    print(f"プレイヤー初期位置: ({safe_x}, {safe_y})")
    print("WASD: 移動")
    print("ESC: 終了")
    
    # 初期衝突チェック
    initial_collision = map_system.check_collision(safe_x, safe_y, player.width, player.height)
    print(f"初期位置での衝突: {initial_collision}")
    
    while running:
        frame_count += 1
        
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
        
        # キー状態チェック
        keys = pygame.key.get_pressed()
        keys_pressed = []
        if keys[pygame.K_w]: keys_pressed.append('W')
        if keys[pygame.K_a]: keys_pressed.append('A')
        if keys[pygame.K_s]: keys_pressed.append('S')
        if keys[pygame.K_d]: keys_pressed.append('D')
        
        # プレイヤー更新前の状態
        old_x, old_y = player.x, player.y
        old_velocity_x, old_velocity_y = player.velocity_x, player.velocity_y
        old_is_moving = player.is_moving
        
        # プレイヤー更新
        player.update(dt, None, map_system)
        
        # プレイヤー更新後の状態
        new_x, new_y = player.x, player.y
        new_velocity_x, new_velocity_y = player.velocity_x, player.velocity_y
        new_is_moving = player.is_moving
        
        # 移動チェック
        position_changed = (old_x != new_x) or (old_y != new_y)
        
        # 衝突チェック
        current_collision = map_system.check_collision(new_x, new_y, player.width, player.height)
        
        # 周囲の衝突チェック
        collision_checks = {}
        for dx, dy, name in [(-32, 0, 'Left'), (32, 0, 'Right'), (0, -32, 'Up'), (0, 32, 'Down')]:
            test_x, test_y = new_x + dx, new_y + dy
            collision_checks[name] = map_system.check_collision(test_x, test_y, player.width, player.height)
        
        # カメラ更新
        player_center_x, player_center_y = player.get_center()
        map_system.set_camera_target(player_center_x, player_center_y)
        map_system.update(dt)
        
        # 描画
        screen.fill((30, 30, 50))
        
        # マップ描画
        map_system.render(screen)
        
        # プレイヤー描画
        screen_x, screen_y = map_system.world_to_screen(new_x, new_y)
        player_rect = pygame.Rect(screen_x, screen_y, player.width, player.height)
        
        # プレイヤーの色（移動状態に応じて）
        if new_is_moving:
            color = (0, 255, 0)  # 緑（移動中）
        else:
            color = (255, 0, 0)  # 赤（停止中）
        
        pygame.draw.rect(screen, color, player_rect)
        pygame.draw.rect(screen, (255, 255, 255), player_rect, 2)
        
        # 中心点
        center_x = screen_x + player.width // 2
        center_y = screen_y + player.height // 2
        pygame.draw.circle(screen, (255, 255, 0), (int(center_x), int(center_y)), 3)
        
        # デバッグ情報表示
        debug_info = [
            f"Frame: {frame_count}",
            f"Keys: {', '.join(keys_pressed) if keys_pressed else 'None'}",
            f"Position: ({new_x:.1f}, {new_y:.1f})",
            f"Old Position: ({old_x:.1f}, {old_y:.1f})",
            f"Position Changed: {position_changed}",
            f"Velocity: ({new_velocity_x:.1f}, {new_velocity_y:.1f})",
            f"Old Velocity: ({old_velocity_x:.1f}, {old_velocity_y:.1f})",
            f"Is Moving: {new_is_moving}",
            f"Was Moving: {old_is_moving}",
            f"Current Speed: {player.current_speed:.1f}",
            f"Base Speed: {player.base_speed:.1f}",
            f"Current Collision: {current_collision}",
            f"Delta Time: {dt:.3f}",
            "",
            "Collision Around:",
            f"  Left: {collision_checks['Left']}",
            f"  Right: {collision_checks['Right']}",
            f"  Up: {collision_checks['Up']}",
            f"  Down: {collision_checks['Down']}",
            "",
            "WASD: Move  ESC: Quit"
        ]
        
        y_offset = 10
        for info in debug_info:
            if info:  # 空行でない場合
                color = (255, 255, 255)
                if "Position Changed: True" in info:
                    color = (0, 255, 0)
                elif "Is Moving: True" in info:
                    color = (0, 255, 255)
                elif "Keys:" in info and keys_pressed:
                    color = (255, 255, 0)
                
                text = font.render(info, True, color)
                screen.blit(text, (10, y_offset))
            y_offset += 18
        
        pygame.display.flip()
        clock.tick(60)
        
        # デバッグ出力（最初の数フレームのみ）
        if frame_count <= 5 or (keys_pressed and frame_count % 60 == 0):
            print(f"Frame {frame_count}: Keys={keys_pressed}, Pos=({new_x:.1f},{new_y:.1f}), "
                  f"Vel=({new_velocity_x:.1f},{new_velocity_y:.1f}), Moving={new_is_moving}, "
                  f"Changed={position_changed}, Collision={current_collision}")
    
    pygame.quit()
    print("移動デバッグテスト終了")

if __name__ == "__main__":
    main()
