#!/usr/bin/env python3
"""
音響システムのテスト
"""

import pygame
import sys
import time
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.audio_system import get_audio_system

def test_audio_system():
    """音響システムのテスト"""
    print("🎵 音響システムテスト開始")
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("音響システムテスト")
    clock = pygame.time.Clock()
    
    # 音響システム取得
    audio_system = get_audio_system()
    
    print(f"利用可能なBGM: {audio_system.get_bgm_list()}")
    print(f"利用可能な効果音: {audio_system.get_sfx_list()}")
    
    # テスト用フォント
    font = pygame.font.Font(None, 36)
    
    # テスト状態
    test_phase = 0
    test_timer = 0
    
    running = True
    while running:
        dt = clock.tick(60) / 1000.0
        test_timer += dt
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_1:
                    print("BGMテスト: residential_bgm")
                    audio_system.play_bgm("residential_bgm")
                elif event.key == pygame.K_2:
                    print("BGMテスト: victory_bgm")
                    audio_system.play_bgm("victory_bgm")
                elif event.key == pygame.K_3:
                    print("BGM停止")
                    audio_system.stop_bgm()
                elif event.key == pygame.K_4:
                    print("効果音テスト: pet_found")
                    audio_system.play_sfx("pet_found")
                elif event.key == pygame.K_5:
                    print("効果音テスト: pet_rescued")
                    audio_system.play_sfx("pet_rescued")
                elif event.key == pygame.K_SPACE:
                    test_phase = (test_phase + 1) % 3
                    test_timer = 0
        
        # 自動テスト
        if test_phase == 1 and test_timer > 3:
            print("自動テスト: BGM再生")
            audio_system.play_bgm("residential_bgm")
            test_phase = 2
            test_timer = 0
        elif test_phase == 2 and test_timer > 2:
            print("自動テスト: 効果音再生")
            audio_system.play_sfx("pet_found")
            test_phase = 0
            test_timer = 0
        
        # 描画
        screen.fill((50, 50, 50))
        
        # 指示テキスト
        instructions = [
            "音響システムテスト",
            "",
            "1: residential_bgm 再生",
            "2: victory_bgm 再生", 
            "3: BGM停止",
            "4: pet_found 効果音",
            "5: pet_rescued 効果音",
            "SPACE: 自動テスト",
            "ESC: 終了",
            "",
            f"現在のBGM: {audio_system.get_current_bgm() or 'なし'}",
            f"BGM再生中: {audio_system.is_bgm_playing()}",
        ]
        
        y = 50
        for instruction in instructions:
            if instruction:
                text = font.render(instruction, True, (255, 255, 255))
                screen.blit(text, (50, y))
            y += 40
        
        pygame.display.flip()
    
    # クリーンアップ
    audio_system.cleanup()
    pygame.quit()
    print("🎵 音響システムテスト終了")

if __name__ == "__main__":
    test_audio_system()
