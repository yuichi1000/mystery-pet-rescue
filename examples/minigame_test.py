#!/usr/bin/env python3
"""ミニゲームテスト"""

import sys
import pygame
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.minigame_manager import MinigameManager, MinigameType
from src.core.minigame import GameConfig, Difficulty

def main():
    print("🎮 ミニゲームテスト開始")
    
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    try:
        manager = MinigameManager(screen)
        print("✅ マネージャー作成成功")
        
        # アクションゲームテスト
        config = GameConfig(difficulty=Difficulty.EASY, time_limit=5.0)
        
        if manager.start_game(MinigameType.ACTION, config):
            print("✅ アクションゲーム開始成功")
            
            # 短時間実行
            clock = pygame.time.Clock()
            for i in range(60):  # 1秒間
                for event in pygame.event.get():
                    manager.handle_event(event)
                
                manager.update(1/60)
                screen.fill((240, 248, 255))
                manager.draw(screen)
                pygame.display.flip()
                clock.tick(60)
            
            manager.stop_current_game()
            print("✅ アクションゲーム停止成功")
        
        # 記憶ゲームテスト
        try:
            if manager.start_game(MinigameType.MEMORY, config):
                print("✅ 記憶ゲーム開始成功")
                manager.stop_current_game()
                print("✅ 記憶ゲーム停止成功")
        except Exception as e:
            print(f"❌ 記憶ゲームエラー: {e}")
        
        print("🎉 テスト完了")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
