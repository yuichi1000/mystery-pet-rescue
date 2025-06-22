"""
言語管理システム

多言語対応のテキスト管理
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional


class LanguageManager:
    """言語管理クラス"""
    
    def __init__(self, locale_path: Path):
        """
        言語管理システムを初期化
        
        Args:
            locale_path: 言語ファイルのディレクトリパス
        """
        self.locale_path = locale_path
        self.current_language = "ja"
        self.fallback_language = "ja"
        self.translations: Dict[str, Dict[str, str]] = {}
        
        # 利用可能な言語
        self.available_languages = {
            "ja": "日本語",
            "en": "English"
        }
        
        # 言語ファイルを読み込み
        self._load_all_languages()
    
    def _load_all_languages(self):
        """全ての言語ファイルを読み込み"""
        for lang_code in self.available_languages.keys():
            self._load_language(lang_code)
    
    def _load_language(self, language_code: str) -> bool:
        """
        指定言語のファイルを読み込み
        
        Args:
            language_code: 言語コード (ja, en)
            
        Returns:
            読み込み成功時True
        """
        try:
            lang_file = self.locale_path / f"{language_code}_JP.json" if language_code == "ja" else self.locale_path / f"{language_code}_US.json"
            
            if not lang_file.exists():
                print(f"言語ファイルが見つかりません: {lang_file}")
                return False
            
            with open(lang_file, 'r', encoding='utf-8') as f:
                self.translations[language_code] = json.load(f)
            
            print(f"言語ファイルを読み込みました: {language_code}")
            return True
            
        except Exception as e:
            print(f"言語ファイル読み込みエラー ({language_code}): {e}")
            return False
    
    def set_language(self, language_code: str) -> bool:
        """
        現在の言語を設定
        
        Args:
            language_code: 言語コード
            
        Returns:
            設定成功時True
        """
        if language_code not in self.available_languages:
            print(f"サポートされていない言語: {language_code}")
            return False
        
        if language_code not in self.translations:
            if not self._load_language(language_code):
                return False
        
        self.current_language = language_code
        print(f"言語を変更しました: {self.available_languages[language_code]}")
        return True
    
    def get_text(self, key: str, **kwargs) -> str:
        """
        指定キーのテキストを取得
        
        Args:
            key: テキストキー (例: "menu.start_game")
            **kwargs: テキスト内の置換変数
            
        Returns:
            ローカライズされたテキスト
        """
        # 現在の言語から取得を試行
        text = self._get_text_from_language(self.current_language, key)
        
        # 見つからない場合はフォールバック言語から取得
        if text is None and self.current_language != self.fallback_language:
            text = self._get_text_from_language(self.fallback_language, key)
        
        # それでも見つからない場合はキーをそのまま返す
        if text is None:
            text = f"[{key}]"
            print(f"テキストキーが見つかりません: {key}")
        
        # 変数を置換
        if kwargs:
            try:
                text = text.format(**kwargs)
            except KeyError as e:
                print(f"テキスト置換エラー ({key}): {e}")
        
        return text
    
    def _get_text_from_language(self, language_code: str, key: str) -> Optional[str]:
        """
        指定言語からテキストを取得
        
        Args:
            language_code: 言語コード
            key: テキストキー
            
        Returns:
            テキスト（見つからない場合はNone）
        """
        if language_code not in self.translations:
            return None
        
        # ネストしたキーに対応 (例: "menu.start_game")
        keys = key.split('.')
        current = self.translations[language_code]
        
        try:
            for k in keys:
                current = current[k]
            return str(current)
        except (KeyError, TypeError):
            return None
    
    def get_current_language(self) -> str:
        """現在の言語コードを取得"""
        return self.current_language
    
    def get_current_language_name(self) -> str:
        """現在の言語名を取得"""
        return self.available_languages.get(self.current_language, "Unknown")
    
    def get_available_languages(self) -> Dict[str, str]:
        """利用可能な言語一覧を取得"""
        return self.available_languages.copy()
    
    def is_language_loaded(self, language_code: str) -> bool:
        """指定言語が読み込まれているかチェック"""
        return language_code in self.translations
    
    def reload_current_language(self) -> bool:
        """現在の言語を再読み込み"""
        return self._load_language(self.current_language)
    
    def get_language_stats(self) -> Dict[str, Any]:
        """言語統計情報を取得"""
        stats = {}
        
        for lang_code, translations in self.translations.items():
            stats[lang_code] = {
                "name": self.available_languages.get(lang_code, "Unknown"),
                "key_count": self._count_keys(translations),
                "loaded": True
            }
        
        return stats
    
    def _count_keys(self, data: Dict[str, Any]) -> int:
        """辞書内のキー数を再帰的にカウント"""
        count = 0
        for value in data.values():
            if isinstance(value, dict):
                count += self._count_keys(value)
            else:
                count += 1
        return count
    
    # よく使用されるテキストのショートカット
    def get_menu_text(self, key: str) -> str:
        """メニューテキストを取得"""
        return self.get_text(f"menu.{key}")
    
    def get_ui_text(self, key: str) -> str:
        """UIテキストを取得"""
        return self.get_text(f"ui.{key}")
    
    def get_game_text(self, key: str) -> str:
        """ゲームテキストを取得"""
        return self.get_text(f"game.{key}")
    
    def get_dialog_text(self, key: str) -> str:
        """ダイアログテキストを取得"""
        return self.get_text(f"dialog.{key}")
    
    def get_pet_text(self, key: str) -> str:
        """ペット関連テキストを取得"""
        return self.get_text(f"pet.{key}")
    
    def get_error_text(self, key: str) -> str:
        """エラーテキストを取得"""
        return self.get_text(f"error.{key}")
