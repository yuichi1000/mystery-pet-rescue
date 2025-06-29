#!/usr/bin/env python3
"""
敗北画面テスト（時間切れ時の表示確認）
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
import time
from src.scenes.game import GameScene
from src.systems.map_system import MapSystem

def test_defeat_screen():
    """敗北画面のテスト"""
    print("💀 敗北画面テスト開始")
    print("=" * 50)
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("敗北画面テスト")
    
    try:
        # マップシステム初期化
        map_system = MapSystem()
        
        # ゲームシーン作成
        game_scene = GameScene(screen)
        
        # 時間切れ状態をシミュレート
        game_scene.game_over = True
        game_scene.defeat_display_time = 0.0
        game_scene.pets_rescued = ["dog", "cat"]  # 2匹救出済み
        game_scene.total_pets = 4
        game_scene.start_time = time.time() - 150  # 2分30秒経過
        
        print("📊 テスト設定:")
        print(f"  救出ペット: {len(game_scene.pets_rescued)}/{game_scene.total_pets}匹")
        print(f"  経過時間: 2分30秒")
        print(f"  状態: 時間切れ")
        print("\n⏰ 3秒後に自動でメニューに戻る予定")
        print("ESCキーで手動終了")
        
        # 描画テスト
        clock = pygame.time.Clock()
        running = True
        test_start_time = time.time()
        
        while running:
            current_time = time.time()
            time_delta = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # 敗北表示時間を更新
            game_scene.defeat_display_time += time_delta
            
            # 3秒経過で終了
            if game_scene.defeat_display_time >= 3.0:
                print("✅ 3秒経過 - 自動終了")
                break
            
            # 背景クリア
            screen.fill((40, 40, 40))
            
            # 敗北画面描画
            game_scene._draw_defeat_screen(screen)
            
            # テスト情報表示
            font = pygame.font.Font(None, 24)
            info_texts = [
                f"敗北表示時間: {game_scene.defeat_display_time:.1f}秒",
                f"残り時間: {max(0, 3.0 - game_scene.defeat_display_time):.1f}秒",
                "ESCで終了"
            ]
            
            for i, text in enumerate(info_texts):
                surface = font.render(text, True, (255, 255, 255))
                screen.blit(surface, (20, 20 + i * 25))
            
            pygame.display.flip()
        
        print("✅ 敗北画面テスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

def main():
    """メイン関数"""
    test_defeat_screen()

if __name__ == "__main__":
    main()
