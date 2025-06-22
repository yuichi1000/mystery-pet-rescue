#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
デバッグ用マップデモ
キャラクター移動の問題を詳細に調査
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
    """デバッグ用マップデモ"""
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Debug Map Demo - Character Movement Test")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 24)
    
    # マップシステム作成
    map_system = MapSystem(tile_size=32)
    map_system.create_sample_map()
    
    # プレイヤー作成（マップ中央に配置）
    map_width, map_height = map_system.get_map_size()
    player = Player(map_width // 2, map_height // 2)
    
    running = True
    last_time = pygame.time.get_ticks() / 1000.0
    
    # デバッグ情報
    debug_info = {
        'keys_pressed': [],
        'player_moving': False,
        'player_velocity': (0, 0),
        'player_position': (0, 0),
        'collision_detected': False
    }
    
    print("デバッグ用マップデモ開始")
    print("WASD: 移動")
    print("ESC: 終了")
    print("詳細なデバッグ情報を画面に表示します")
    
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
        
        # キー状態の詳細チェック
        keys = pygame.key.get_pressed()
        debug_info['keys_pressed'] = []
        if keys[pygame.K_w]: debug_info['keys_pressed'].append('W')
        if keys[pygame.K_a]: debug_info['keys_pressed'].append('A')
        if keys[pygame.K_s]: debug_info['keys_pressed'].append('S')
        if keys[pygame.K_d]: debug_info['keys_pressed'].append('D')
        if keys[pygame.K_UP]: debug_info['keys_pressed'].append('↑')
        if keys[pygame.K_DOWN]: debug_info['keys_pressed'].append('↓')
        if keys[pygame.K_LEFT]: debug_info['keys_pressed'].append('←')
        if keys[pygame.K_RIGHT]: debug_info['keys_pressed'].append('→')
        
        # プレイヤー更新前の状態記録
        old_x, old_y = player.get_position()
        
        # プレイヤー更新（マップシステム付き）
        player.update(dt, None, map_system)
        
        # プレイヤー更新後の状態記録
        new_x, new_y = player.get_position()
        debug_info['player_moving'] = player.is_moving
        debug_info['player_velocity'] = (player.velocity_x, player.velocity_y)
        debug_info['player_position'] = (new_x, new_y)
        debug_info['collision_detected'] = map_system.check_collision(new_x, new_y, player.width, player.height)
        
        # 移動があったかチェック
        moved = abs(new_x - old_x) > 0.1 or abs(new_y - old_y) > 0.1
        
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
        
        # プレイヤーの周りに円を描画（可視化）
        pygame.draw.circle(screen, (255, 255, 0), (int(screen_x + player.width//2), int(screen_y + player.height//2)), player.width//2 + 5, 2)
        
        # デバッグ情報表示
        y_offset = 10
        debug_texts = [
            f"Keys Pressed: {', '.join(debug_info['keys_pressed']) if debug_info['keys_pressed'] else 'None'}",
            f"Player Moving: {debug_info['player_moving']}",
            f"Player Velocity: ({debug_info['player_velocity'][0]:.1f}, {debug_info['player_velocity'][1]:.1f})",
            f"Player Position: ({debug_info['player_position'][0]:.1f}, {debug_info['player_position'][1]:.1f})",
            f"Collision Detected: {debug_info['collision_detected']}",
            f"Actually Moved: {moved}",
            f"Player Animation State: {player.animation_state.name}",
            f"Player Speed: {player.current_speed:.1f}",
            f"Delta Time: {dt:.3f}",
            f"FPS: {clock.get_fps():.1f}",
            "",
            "Controls:",
            "WASD / Arrow Keys: Move",
            "ESC: Quit"
        ]
        
        for text in debug_texts:
            if text:  # 空行でない場合
                color = (255, 255, 255)
                if "Keys Pressed:" in text and debug_info['keys_pressed']:
                    color = (0, 255, 0)  # 緑色でキー入力を強調
                elif "Player Moving: True" in text:
                    color = (0, 255, 0)  # 緑色で移動状態を強調
                elif "Actually Moved: True" in text:
                    color = (0, 255, 255)  # シアンで実際の移動を強調
                
                text_surface = font.render(text, True, color)
                screen.blit(text_surface, (10, y_offset))
            y_offset += 20
        
        pygame.display.flip()
        clock.tick(TARGET_FPS)
    
    pygame.quit()
    print("デバッグ用マップデモ終了")

if __name__ == "__main__":
    main()
