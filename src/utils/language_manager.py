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
                "game_title": "Mystery Pet Rescue",
                
                # ゲーム内UI
                "pets_found": "Pets Found",
                "time_remaining": "Time Remaining",
                "minimap": "Minimap",
                "current_objective": "Current Objective",
                "game_paused": "Game Paused",
                "game_resumed": "Game Resumed",
                "pet_rescued": " rescued!",
                "all_pets_rescued": "All pets rescued!",
                "game_over": "Game Over",
                "victory": "Victory!",
                "find_pets": "Find the pets!",
                "pet_found": "found!",
                "rescue_instruction": "Press E to rescue",
                
                # ペット名（動物名）
                "pet_cat": "Cat",
                "pet_dog": "Dog", 
                "pet_rabbit": "Rabbit",
                "pet_bird": "Bird",
                
                # 結果画面
                "congratulations": "Congratulations!",
                "time_bonus": "Time Bonus",
                "total_score": "Total Score",
                "return_to_menu": "Return to Menu",
                "play_again": "Play Again",
                "quit": "Quit",
                "game_result": "Game Result",
                "game_complete": "Game Complete",
                "time_up": "Time Up",
                "mission_failed": "Mission Failed",
                "pets_rescued": "Pets Rescued",
                "time_taken": "Time Taken",
                "completion_rate": "Completion Rate",
                "rank": "Rank",
                "perfect": "Perfect!",
                "excellent": "Excellent!",
                "good": "Good!",
                "try_again": "Try Again!",
                "returning_to_menu": "Returning to menu...",
                
                # ヒント
                "pets_hiding_hint": "The pets might be hiding near residential areas or parks.",
                "search_buildings_hint": "Try searching around buildings and near trees.",
                "parks_hint": "Midori Park and Kids Plaza are places animals love.",
                
                # 操作説明
                "controls_move": "WASD/Arrow Keys: Move",
                "controls_run": "Shift: Run",
                "controls_interact": "E: Interact",
                "controls_pause": "ESC: Pause",
                "controls_minimap": "M: Toggle Minimap",
                
                # 通知メッセージ
                "time_warning": "Time is running out!",
                "no_lives": "No lives remaining!",
                "time_bonus_message": "Time Bonus: {bonus} points",
                "collision_debug_output": "Collision info output to console",
                "collision_display_on": "Collision Display: ON",
                "collision_display_off": "Collision Display: OFF",
                "objective_completed": "Objective Completed!",
                
                # 敗北画面用
                "pets_rescued_subtitle": "You rescued {count}/{total} pets",
                "pets_rescued_count": "Pets Rescued: {count}/{total}",
                "pet_unit": "",  # 英語では単位なし
                
                # 勝利画面用
                "all_pets_rescued_subtitle": "All pets have been rescued!",
                "pets_found_count": "Pets Found: {count}/{total}",
                "remaining_time_display": "Remaining Time: {time}"
            },
            Language.JAPANESE.value: {
                # メニュー
                "start_game": "ゲーム開始",
                "quit_game": "ゲーム終了",
                "language": "言語",
                "english": "English",
                "japanese": "日本語",
                "game_title": "ミステリー・ペット・レスキュー",
                
                # ゲーム内UI
                "pets_found": "救出したペット",
                "time_remaining": "残り時間",
                "minimap": "ミニマップ",
                "current_objective": "現在の目標",
                "game_paused": "ゲーム一時停止",
                "game_resumed": "ゲーム再開",
                "pet_rescued": "を救出しました！",
                "all_pets_rescued": "すべてのペットを救出しました！",
                "game_over": "ゲームオーバー",
                "victory": "勝利！",
                "find_pets": "ペットを探しましょう！",
                "pet_found": "を見つけました！",
                "rescue_instruction": "Eキーで救出できます",
                
                # ペット名（動物名）
                "pet_cat": "ねこ",
                "pet_dog": "いぬ",
                "pet_rabbit": "うさぎ",
                "pet_bird": "とり",
                
                # 結果画面
                "congratulations": "おめでとうございます！",
                "time_bonus": "タイムボーナス",
                "total_score": "総合スコア",
                "return_to_menu": "メニューに戻る",
                "play_again": "もう一度",
                "quit": "終了",
                "game_result": "ゲーム結果",
                "game_complete": "ゲームクリア",
                "time_up": "時間切れ",
                "mission_failed": "ミッション失敗",
                "pets_rescued": "救出したペット",
                "time_taken": "経過時間",
                "completion_rate": "達成率",
                "rank": "ランク",
                "perfect": "パーフェクト！",
                "excellent": "素晴らしい！",
                "good": "良い！",
                "try_again": "再挑戦！",
                "returning_to_menu": "まもなくメニューに戻ります...",
                
                # ヒント
                "pets_hiding_hint": "ペットたちは住宅街や公園の近くに隠れているかもしれません。",
                "search_buildings_hint": "建物の周りや木の近くを探してみましょう。",
                "parks_hint": "みどり公園とちびっこ広場は動物たちが好む場所です。",
                
                # 操作説明
                "controls_move": "WASD/矢印キー: 移動",
                "controls_run": "Shift: 走る",
                "controls_interact": "E: 相互作用",
                "controls_pause": "ESC: 一時停止",
                "controls_minimap": "M: ミニマップ切り替え",
                
                # 通知メッセージ
                "time_warning": "残り時間が少なくなりました！",
                "no_lives": "ライフが尽きました！",
                "time_bonus_message": "タイムボーナス: {bonus}点",
                "collision_debug_output": "衝突判定情報をコンソールに出力",
                "collision_display_on": "衝突判定表示: ON",
                "collision_display_off": "衝突判定表示: OFF",
                "objective_completed": "目標達成！",
                
                # 敗北画面用
                "pets_rescued_subtitle": "{count}/{total}匹のペットを救出しました",
                "pets_rescued_count": "救出したペット: {count}/{total}匹",
                "pet_unit": "匹",
                
                # 勝利画面用
                "all_pets_rescued_subtitle": "全てのペットを救出しました！",
                "pets_found_count": "発見したペット: {count}/{total}匹",
                "remaining_time_display": "残り時間: {time}"
            }
        }
    
    def set_language(self, language: Language):
        """言語を設定"""
        print(f"🌐 言語設定要求: {language.value}")
        old_lang = self.current_language
        self.current_language = language
        print(f"🔄 言語変更完了: {old_lang.value} → {self.current_language.value}")
        
        # テスト用に現在の翻訳を確認
        test_text = self.get_text("start_game")
        print(f"🧪 テスト翻訳 'start_game': {test_text}")
    
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
    
    def get_pet_name(self, pet_type: str) -> str:
        """ペットタイプから動物名を取得"""
        pet_key = f"pet_{pet_type.lower()}"
        return self.get_text(pet_key)
    
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
