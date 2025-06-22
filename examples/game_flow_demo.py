#!/usr/bin/env python3
"""
ゲームフローデモ
タイトル→ゲーム→結果の流れをテスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from src.core.game_flow import GameFlowManager

def main():
    """ゲームフローデモ"""
    print("🎮 ゲームフローデモ")
    print("=" * 50)
    print("📋 テスト内容:")
    print("  1. タイトル画面表示")
    print("  2. ゲーム画面への遷移")
    print("  3. ペット救出ゲーム")
    print("  4. 結果画面表示")
    print("  5. メニューへの戻り")
    print("=" * 50)
    print()
    print("🎯 操作方法:")
    print("  - ENTER/SPACE: ゲーム開始")
    print("  - WASD/矢印キー: プレイヤー移動")
    print("  - P: ポーズ")
    print("  - ESC: メニューに戻る")
    print("  - Q: ゲーム終了")
    print("=" * 50)
    print()
    
    # Pygame初期化
    pygame.init()
    pygame.mixer.init()
    
    # 画面設定
    screen_width = 1280
    screen_height = 720
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("ゲームフローデモ - ミステリー・ペット・レスキュー")
    
    # ゲームフロー管理
    flow_manager = GameFlowManager(screen)
    
    # ゲーム設定
    clock = pygame.time.Clock()
    target_fps = 60
    
    try:
        print("🚀 デモ開始")
        
        while flow_manager.is_running():
            # フレーム時間計算
            time_delta = clock.tick(target_fps) / 1000.0
            
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    flow_manager.running = False
                else:
                    flow_manager.handle_event(event)
            
            # 更新処理
            flow_manager.update(time_delta)
            
            # 描画処理
            screen.fill((0, 0, 0))  # 背景クリア
            flow_manager.draw(screen)
            
            # FPS表示
            fps_text = f"FPS: {int(clock.get_fps())}"
            font = pygame.font.Font(None, 24)
            fps_surface = font.render(fps_text, True, (255, 255, 255))
            screen.blit(fps_surface, (10, 10))
            
            # 現在のシーン表示
            scene_name = flow_manager.get_current_scene_name()
            scene_text = f"Scene: {scene_name}"
            scene_surface = font.render(scene_text, True, (255, 255, 255))
            screen.blit(scene_surface, (10, 35))
            
            # 画面更新
            pygame.display.flip()
        
        print("✅ デモ正常終了")
        
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        print("👋 デモを終了します")

if __name__ == "__main__":
    main()
