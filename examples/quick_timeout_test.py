#!/usr/bin/env python3
"""
短時間タイムアウトテスト（5秒でタイムアウト）
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from src.core.game_main import Game
from src.utils.config import Config

def main():
    """メイン関数"""
    print("⚡ 短時間タイムアウトテスト開始")
    print("=" * 50)
    print("⏰ 5秒でタイムアウトします")
    print("何もせずに待ってください...")
    
    try:
        # 設定読み込み
        config = Config.load()
        
        # ゲーム作成
        game = Game(config)
        
        # タイマーを5秒に短縮（テスト用）
        # ゲーム開始後にタイマーを変更
        def modify_timer():
            if hasattr(game.flow_manager, 'current_scene'):
                scene = game.flow_manager.current_scene
                if hasattr(scene, 'timer_system'):
                    scene.timer_system.time_limit = 5.0
                    scene.timer_system.remaining_time = 5.0
                    print("⏰ タイマーを5秒に設定しました")
        
        # ゲーム開始
        game.flow_manager.change_scene("game")
        modify_timer()
        
        # ゲーム実行
        game.run()
        
    except KeyboardInterrupt:
        print("⚠️ ユーザーによる中断")
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
