#!/usr/bin/env python3
"""
謎解きシステムデモ
アイテム組み合わせ謎解きゲームのデモンストレーション
"""

import sys
import pygame
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.puzzle_system import PuzzleSystem
from src.ui.puzzle_ui import PuzzleUI

def main():
    print("🧩 謎解きシステムデモ起動中...")
    
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("謎解きシステムデモ - アイテム組み合わせ")
    clock = pygame.time.Clock()
    
    # システム初期化
    puzzle_system = PuzzleSystem()
    puzzle_ui = PuzzleUI(screen, puzzle_system)
    
    print("✅ 謎解きシステム初期化完了")
    print("🎯 利用可能な謎解き:")
    
    puzzles = puzzle_system.get_available_puzzles()
    for puzzle in puzzles:
        print(f"  - {puzzle['title']} ({puzzle['difficulty']})")
    
    print("\n🎮 操作方法:")
    print("  マウス: 謎解き選択・アイテム選択・ボタンクリック")
    print("  H: ヒント要求")
    print("  R: 謎解きリセット")
    print("  ESC: 謎解き選択に戻る")
    
    running = True
    
    while running:
        time_delta = clock.tick(60) / 1000.0
        events = pygame.event.get()
        
        for event in events:
            if event.type == pygame.QUIT:
                running = False
        
        # UI更新
        result = puzzle_ui.update(time_delta, events)
        
        # 終了チェック
        if result == "quit":
            running = False
        
        # 描画
        puzzle_ui.draw()
        
        pygame.display.flip()
    
    # 進行状況を保存
    puzzle_system.save_progress()
    
    print("🎉 謎解きシステムデモ終了")
    pygame.quit()

if __name__ == "__main__":
    main()
