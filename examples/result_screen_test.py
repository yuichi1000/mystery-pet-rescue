#!/usr/bin/env python3
"""
結果画面テスト（勝利・敗北・時間切れ）
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from src.scenes.result import ResultScene

def test_result_screens():
    """結果画面のテスト"""
    print("🏆 結果画面テスト開始")
    print("=" * 50)
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("結果画面テスト")
    
    # テストシナリオ
    scenarios = [
        {
            "name": "完璧クリア",
            "result": {
                'victory': True,
                'game_over': False,
                'defeat_reason': None,
                'pets_rescued': 4,
                'total_pets': 4,
                'time_taken': 120.0,
                'remaining_time': 60.0,
                'score': 4600,
                'completion_rate': 100.0
            }
        },
        {
            "name": "時間切れ",
            "result": {
                'victory': False,
                'game_over': True,
                'defeat_reason': 'time_up',
                'pets_rescued': 2,
                'total_pets': 4,
                'time_taken': 180.0,
                'remaining_time': 0.0,
                'score': 2000,
                'completion_rate': 50.0
            }
        },
        {
            "name": "部分クリア",
            "result": {
                'victory': False,
                'game_over': True,
                'defeat_reason': 'other',
                'pets_rescued': 3,
                'total_pets': 4,
                'time_taken': 150.0,
                'remaining_time': 30.0,
                'score': 3300,
                'completion_rate': 75.0
            }
        }
    ]
    
    current_scenario = 0
    clock = pygame.time.Clock()
    running = True
    
    # 最初のシナリオで結果画面作成
    result_scene = ResultScene(screen, scenarios[current_scenario]["result"])
    
    print(f"📊 現在のシナリオ: {scenarios[current_scenario]['name']}")
    print("スペースキー: 次のシナリオ")
    print("ESCキー: 終了")
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # 次のシナリオに切り替え
                    current_scenario = (current_scenario + 1) % len(scenarios)
                    result_scene = ResultScene(screen, scenarios[current_scenario]["result"])
                    print(f"📊 現在のシナリオ: {scenarios[current_scenario]['name']}")
        
        # 描画
        screen.fill((0, 0, 0))
        result_scene.draw(screen)
        
        # シナリオ情報表示
        font = pygame.font.Font(None, 24)
        info_text = f"シナリオ: {scenarios[current_scenario]['name']} ({current_scenario + 1}/{len(scenarios)})"
        info_surface = font.render(info_text, True, (255, 255, 255))
        screen.blit(info_surface, (20, 20))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    print("✅ 結果画面テスト完了")

def main():
    """メイン関数"""
    try:
        test_result_screens()
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
