#!/usr/bin/env python3
"""
通知システムの言語対応テスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from src.utils.language_manager import get_language_manager, get_text, Language
from src.ui.game_ui import GameUI, NotificationType
from src.utils.font_manager import get_font_manager

def test_notification_languages():
    """通知システムの言語対応テスト"""
    print("🌐 通知システム言語対応テスト開始")
    print("=" * 50)
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("通知言語テスト")
    
    try:
        # フォントマネージャー初期化
        font_manager = get_font_manager()
        
        # GameUI作成
        game_ui = GameUI(screen)
        
        # テスト対象の通知メッセージ
        test_notifications = [
            ("time_warning", NotificationType.WARNING),
            ("no_lives", NotificationType.ERROR),
            ("objective_completed", NotificationType.SUCCESS),
            ("collision_debug_output", NotificationType.INFO),
            ("collision_display_on", NotificationType.INFO),
            ("collision_display_off", NotificationType.INFO),
        ]
        
        # 特殊フォーマット付きメッセージ
        time_bonus_msg = get_text("time_bonus_message").format(bonus=150)
        
        languages = [Language.JAPANESE, Language.ENGLISH]
        
        for lang in languages:
            print(f"\n🌐 言語: {lang.value}")
            get_language_manager().set_language(lang)
            
            print("📢 通知メッセージ:")
            for key, notification_type in test_notifications:
                message = get_text(key)
                print(f"  {key}: {message}")
            
            print(f"  time_bonus_message: {time_bonus_msg}")
            
            # 実際の通知表示テスト
            print(f"\n🎮 {lang.value}での通知表示テスト（3秒間）")
            
            # 通知を追加
            for key, notification_type in test_notifications:
                game_ui.add_notification(get_text(key), notification_type, duration=2.0)
            
            # タイムボーナス通知
            game_ui.add_notification(time_bonus_msg, NotificationType.INFO, duration=2.0)
            
            # 3秒間表示
            clock = pygame.time.Clock()
            start_time = pygame.time.get_ticks()
            
            while pygame.time.get_ticks() - start_time < 3000:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                
                time_delta = clock.tick(60) / 1000.0
                game_ui.update(time_delta)
                
                # 背景クリア
                screen.fill((40, 40, 40))
                
                # 言語情報表示
                font = pygame.font.Font(None, 36)
                lang_text = font.render(f"Language: {lang.value.upper()}", True, (255, 255, 255))
                screen.blit(lang_text, (20, 20))
                
                # UI描画
                game_ui.draw(screen)
                
                pygame.display.flip()
            
            # 通知をクリア
            game_ui.notifications.clear()
        
        print("\n✅ 通知システム言語対応テスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

def main():
    """メイン関数"""
    test_notification_languages()

if __name__ == "__main__":
    main()
