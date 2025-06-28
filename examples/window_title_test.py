#!/usr/bin/env python3
"""
ウィンドウタイトル多言語対応テスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from src.utils.language_manager import get_language_manager, Language, get_text

def test_window_title():
    """ウィンドウタイトルの多言語対応テスト"""
    print("🪟 ウィンドウタイトル多言語対応テスト開始")
    print("=" * 50)
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((400, 300))
    
    # 言語マネージャーを取得
    lang_manager = get_language_manager()
    
    # 各言語でウィンドウタイトルをテスト
    for language in [Language.ENGLISH, Language.JAPANESE]:
        print(f"\n📝 言語: {language.value}")
        print("-" * 30)
        
        # 言語を設定
        lang_manager.set_language(language)
        
        # ウィンドウタイトルを取得・設定
        title = get_text("game_title")
        pygame.display.set_caption(title)
        
        print(f"ウィンドウタイトル: '{title}'")
        print(f"pygame.display.get_caption(): {pygame.display.get_caption()}")
        
        # 少し待機（確認用）
        pygame.time.wait(1000)
    
    pygame.quit()
    print("\n✅ ウィンドウタイトルテスト完了")

def main():
    """メイン関数"""
    try:
        test_window_title()
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
