#!/usr/bin/env python3
"""
ゲーム画面の言語対応テスト（勝利・敗北画面）
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.language_manager import get_language_manager, get_text, Language

def test_game_screen_translations():
    """ゲーム画面の翻訳テスト"""
    print("🎮 ゲーム画面言語対応テスト開始")
    print("=" * 50)
    
    # テスト対象の翻訳キー
    test_keys = [
        # 敗北画面用
        "pets_rescued_subtitle",
        "pets_rescued_count", 
        "pet_unit",
        
        # 勝利画面用
        "all_pets_rescued_subtitle",
        "pets_found_count",
        "remaining_time_display",
        
        # 共通
        "returning_to_menu"
    ]
    
    languages = [Language.JAPANESE, Language.ENGLISH]
    
    for lang in languages:
        print(f"\n🌐 言語: {lang.value}")
        get_language_manager().set_language(lang)
        
        print("📢 ゲーム画面メッセージ:")
        
        # 敗北画面のテスト
        print("  💀 敗北画面:")
        try:
            subtitle = get_text("pets_rescued_subtitle").format(count=2, total=4)
            count_text = get_text("pets_rescued_count").format(count=2, total=4)
            print(f"    サブタイトル: {subtitle}")
            print(f"    カウント表示: {count_text}")
        except Exception as e:
            print(f"    ❌ 敗北画面エラー: {e}")
        
        # 勝利画面のテスト
        print("  🎉 勝利画面:")
        try:
            subtitle = get_text("all_pets_rescued_subtitle")
            count_text = get_text("pets_found_count").format(count=4, total=4)
            time_text = get_text("remaining_time_display").format(time="01:23")
            print(f"    サブタイトル: {subtitle}")
            print(f"    カウント表示: {count_text}")
            print(f"    時間表示: {time_text}")
        except Exception as e:
            print(f"    ❌ 勝利画面エラー: {e}")
        
        # 共通メッセージ
        print("  🔄 共通:")
        try:
            menu_text = get_text("returning_to_menu")
            print(f"    メニュー復帰: {menu_text}")
        except Exception as e:
            print(f"    ❌ 共通メッセージエラー: {e}")
    
    print("\n✅ ゲーム画面言語対応テスト完了")

def main():
    """メイン関数"""
    test_game_screen_translations()

if __name__ == "__main__":
    main()
