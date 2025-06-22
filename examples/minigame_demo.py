#!/usr/bin/env python3
"""
ミニゲームフレームワークのデモ
"""

import sys
import pygame
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from src.scenes.minigame_scene import MinigameScene

def main():
    print("🎮 ミニゲームデモ起動中...")
    
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("ミニゲーム - デモ")
    clock = pygame.time.Clock()
    
    try:
        minigame_scene = MinigameScene(screen)
        minigame_scene.enter()
        
        print("✅ 初期化完了")
        print("1/2: ゲーム選択, D: 難易度, T: 時間, ESC: 終了")
        
        running = True
        while running:
            time_delta = clock.tick(60) / 1000.0
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                result = minigame_scene.handle_event(event)
                if result == "menu":
                    running = False
            
            minigame_scene.update(time_delta)
            minigame_scene.draw(screen)
            pygame.display.flip()
        
        print("🎉 デモ終了")
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
