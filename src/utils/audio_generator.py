"""
統合音声生成システム
実際のBeatoven.ai APIとモックAPIを切り替え可能
"""

import os
from typing import Optional, Dict, Any, List
from dotenv import load_dotenv
import logging

# 環境変数読み込み
load_dotenv()

logger = logging.getLogger(__name__)

class AudioGenerator:
    """統合音声生成システム"""
    
    def __init__(self):
        self.use_mock = os.getenv('USE_MOCK_API', 'False').lower() == 'true'
        self.api_key = os.getenv('BEATOVEN_API_KEY')
        
        # APIキーがない場合は自動的にモックを使用
        if not self.api_key and not self.use_mock:
            logger.warning("BEATOVEN_API_KEY が設定されていません。モックAPIを使用します。")
            self.use_mock = True
        
        # 適切なジェネレーターを初期化
        if self.use_mock:
            from .mock_beatoven import get_mock_beatoven_generator
            self.generator = get_mock_beatoven_generator()
            logger.info("モックBeatoven.ai APIを使用")
        else:
            from .beatoven_generator import get_beatoven_generator
            self.generator = get_beatoven_generator()
            logger.info("実際のBeatoven.ai APIを使用")
    
    def generate_bgm(self, 
                     scene_type: str, 
                     mood: str, 
                     duration: int = 60,
                     **kwargs) -> Optional[bytes]:
        """BGMを生成"""
        return self.generator.generate_bgm(scene_type, mood, duration, **kwargs)
    
    def generate_sfx(self, 
                     effect_type: str,
                     intensity: str = "medium",
                     duration: float = 2.0,
                     **kwargs) -> Optional[bytes]:
        """効果音を生成"""
        return self.generator.generate_sfx(effect_type, intensity, duration, **kwargs)
    
    def generate_game_audio_set(self) -> Dict[str, bool]:
        """ゲームに必要な全音声を生成"""
        return self.generator.generate_game_audio_set()
    
    def clear_cache(self):
        """キャッシュをクリア"""
        if hasattr(self.generator, 'clear_cache'):
            self.generator.clear_cache()
    
    def get_cache_info(self) -> Dict[str, Any]:
        """キャッシュ情報を取得"""
        if hasattr(self.generator, 'get_cache_info'):
            return self.generator.get_cache_info()
        return {'cache_count': 0, 'total_size_mb': 0.0, 'cache_dir': 'none'}
    
    def is_using_mock(self) -> bool:
        """モックAPIを使用しているかチェック"""
        return self.use_mock


# グローバルインスタンス
_audio_generator: Optional[AudioGenerator] = None

def get_audio_generator() -> AudioGenerator:
    """AudioGeneratorのシングルトンインスタンスを取得"""
    global _audio_generator
    if _audio_generator is None:
        _audio_generator = AudioGenerator()
    return _audio_generator
