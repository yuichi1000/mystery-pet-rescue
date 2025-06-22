#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
速度調整テスト
様々な速度でプレイヤーの移動をテスト
"""

import pygame
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 基本設定
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60

# 色定義
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_BLUE = (0, 0, 255)
COLOR_GREEN = (0, 255, 0)
COLOR_RED = (255, 0, 0)
COLOR_YELLOW = (255, 255, 0)

class SpeedTestPlayer:
    """速度テスト用プレイヤークラス"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 300  # ピクセル/秒
        self.size = 50
        self.trail = []  # 軌跡
        
    def update(self, dt):
        """プレイヤー更新"""
        keys = pygame.key.get_pressed()
        
        # 速度調整
        if keys[pygame.K_1]:
            self.speed = 100  # 遅い
        elif keys[pygame.K_2]:
            self.speed = 300  # 普通
        elif keys[pygame.K_3]:
            self.speed = 500  # 速い
        elif keys[pygame.K_4]:
            self.speed = 800  # 非常に速い
        
        # WASD移動
        moved = False
        if keys[pygame.K_w]:
            self.y -= self.speed * dt
            moved = True
        if keys[pygame.K_s]:
            self.y += self.speed * dt
            moved = True
        if keys[pygame.K_a]:
            self.x -= self.speed * dt
            moved = True
        if keys[pygame.K_d]:
            self.x += self.speed * dt
            moved = True
        
        # 画面境界チェック
        self.x = max(0, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.size, self.y))
        
        # 軌跡更新
        if moved:
            self.trail.append((int(self.x + self.size//2), int(self.y + self.size//2)))
            if len(self.trail) > 100:  # 軌跡の長さ制限
                self.trail.pop(0)
    
    def render(self, screen):
        """プレイヤー描画"""
        # 軌跡描画
        if len(self.trail) > 1:
            for i in range(1, len(self.trail)):
                alpha = i / len(self.trail)
                start_pos = self.trail[i-1]
                end_pos = self.trail[i]
                pygame.draw.line(screen, COLOR_YELLOW, start_pos, end_pos, 2)
        
        # プレイヤー本体
        rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)
        pygame.draw.rect(screen, COLOR_BLUE, rect)
        pygame.draw.rect(screen, COLOR_WHITE, rect, 2)

def main():
    """メイン関数"""
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Speed Test - Press 1/2/3/4 for different speeds")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    small_font = pygame.font.Font(None, 24)
    
    # プレイヤー作成
    player = SpeedTestPlayer(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    running = True
    last_time = pygame.time.get_ticks() / 1000.0
    
    print("速度調整テスト開始")
    print("WASD: 移動")
    print("1: 遅い (100px/s)")
    print("2: 普通 (300px/s)")
    print("3: 速い (500px/s)")
    print("4: 非常に速い (800px/s)")
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
                elif event.key == pygame.K_c:
                    player.trail.clear()  # 軌跡クリア
        
        # 更新
        player.update(dt)
        
        # 描画
        screen.fill(COLOR_BLACK)
        player.render(screen)
        
        # 情報表示
        info_lines = [
            f"Position: ({player.x:.0f}, {player.y:.0f})",
            f"Speed: {player.speed} px/s",
            f"FPS: {clock.get_fps():.1f}",
            f"Delta Time: {dt:.3f}s"
        ]
        
        for i, line in enumerate(info_lines):
            text = small_font.render(line, True, COLOR_WHITE)
            screen.blit(text, (10, 10 + i * 25))
        
        # 操作説明
        instructions = [
            "WASD: Move",
            "1: Slow (100px/s)",
            "2: Normal (300px/s)", 
            "3: Fast (500px/s)",
            "4: Very Fast (800px/s)",
            "C: Clear trail",
            "ESC: Quit"
        ]
        
        for i, instruction in enumerate(instructions):
            color = COLOR_GREEN if i < 1 else COLOR_WHITE
            text = small_font.render(instruction, True, color)
            screen.blit(text, (10, SCREEN_HEIGHT - 180 + i * 25))
        
        # 現在の速度を大きく表示
        speed_text = font.render(f"Current Speed: {player.speed} px/s", True, COLOR_RED)
        screen.blit(speed_text, (SCREEN_WIDTH - 400, 20))
        
        # 速度レベル表示
        speed_levels = {
            100: "SLOW",
            300: "NORMAL", 
            500: "FAST",
            800: "VERY FAST"
        }
        level_text = speed_levels.get(player.speed, "CUSTOM")
        level_surface = font.render(level_text, True, COLOR_YELLOW)
        screen.blit(level_surface, (SCREEN_WIDTH - 400, 60))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    print("速度テスト終了")

if __name__ == "__main__":
    main()
