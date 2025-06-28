#!/usr/bin/env python3
"""
多言語対応テスト
言語切り替えとペット名の表示をテスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.language_manager import get_language_manager, Language
from src.entities.pet import Pet, PetData, PetType

def test_language_switching():
    """言語切り替えテスト"""
    print("🌐 多言語対応テスト開始")
    print("=" * 50)
    
    # 言語マネージャーを取得
    lang_manager = get_language_manager()
    
    # テスト用ペットデータを作成
    test_pets = [
        PetData("dog_001", "dog", PetType.DOG, "friendly", "common", "犬"),
        PetData("cat_001", "cat", PetType.CAT, "shy", "common", "猫"),
        PetData("rabbit_001", "rabbit", PetType.RABBIT, "gentle", "uncommon", "うさぎ"),
        PetData("bird_001", "bird", PetType.BIRD, "active", "rare", "鳥")
    ]
    
    # ペットオブジェクトを作成
    pets = [Pet(pet_data, 0, 0) for pet_data in test_pets]
    
    # 各言語でテスト
    for language in [Language.ENGLISH, Language.JAPANESE]:
        print(f"\n📝 言語: {language.value}")
        print("-" * 30)
        
        # 言語を設定
        lang_manager.set_language(language)
        
        # UI要素のテスト
        print("UI要素:")
        ui_keys = [
            "game_title", "start_game", "quit_game", "language",
            "pets_found", "time_remaining", "minimap",
            "congratulations", "play_again", "return_to_menu"
        ]
        
        for key in ui_keys:
            text = lang_manager.get_text(key)
            print(f"  {key}: '{text}'")
        
        # ペット名のテスト
        print("\nペット名:")
        for pet in pets:
            display_name = pet.get_display_name()
            print(f"  {pet.data.pet_type.value}: '{display_name}'")
        
        print()

def test_pet_name_consistency():
    """ペット名の一貫性テスト"""
    print("🐾 ペット名一貫性テスト")
    print("=" * 50)
    
    lang_manager = get_language_manager()
    
    # 各ペットタイプをテスト
    pet_types = ["dog", "cat", "rabbit", "bird"]
    
    for pet_type in pet_types:
        print(f"\n🔍 {pet_type.upper()}:")
        
        # 各言語での表示名を確認
        for language in [Language.ENGLISH, Language.JAPANESE]:
            lang_manager.set_language(language)
            display_name = lang_manager.get_pet_name(pet_type)
            print(f"  {language.value}: '{display_name}'")

def main():
    """メイン関数"""
    try:
        test_language_switching()
        test_pet_name_consistency()
        print("✅ 多言語対応テスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
