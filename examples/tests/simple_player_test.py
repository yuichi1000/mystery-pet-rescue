#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
シンプルなプレイヤーテスト
WASDキーの動作確認用
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

class SimplePlayer:
    """シンプルなプレイヤークラス"""
    
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.speed = 300  # ピクセル/秒（適切な速度）
        self.size = 50
        
    def update(self, dt):
        """プレイヤー更新"""
        keys = pygame.key.get_pressed()
        
        # WASD移動
        if keys[pygame.K_w]:
            self.y -= self.speed * dt
        if keys[pygame.K_s]:
            self.y += self.speed * dt
        if keys[pygame.K_a]:
            self.x -= self.speed * dt
        if keys[pygame.K_d]:
            self.x += self.speed * dt
        
        # 画面境界チェック
        self.x = max(0, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(0, min(SCREEN_HEIGHT - self.size, self.y))
    
    def render(self, screen):
        """プレイヤー描画"""
        rect = pygame.Rect(int(self.x), int(self.y), self.size, self.size)
        pygame.draw.rect(screen, COLOR_BLUE, rect)
        pygame.draw.rect(screen, COLOR_WHITE, rect, 2)

def main():
    """メイン関数"""
    pygame.init()
    
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simple Player Test - WASD to Move")
    clock = pygame.time.Clock()
    font = pygame.font.Font(None, 36)
    
    # プレイヤー作成
    player = SimplePlayer(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
    
    running = True
    last_time = pygame.time.get_ticks() / 1000.0
    
    print("シンプルプレイヤーテスト開始")
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
        
        # 更新
        player.update(dt)
        
        # 描画
        screen.fill(COLOR_BLACK)
        player.render(screen)
        
        # 情報表示
        info_text = font.render(f"Position: ({player.x:.0f}, {player.y:.0f})", True, COLOR_WHITE)
        screen.blit(info_text, (10, 10))
        
        instruction_text = font.render("WASD: Move  ESC: Quit", True, COLOR_GREEN)
        screen.blit(instruction_text, (10, 50))
        
        # キー状態表示
        keys = pygame.key.get_pressed()
        key_status = []
        if keys[pygame.K_w]: key_status.append("W")
        if keys[pygame.K_a]: key_status.append("A")
        if keys[pygame.K_s]: key_status.append("S")
        if keys[pygame.K_d]: key_status.append("D")
        
        if key_status:
            key_text = font.render(f"Keys: {' '.join(key_status)}", True, COLOR_RED)
            screen.blit(key_text, (10, 90))
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    print("テスト終了")

if __name__ == "__main__":
    main()
