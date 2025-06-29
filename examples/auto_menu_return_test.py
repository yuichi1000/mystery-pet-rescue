#!/usr/bin/env python3
"""
自動メニュー復帰テスト
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

def test_auto_menu_return():
    """自動メニュー復帰のテスト"""
    print("🔄 自動メニュー復帰テスト開始")
    print("=" * 50)
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("自動メニュー復帰テスト")
    
    try:
        # マップシステム初期化
        map_system = MapSystem()
        
        # ゲームシーン作成
        game_scene = GameScene(screen)
        
        # 時間切れ状態をシミュレート
        game_scene.game_over = True
        game_scene.defeat_display_time = 0.0
        game_scene.pets_rescued = ["dog"]  # 1匹救出済み
        game_scene.total_pets = 4
        game_scene.start_time = time.time() - 180  # 3分経過
        
        print("📊 テスト設定:")
        print(f"  game_over: {game_scene.game_over}")
        print(f"  defeat_display_time: {game_scene.defeat_display_time}")
        print(f"  救出ペット: {len(game_scene.pets_rescued)}/{game_scene.total_pets}匹")
        print("\n⏰ 3秒後に自動でメニューに戻る予定")
        print("ESCキーで手動終了")
        
        # 描画テスト
        clock = pygame.time.Clock()
        running = True
        test_start_time = time.time()
        
        while running:
            time_delta = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # ゲームシーンの更新
            result = game_scene.update(time_delta)
            print(f"📊 update結果: {result}, game_over: {game_scene.game_over}, defeat_time: {game_scene.defeat_display_time:.1f}")
            
            # メニューに戻る判定
            if result == "menu":
                print("✅ 自動メニュー復帰成功！")
                break
            
            # 背景クリア
            screen.fill((40, 40, 40))
            
            # ゲームシーン描画
            game_scene.draw(screen)
            
            # テスト情報表示
            font = pygame.font.Font(None, 24)
            info_texts = [
                f"敗北表示時間: {game_scene.defeat_display_time:.1f}秒",
                f"残り時間: {max(0, 3.0 - game_scene.defeat_display_time):.1f}秒",
                f"game_over: {game_scene.game_over}",
                "ESCで終了"
            ]
            
            for i, text in enumerate(info_texts):
                surface = font.render(text, True, (255, 255, 255))
                screen.blit(surface, (20, 20 + i * 25))
            
            pygame.display.flip()
            
            # 10秒でタイムアウト
            if time.time() - test_start_time > 10:
                print("⚠️ 10秒経過 - タイムアウト")
                break
        
        print("✅ 自動メニュー復帰テスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

def main():
    """メイン関数"""
    test_auto_menu_return()

if __name__ == "__main__":
    main()
