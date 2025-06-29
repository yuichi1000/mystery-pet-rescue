#!/usr/bin/env python3
"""
Web版デバッグスクリプト
Web版の動作確認とデバッグ情報出力
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# Web環境フラグ設定
os.environ['WEB_VERSION'] = '1'

def debug_imports():
    """インポートのデバッグ"""
    print("🔍 インポートデバッグ")
    print("=" * 40)
    
    modules_to_test = [
        'pygame',
        'src.utils.web_utils',
        'src.core.game_main',
        'src.core.game_flow',
        'src.utils.asset_manager',
        'src.utils.font_manager',
        'src.systems.audio_system'
    ]
    
    for module_name in modules_to_test:
        try:
            module = __import__(module_name)
            print(f"✅ {module_name}: OK")
        except ImportError as e:
            print(f"❌ {module_name}: {e}")
        except Exception as e:
            print(f"⚠️ {module_name}: {e}")

def debug_web_environment():
    """Web環境のデバッグ"""
    print("\n🌐 Web環境デバッグ")
    print("=" * 40)
    
    try:
        from src.utils.web_utils import is_web_environment, log_web_info, check_web_assets
        
        print(f"Web環境判定: {is_web_environment()}")
        log_web_info()
        
        print("\n📁 アセット確認:")
        assets = check_web_assets()
        for asset, exists in assets.items():
            status = "✅" if exists else "❌"
            print(f"  {status} {asset}")
            
    except Exception as e:
        print(f"❌ Web環境デバッグエラー: {e}")
        import traceback
        traceback.print_exc()

def debug_pygame_init():
    """Pygame初期化のデバッグ"""
    print("\n🎮 Pygame初期化デバッグ")
    print("=" * 40)
    
    try:
        import pygame
        print(f"Pygame バージョン: {pygame.version.ver}")
        
        # 初期化
        pygame.init()
        print("✅ pygame.init() 成功")
        
        # 音声初期化
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
            print("✅ pygame.mixer.init() 成功")
        except Exception as e:
            print(f"⚠️ pygame.mixer.init() 失敗: {e}")
        
        # 画面初期化
        try:
            screen = pygame.display.set_mode((800, 600))
            print("✅ pygame.display.set_mode() 成功")
            pygame.display.set_caption("Debug Test")
            print("✅ pygame.display.set_caption() 成功")
        except Exception as e:
            print(f"❌ 画面初期化失敗: {e}")
        
        # イベント処理テスト
        try:
            events = pygame.event.get()
            print(f"✅ pygame.event.get() 成功 ({len(events)} イベント)")
        except Exception as e:
            print(f"❌ イベント処理失敗: {e}")
        
    except Exception as e:
        print(f"❌ Pygame初期化エラー: {e}")
        import traceback
        traceback.print_exc()

def debug_game_main():
    """GameMain初期化のデバッグ"""
    print("\n🎮 GameMain初期化デバッグ")
    print("=" * 40)
    
    try:
        from src.core.game_main import GameMain
        
        print("GameMain クラス作成中...")
        game = GameMain()
        print("✅ GameMain 初期化成功")
        
        # 属性確認
        attributes = ['screen', 'clock', 'flow_manager', 'is_web']
        for attr in attributes:
            if hasattr(game, attr):
                value = getattr(game, attr)
                print(f"✅ {attr}: {type(value).__name__}")
            else:
                print(f"❌ {attr}: 属性なし")
        
    except Exception as e:
        print(f"❌ GameMain初期化エラー: {e}")
        import traceback
        traceback.print_exc()

def debug_async_loop():
    """非同期ループのデバッグ"""
    print("\n🔄 非同期ループデバッグ")
    print("=" * 40)
    
    try:
        import asyncio
        
        async def test_async():
            print("✅ 非同期関数実行開始")
            for i in range(3):
                print(f"  フレーム {i+1}")
                await asyncio.sleep(0)
            print("✅ 非同期関数実行完了")
        
        # 非同期実行テスト
        asyncio.run(test_async())
        print("✅ asyncio.run() 成功")
        
    except Exception as e:
        print(f"❌ 非同期ループエラー: {e}")
        import traceback
        traceback.print_exc()

def main():
    """メインデバッグ関数"""
    print("🐛 Web版デバッグスクリプト")
    print("=" * 60)
    print(f"Python バージョン: {sys.version}")
    print(f"作業ディレクトリ: {os.getcwd()}")
    print(f"sys.path: {sys.path[:3]}...")
    
    # 各種デバッグ実行
    debug_imports()
    debug_web_environment()
    debug_pygame_init()
    debug_game_main()
    debug_async_loop()
    
    print("\n🎯 デバッグ完了")
    print("=" * 60)
    print("Web版の問題がある場合は、上記の❌項目を確認してください")

if __name__ == "__main__":
    main()
