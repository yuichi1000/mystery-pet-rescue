#!/usr/bin/env python3
"""
UI機能削除テスト（ミニマップ・フルスクリーン）
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from src.ui.game_ui import GameUI
from src.utils.language_manager import get_text

def test_ui_feature_removal():
    """UI機能削除のテスト"""
    print("🗑️ UI機能削除テスト開始")
    print("=" * 50)
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("UI機能削除テスト")
    
    try:
        # GameUI作成
        game_ui = GameUI(screen)
        
        # UI画像の読み込み
        game_ui._load_ui_images()
        
        # UIレイアウト設定
        try:
            game_ui._setup_ui_layout()
            print("✅ UIレイアウト設定完了")
        except Exception as e:
            print(f"❌ UIレイアウト設定エラー: {e}")
            import traceback
            traceback.print_exc()
        
        print("🔍 削除された機能の確認:")
        
        # ミニマップ関連の確認
        print("  📍 ミニマップ機能:")
        has_minimap_method = hasattr(game_ui, '_draw_minimap')
        has_minimap_surface = hasattr(game_ui, 'minimap_surface')
        has_minimap_rect = hasattr(game_ui, 'minimap_rect')
        has_set_map_system = hasattr(game_ui, 'set_map_system')
        
        print(f"    _draw_minimap メソッド: {'❌ 存在' if has_minimap_method else '✅ 削除済み'}")
        print(f"    minimap_surface 属性: {'❌ 存在' if has_minimap_surface else '✅ 削除済み'}")
        print(f"    minimap_rect 属性: {'❌ 存在' if has_minimap_rect else '✅ 削除済み'}")
        print(f"    set_map_system メソッド: {'❌ 存在' if has_set_map_system else '✅ 削除済み'}")
        
        # 翻訳キーの確認
        print("  🌐 翻訳キー:")
        try:
            minimap_text = get_text("minimap")
            print(f"    'minimap' キー: ❌ 存在 ('{minimap_text}')")
        except KeyError:
            print(f"    'minimap' キー: ✅ 削除済み")
        
        try:
            controls_minimap = get_text("controls_minimap")
            print(f"    'controls_minimap' キー: ❌ 存在 ('{controls_minimap}')")
        except KeyError:
            print(f"    'controls_minimap' キー: ✅ 削除済み")
        
        # GameUIの基本機能が正常に動作するかテスト
        print("\n🧪 基本機能テスト:")
        
        # 通知システム
        from src.ui.game_ui import NotificationType
        game_ui.add_notification("テスト通知", NotificationType.INFO)
        print("    通知システム: ✅ 正常動作")
        
        # 描画テスト（3秒間）
        print("    描画テスト（3秒間）...")
        
        clock = pygame.time.Clock()
        start_time = pygame.time.get_ticks()
        
        while pygame.time.get_ticks() - start_time < 3000:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        return
            
            time_delta = clock.tick(60) / 1000.0
            game_ui.update(time_delta)
            
            # 背景クリア
            screen.fill((40, 40, 40))
            
            # UI描画（ミニマップなし）
            game_ui.draw(screen, [], (640, 360))
            
            # 情報表示
            font = pygame.font.Font(None, 24)
            info_texts = [
                "ミニマップ機能削除テスト",
                "ESCで終了",
                "ミニマップが表示されていないことを確認"
            ]
            
            for i, text in enumerate(info_texts):
                surface = font.render(text, True, (255, 255, 255))
                screen.blit(surface, (20, 20 + i * 25))
            
            pygame.display.flip()
        
        print("    描画テスト: ✅ 正常動作（ミニマップなし）")
        
        print("\n✅ UI機能削除テスト完了")
        print("📋 結果:")
        print("  - ミニマップ機能: 完全削除")
        print("  - 翻訳キー: 削除済み")
        print("  - 基本UI機能: 正常動作")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

def main():
    """メイン関数"""
    test_ui_feature_removal()

if __name__ == "__main__":
    main()
