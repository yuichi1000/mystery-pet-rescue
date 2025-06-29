#!/usr/bin/env python3
"""
ゲームオーバー処理テスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.game_flow import GameFlowManager
import pygame

def test_game_over_method():
    """GameFlowManagerのgame_overメソッドテスト"""
    print("💀 ゲームオーバーメソッドテスト開始")
    print("=" * 50)
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    try:
        # GameFlowManager作成
        flow_manager = GameFlowManager(screen)
        
        # game_overメソッドの存在確認
        if hasattr(flow_manager, 'game_over'):
            print("✅ game_overメソッドが存在します")
            
            # 各種理由でのテスト
            reasons = ["time_up", "no_lives", "other"]
            
            for reason in reasons:
                print(f"\n🧪 テスト: {reason}")
                try:
                    flow_manager.game_over(reason)
                    print(f"✅ {reason}: 正常実行")
                except Exception as e:
                    print(f"❌ {reason}: エラー - {e}")
        else:
            print("❌ game_overメソッドが存在しません")
        
        print("\n📊 GameFlowManagerのメソッド一覧:")
        methods = [method for method in dir(flow_manager) if not method.startswith('_')]
        for method in sorted(methods):
            print(f"  - {method}")
        
        print("\n✅ ゲームオーバーメソッドテスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

def main():
    """メイン関数"""
    test_game_over_method()

if __name__ == "__main__":
    main()
