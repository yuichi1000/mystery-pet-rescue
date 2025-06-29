#!/usr/bin/env python3
"""
シンプルな通知言語対応テスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.language_manager import get_language_manager, get_text, Language

def test_notification_translations():
    """通知の翻訳テスト"""
    print("🌐 通知翻訳テスト開始")
    print("=" * 50)
    
    # テスト対象の通知メッセージ
    test_keys = [
        "time_warning",
        "no_lives", 
        "time_bonus_message",
        "collision_debug_output",
        "collision_display_on",
        "collision_display_off",
        "objective_completed"
    ]
    
    languages = [Language.JAPANESE, Language.ENGLISH]
    
    for lang in languages:
        print(f"\n🌐 言語: {lang.value}")
        get_language_manager().set_language(lang)
        
        print("📢 通知メッセージ:")
        for key in test_keys:
            try:
                if key == "time_bonus_message":
                    # フォーマット付きメッセージのテスト
                    message = get_text(key).format(bonus=150)
                else:
                    message = get_text(key)
                print(f"  ✅ {key}: {message}")
            except Exception as e:
                print(f"  ❌ {key}: エラー - {e}")
    
    print("\n✅ 通知翻訳テスト完了")

def main():
    """メイン関数"""
    test_notification_translations()

if __name__ == "__main__":
    main()
