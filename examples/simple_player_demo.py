#!/usr/bin/env python3
"""
シンプルプレイヤーデモ
プレイヤーの移動とスプライト表示の確認
"""

import sys
import pygame
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.entities.player import Player
from src.utils.font_manager import get_font_manager

def main():
    print("🎮 シンプルプレイヤーデモ起動中...")
    
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("シンプルプレイヤーデモ - 移動とスプライト確認")
    clock = pygame.time.Clock()
    
    # プレイヤー作成
    player = Player(400, 300)
    font_manager = get_font_manager()
    
    print("✅ プレイヤー初期化完了")
    print("🎯 操作方法:")
    print("  WASD または 矢印キー: 移動")
    print("  Shift: 走行")
    print("  ESC: 終了")
    
    running = True
    
    while running:
        time_delta = clock.tick(60) / 1000.0
        
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
        
        # キー入力取得（修正版）
        keys = pygame.key.get_pressed()
        keys_pressed = set()
        
        # 移動キーをチェック
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            keys_pressed.add(pygame.K_LEFT)
            keys_pressed.add(pygame.K_a)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            keys_pressed.add(pygame.K_RIGHT)
            keys_pressed.add(pygame.K_d)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            keys_pressed.add(pygame.K_UP)
            keys_pressed.add(pygame.K_w)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            keys_pressed.add(pygame.K_DOWN)
            keys_pressed.add(pygame.K_s)
        if keys[pygame.K_LSHIFT]:
            keys_pressed.add(pygame.K_LSHIFT)
        
        # プレイヤー更新
        player.update(time_delta, keys_pressed)
        
        # 描画
        screen.fill((50, 150, 50))  # 緑の背景
        
        # グリッド描画（参考用）
        for x in range(0, screen.get_width(), 64):
            pygame.draw.line(screen, (100, 200, 100), (x, 0), (x, screen.get_height()))
        for y in range(0, screen.get_height(), 64):
            pygame.draw.line(screen, (100, 200, 100), (0, y), (screen.get_width(), y))
        
        # プレイヤー描画
        player.draw(screen)
        
        # 情報表示
        player_pos = player.get_position()
        player_stats = player.get_stats()
        
        info_texts = [
            f"位置: ({int(player_pos[0])}, {int(player_pos[1])})",
            f"方向: {player.direction.value}",
            f"移動中: {player.is_moving}",
            f"走行中: {player.is_running}",
            f"スタミナ: {int(player_stats.stamina)}/{player_stats.max_stamina}",
            f"速度: ({player.velocity_x:.1f}, {player.velocity_y:.1f})"
        ]
        
        for i, text in enumerate(info_texts):
            text_surface = font_manager.render_text(text, 18, (255, 255, 255))
            screen.blit(text_surface, (10, 10 + i * 25))
        
        # 操作説明
        controls = [
            "WASD / 矢印キー: 移動",
            "Shift: 走行",
            "ESC: 終了"
        ]
        
        for i, control in enumerate(controls):
            control_surface = font_manager.render_text(control, 16, (255, 255, 255))
            screen.blit(control_surface, (screen.get_width() - 200, 10 + i * 25))
        
        # FPS表示
        fps_text = f"FPS: {int(clock.get_fps())}"
        fps_surface = font_manager.render_text(fps_text, 16, (255, 255, 0))
        screen.blit(fps_surface, (screen.get_width() - 100, screen.get_height() - 30))
        
        pygame.display.flip()
    
    pygame.quit()
    print("🎉 シンプルプレイヤーデモ終了")

if __name__ == "__main__":
    main()
