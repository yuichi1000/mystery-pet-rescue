"""
言語管理システム
"""

import json
import os
from typing import Dict, Any
from enum import Enum

class Language(Enum):
    """サポートされている言語"""
    ENGLISH = "en"
    JAPANESE = "ja"

class LanguageManager:
    """言語管理クラス"""
    
    def __init__(self):
        self.current_language = Language.ENGLISH  # デフォルトは英語
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()
    
    def _load_translations(self):
        """翻訳データを読み込み"""
        # 基本的な翻訳データを直接定義
        self.translations = {
            Language.ENGLISH.value: {
                # メニュー
                "start_game": "Start Game",
                "quit_game": "Quit Game",
                "language": "Language",
                "english": "English",
                "japanese": "日本語",
                
                # ゲーム内
                "pets_found": "Pets Found",
                "time_remaining": "Time Remaining",
                "game_paused": "Game Paused",
                "game_resumed": "Game Resumed",
                "pet_rescued": "Pet Rescued!",
                "all_pets_rescued": "All pets rescued!",
                "game_over": "Game Over",
                "victory": "Victory!",
                "find_pets": "Find the pets!",
                
                # 結果画面
                "congratulations": "Congratulations!",
                "time_bonus": "Time Bonus",
                "total_score": "Total Score",
                "return_to_menu": "Return to Menu",
                
                # ヒント
                "pets_hiding_hint": "The pets might be hiding near residential areas or parks.",
                "search_buildings_hint": "Try searching around buildings and near trees.",
                "parks_hint": "Midori Park and Kids Plaza are places animals love."
            },
            Language.JAPANESE.value: {
                # メニュー
                "start_game": "ゲーム開始",
                "quit_game": "ゲーム終了",
                "language": "言語",
                "english": "English",
                "japanese": "日本語",
                
                # ゲーム内
                "pets_found": "救出したペット",
                "time_remaining": "残り時間",
                "game_paused": "ゲーム一時停止",
                "game_resumed": "ゲーム再開",
                "pet_rescued": "ペットを救出しました！",
                "all_pets_rescued": "すべてのペットを救出しました！",
                "game_over": "ゲームオーバー",
                "victory": "勝利！",
                "find_pets": "ペットを探しましょう！",
                
                # 結果画面
                "congratulations": "おめでとうございます！",
                "time_bonus": "タイムボーナス",
                "total_score": "総合スコア",
                "return_to_menu": "メニューに戻る",
                
                # ヒント
                "pets_hiding_hint": "ペットたちは住宅街や公園の近くに隠れているかもしれません。",
                "search_buildings_hint": "建物の周りや木の近くを探してみましょう。",
                "parks_hint": "みどり公園とちびっこ広場は動物たちが好む場所です。"
            }
        }
    
    def set_language(self, language: Language):
        """言語を設定"""
        self.current_language = language
        print(f"🌐 言語を{language.value}に変更しました")
    
    def get_current_language(self) -> Language:
        """現在の言語を取得"""
        return self.current_language
    
    def get_text(self, key: str) -> str:
        """指定されたキーの翻訳テキストを取得"""
        lang_code = self.current_language.value
        if lang_code in self.translations and key in self.translations[lang_code]:
            return self.translations[lang_code][key]
        
        # フォールバック: 英語を試す
        if Language.ENGLISH.value in self.translations and key in self.translations[Language.ENGLISH.value]:
            return self.translations[Language.ENGLISH.value][key]
        
        # 最終フォールバック: キー名をそのまま返す
        return key
    
    def get_language_display_name(self, language: Language) -> str:
        """言語の表示名を取得"""
        if language == Language.ENGLISH:
            return self.get_text("english")
        elif language == Language.JAPANESE:
            return self.get_text("japanese")
        return language.value

# グローバルインスタンス
_language_manager = None

def get_language_manager() -> LanguageManager:
    """言語マネージャーのシングルトンインスタンスを取得"""
    global _language_manager
    if _language_manager is None:
        _language_manager = LanguageManager()
    return _language_manager

def get_text(key: str) -> str:
    """翻訳テキストを取得するヘルパー関数"""
    return get_language_manager().get_text(key)
