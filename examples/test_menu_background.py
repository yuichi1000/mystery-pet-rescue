#!/usr/bin/env python3
"""
メニュー背景画像テスト
メニューシーンの背景画像表示を確認
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from src.scenes.menu import MenuScene

def main():
    """メニュー背景画像テスト"""
    print("🖼️ メニュー背景画像テスト開始")
    
    # Pygame初期化
    pygame.init()
    
    # 画面設定
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("メニュー背景画像テスト")
    
    # メニューシーン作成
    menu_scene = MenuScene(screen)
    menu_scene.enter()
    
    # ゲームループ
    clock = pygame.time.Clock()
    running = True
    
    print("🎮 メニュー表示中（ESCで終了）")
    
    while running:
        time_delta = clock.tick(60) / 1000.0
        
        # イベント処理
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                else:
                    # メニューのイベント処理
                    result = menu_scene.handle_event(event)
                    if result == "quit":
                        running = False
        
        # 更新
        menu_scene.update(time_delta)
        
        # 描画
        screen.fill((0, 0, 0))
        menu_scene.draw(screen)
        
        # 背景画像の状態を画面に表示
        font = pygame.font.Font(None, 24)
        if menu_scene.background_image:
            status_text = f"✅ 背景画像: {menu_scene.background_image.get_size()}"
            color = (0, 255, 0)
        else:
            status_text = "❌ 背景画像: 読み込み失敗"
            color = (255, 0, 0)
        
        status_surface = font.render(status_text, True, color)
        screen.blit(status_surface, (10, 10))
        
        pygame.display.flip()
    
    menu_scene.exit()
    pygame.quit()
    print("🖼️ メニュー背景画像テスト終了")

if __name__ == "__main__":
    main()
