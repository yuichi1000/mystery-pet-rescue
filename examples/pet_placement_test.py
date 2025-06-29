#!/usr/bin/env python3
"""
ペット配置システムのテスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from src.scenes.game import GameScene
from src.systems.map_system import MapSystem

def test_pet_placement():
    """ペット配置のテスト"""
    print("🐾 ペット配置システムテスト開始")
    print("=" * 50)
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("ペット配置テスト")
    
    try:
        # ゲームシーン作成
        game_scene = GameScene(screen)
        
        print("📊 ペット配置情報:")
        print(f"  生成されたペット数: {len(game_scene.pets)}")
        
        # 各ペットの位置を確認
        for i, pet in enumerate(game_scene.pets):
            x, y = pet.x, pet.y
            print(f"  ペット{i+1} ({pet.data.name}): ({x:.1f}, {y:.1f})")
            
            # 建物との重複チェック
            is_blocked = game_scene._is_position_blocked_by_building(x, y)
            walkable = game_scene.map_system.is_walkable(x, y)
            
            print(f"    通過可能: {'✅' if walkable else '❌'}")
            print(f"    建物重複: {'❌' if is_blocked else '✅'}")
            
            if is_blocked or not walkable:
                print(f"    ⚠️ 問題のある配置です！")
        
        # 視覚的テスト（5秒間表示）
        print("\n🎮 視覚的テスト（5秒間）")
        print("ペットの配置を確認してください...")
        
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()
        
        while pygame.time.get_ticks() - start_time < 5000:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
            
            # 背景クリア
            screen.fill((40, 40, 40))
            
            # ゲームシーン描画
            game_scene.draw(screen)
            
            # 情報表示
            font = pygame.font.Font(None, 24)
            info_texts = [
                f"ペット数: {len(game_scene.pets)}",
                "ESCで終了",
                "ペットが建物に重なっていないか確認"
            ]
            
            for i, text in enumerate(info_texts):
                surface = font.render(text, True, (255, 255, 255))
                screen.blit(surface, (20, 20 + i * 25))
            
            pygame.display.flip()
            clock.tick(60)
        
        print("✅ ペット配置システムテスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

def main():
    """メイン関数"""
    test_pet_placement()

if __name__ == "__main__":
    main()
