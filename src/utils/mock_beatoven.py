"""
Beatoven.ai API のモック実装
開発・テスト用
"""

import os
import time
import random
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class MockBeatovenGenerator:
    """Beatoven.ai API のモック実装"""
    
    def __init__(self):
        self.mock_audio_dir = Path("assets/mock_audio")
        self.mock_audio_dir.mkdir(parents=True, exist_ok=True)
        
        # モック音声ファイルを作成
        self._create_mock_audio_files()
        
        logger.info("MockBeatovenGenerator 初期化完了")
    
    def _create_mock_audio_files(self):
        """モック用の音声ファイルを作成（無音ファイル）"""
        mock_files = [
            # BGM
            "menu_bgm.mp3",
            "residential_bgm.mp3", 
            "forest_bgm.mp3",
            "puzzle_bgm.mp3",
            "victory_bgm.mp3",
            "game_over_bgm.mp3",
            # 効果音
            "pet_found.wav",
            "pet_rescued.wav",
            "button_click.wav",
            "footstep.wav",
            "notification.wav",
            "error.wav",
            "puzzle_solve.wav"
        ]
        
        for filename in mock_files:
            file_path = self.mock_audio_dir / filename
            if not file_path.exists():
                # 簡単な無音ファイルを作成（WAVヘッダー付き）
                self._create_silent_audio(file_path, duration=2.0)
    
    def _create_silent_audio(self, file_path: Path, duration: float = 2.0):
        """無音の音声ファイルを作成"""
        # 簡単なWAVファイルヘッダー（44.1kHz, 16bit, モノラル）
        sample_rate = 44100
        samples = int(sample_rate * duration)
        
        # WAVヘッダー
        wav_header = bytearray([
            # RIFF header
            0x52, 0x49, 0x46, 0x46,  # "RIFF"
            0x00, 0x00, 0x00, 0x00,  # File size (will be filled)
            0x57, 0x41, 0x56, 0x45,  # "WAVE"
            
            # fmt chunk
            0x66, 0x6D, 0x74, 0x20,  # "fmt "
            0x10, 0x00, 0x00, 0x00,  # Chunk size (16)
            0x01, 0x00,              # Audio format (PCM)
            0x01, 0x00,              # Number of channels (1)
            0x44, 0xAC, 0x00, 0x00,  # Sample rate (44100)
            0x88, 0x58, 0x01, 0x00,  # Byte rate
            0x02, 0x00,              # Block align
            0x10, 0x00,              # Bits per sample (16)
            
            # data chunk
            0x64, 0x61, 0x74, 0x61,  # "data"
            0x00, 0x00, 0x00, 0x00,  # Data size (will be filled)
        ])
        
        # 無音データ（16bit = 2bytes per sample）
        silent_data = bytes(samples * 2)
        
        # サイズを計算して設定
        data_size = len(silent_data)
        file_size = len(wav_header) + data_size - 8
        
        # ファイルサイズを設定
        wav_header[4:8] = file_size.to_bytes(4, 'little')
        wav_header[40:44] = data_size.to_bytes(4, 'little')
        
        try:
            with open(file_path, 'wb') as f:
                f.write(wav_header)
                f.write(silent_data)
            logger.debug(f"モック音声ファイル作成: {file_path}")
        except IOError as e:
            logger.error(f"モック音声ファイル作成失敗: {e}")
    
    def generate_bgm(self, 
                     scene_type: str, 
                     mood: str, 
                     duration: int = 60,
                     style: Optional[str] = None,
                     tempo: Optional[str] = None,
                     instruments: Optional[List[str]] = None) -> Optional[bytes]:
        """BGM生成のモック"""
        logger.info(f"モックBGM生成: {scene_type}_{mood} ({duration}秒)")
        
        # 生成時間をシミュレート
        time.sleep(random.uniform(0.5, 2.0))
        
        # 対応するモックファイルを探す
        mock_file = self.mock_audio_dir / f"{scene_type}_bgm.mp3"
        if not mock_file.exists():
            mock_file = self.mock_audio_dir / "menu_bgm.mp3"  # フォールバック
        
        try:
            with open(mock_file, 'rb') as f:
                return f.read()
        except IOError as e:
            logger.error(f"モックBGM読み込み失敗: {e}")
            return None
    
    def generate_sfx(self, 
                     effect_type: str,
                     intensity: str = "medium",
                     duration: float = 2.0,
                     style: Optional[str] = None) -> Optional[bytes]:
        """効果音生成のモック"""
        logger.info(f"モック効果音生成: {effect_type} ({intensity})")
        
        # 生成時間をシミュレート
        time.sleep(random.uniform(0.2, 1.0))
        
        # 対応するモックファイルを探す
        mock_file = self.mock_audio_dir / f"{effect_type}.wav"
        if not mock_file.exists():
            mock_file = self.mock_audio_dir / "notification.wav"  # フォールバック
        
        try:
            with open(mock_file, 'rb') as f:
                return f.read()
        except IOError as e:
            logger.error(f"モック効果音読み込み失敗: {e}")
            return None
    
    def generate_game_audio_set(self) -> Dict[str, bool]:
        """全音声生成のモック"""
        logger.info("モック: 全音声生成開始")
        
        results = {}
        
        # BGM
        bgm_types = ['menu', 'residential', 'forest', 'puzzle', 'victory', 'game_over']
        for bgm_type in bgm_types:
            name = f"{bgm_type}_bgm"
            audio_data = self.generate_bgm(bgm_type, 'default')
            results[name] = audio_data is not None
            
            if audio_data:
                self._save_to_assets(name + '.mp3', audio_data)
        
        # 効果音
        sfx_types = ['pet_found', 'pet_rescued', 'button_click', 'footstep', 'notification', 'error', 'puzzle_solve']
        for sfx_type in sfx_types:
            audio_data = self.generate_sfx(sfx_type)
            results[sfx_type] = audio_data is not None
            
            if audio_data:
                self._save_to_assets(sfx_type + '.wav', audio_data)
        
        return results
    
    def _save_to_assets(self, filename: str, audio_data: bytes):
        """音声データをassetsディレクトリに保存"""
        if filename.endswith('.mp3'):
            asset_path = Path("assets/music") / filename
        else:
            asset_path = Path("assets/sounds") / filename
        
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(asset_path, 'wb') as f:
                f.write(audio_data)
            logger.info(f"モックアセット保存: {asset_path}")
        except IOError as e:
            logger.error(f"モックアセット保存エラー: {e}")
    
    def clear_cache(self):
        """キャッシュクリア（モックでは何もしない）"""
        logger.info("モック: キャッシュクリア（何もしません）")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """キャッシュ情報（モック）"""
        return {
            'cache_count': 0,
            'total_size_mb': 0.0,
            'cache_dir': 'mock'
        }


def get_mock_beatoven_generator() -> MockBeatovenGenerator:
    """MockBeatovenGeneratorのインスタンスを取得"""
    return MockBeatovenGenerator()
