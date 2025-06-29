"""
音響システム
BGM・効果音の管理と再生
"""

import pygame
import os
from typing import Dict, Optional, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class AudioSystem:
    """音響システムクラス"""
    
    def __init__(self):
        # Web環境チェック
        self.is_web = self._check_web_environment()
        
        # Pygameミキサーの初期化（Web対応）
        if not pygame.mixer.get_init():
            if self.is_web:
                # Web環境では軽量設定
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
                print("🌐 Web環境用音声初期化")
            else:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
                print("🖥️ デスクトップ環境用音声初期化")
        
        # 音量設定
        self.master_volume = 1.0
        self.bgm_volume = 0.7 if not self.is_web else 0.5  # Web版は音量を下げる
        self.sfx_volume = 0.8 if not self.is_web else 0.6
        
        # BGMトラック管理
        self.bgm_tracks: Dict[str, str] = {}
        self.current_bgm: Optional[str] = None
        self.bgm_fade_duration = 1000 if not self.is_web else 500  # Web版は短縮
        
        # 効果音管理
        self.sound_effects: Dict[str, pygame.mixer.Sound] = {}
        self.sound_channels: List[pygame.mixer.Channel] = []
        
        # アセットパス（Web対応）
        if self.is_web:
            from src.utils.web_utils import get_web_safe_path
            self.music_path = Path(get_web_safe_path("assets/music"))
            self.sfx_path = Path(get_web_safe_path("assets/sounds"))
        else:
            self.music_path = Path("assets/music")
            self.sfx_path = Path("assets/sounds")
        
        # 初期化
        self._load_audio_assets()
        self._setup_channels()
        
        logger.info(f"AudioSystem初期化完了 ({'Web版' if self.is_web else 'デスクトップ版'})")
    
    def _check_web_environment(self) -> bool:
        """Web環境かチェック"""
        try:
            from src.utils.web_utils import is_web_environment
            return is_web_environment()
        except ImportError:
            import os
            return os.environ.get('WEB_VERSION') == '1'
    
    def _setup_channels(self):
        """音声チャンネルを設定"""
        # 効果音用チャンネルを確保
        pygame.mixer.set_num_channels(16)
        for i in range(8):  # 8チャンネルを効果音用に確保
            channel = pygame.mixer.Channel(i)
            self.sound_channels.append(channel)
    
    def _load_audio_assets(self):
        """音声アセットを読み込み"""
        # BGMファイルを検索・登録
        if self.music_path.exists():
            for music_file in self.music_path.glob("*.mp3"):
                track_name = music_file.stem
                self.bgm_tracks[track_name] = str(music_file)
                logger.info(f"BGM登録: {track_name} -> {music_file}")
            
            for music_file in self.music_path.glob("*.ogg"):
                track_name = music_file.stem
                self.bgm_tracks[track_name] = str(music_file)
                logger.info(f"BGM登録: {track_name} -> {music_file}")
        
        # 効果音ファイルを読み込み
        if self.sfx_path.exists():
            for sfx_file in self.sfx_path.glob("*.wav"):
                try:
                    sound_name = sfx_file.stem
                    sound = pygame.mixer.Sound(str(sfx_file))
                    sound.set_volume(self.sfx_volume * self.master_volume)
                    self.sound_effects[sound_name] = sound
                    logger.info(f"効果音読み込み: {sound_name}")
                except pygame.error as e:
                    logger.error(f"効果音読み込み失敗: {sfx_file} - {e}")
            
            for sfx_file in self.sfx_path.glob("*.ogg"):
                try:
                    sound_name = sfx_file.stem
                    sound = pygame.mixer.Sound(str(sfx_file))
                    sound.set_volume(self.sfx_volume * self.master_volume)
                    self.sound_effects[sound_name] = sound
                    logger.info(f"効果音読み込み: {sound_name}")
                except pygame.error as e:
                    logger.error(f"効果音読み込み失敗: {sfx_file} - {e}")
            
            # MP3ファイルも読み込み
            for sfx_file in self.sfx_path.glob("*.mp3"):
                try:
                    sound_name = sfx_file.stem
                    sound = pygame.mixer.Sound(str(sfx_file))
                    sound.set_volume(self.sfx_volume * self.master_volume)
                    self.sound_effects[sound_name] = sound
                    logger.info(f"効果音読み込み: {sound_name}")
                except pygame.error as e:
                    logger.error(f"効果音読み込み失敗: {sfx_file} - {e}")
    
    def play_bgm(self, track_name: str, loop: bool = True, fade_in: bool = True):
        """BGMを再生"""
        if track_name not in self.bgm_tracks:
            logger.warning(f"BGMトラック未発見: {track_name}")
            return False
        
        # 同じBGMが再生中の場合はスキップ
        if self.current_bgm == track_name and pygame.mixer.music.get_busy():
            return True
        
        try:
            # 現在のBGMを停止
            if pygame.mixer.music.get_busy():
                if fade_in:
                    pygame.mixer.music.fadeout(self.bgm_fade_duration)
                else:
                    pygame.mixer.music.stop()
            
            # 新しいBGMを読み込み・再生
            track_path = self.bgm_tracks[track_name]
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.set_volume(self.bgm_volume * self.master_volume)
            
            loops = -1 if loop else 0
            if fade_in:
                pygame.mixer.music.play(loops, fade_ms=self.bgm_fade_duration)
            else:
                pygame.mixer.music.play(loops)
            
            self.current_bgm = track_name
            logger.info(f"BGM再生開始: {track_name}")
            return True
            
        except pygame.error as e:
            logger.error(f"BGM再生失敗: {track_name} - {e}")
            return False
    
    def stop_bgm(self, fade_out: bool = True):
        """BGMを停止"""
        if pygame.mixer.music.get_busy():
            if fade_out:
                pygame.mixer.music.fadeout(self.bgm_fade_duration)
            else:
                pygame.mixer.music.stop()
            self.current_bgm = None
            logger.info("BGM停止")
    
    def pause_bgm(self):
        """BGMを一時停止"""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            logger.info("BGM一時停止")
    
    def resume_bgm(self):
        """BGMを再開"""
        pygame.mixer.music.unpause()
        logger.info("BGM再開")
    
    def play_sfx(self, sound_name: str, volume: float = 1.0) -> bool:
        """
        効果音を再生（1回のみ、ループなし）
        
        Args:
            sound_name: 効果音名
            volume: 音量 (0.0-1.0)
        """
        if sound_name not in self.sound_effects:
            logger.warning(f"効果音未発見: {sound_name}")
            return False
        
        try:
            sound = self.sound_effects[sound_name]
            
            # 重複再生チェック
            current_time = pygame.time.get_ticks()
            recent_sounds = getattr(self, '_recent_sounds', {})
            
            # 同じ効果音が200ms以内に再生されていたらスキップ
            if sound_name in recent_sounds:
                if current_time - recent_sounds[sound_name] < 200:
                    logger.debug(f"効果音重複スキップ: {sound_name}")
                    return False
            
            # 再生記録を更新
            if not hasattr(self, '_recent_sounds'):
                self._recent_sounds = {}
            self._recent_sounds[sound_name] = current_time
            
            # 空いているチャンネルを探す
            channel = None
            for ch in self.sound_channels:
                if not ch.get_busy():
                    channel = ch
                    break
            
            # 全チャンネルが使用中の場合は最初のチャンネルを使用
            if channel is None:
                channel = self.sound_channels[0]
                channel.stop()  # 既存の音を停止
            
            # 音量調整
            adjusted_volume = volume * self.sfx_volume * self.master_volume
            sound.set_volume(adjusted_volume)
            
            # 再生（必ず1回のみ、loops=0）
            channel.play(sound, loops=0)
            logger.debug(f"効果音再生: {sound_name} (1回のみ)")
            return True
            
        except pygame.error as e:
            logger.error(f"効果音再生失敗: {sound_name} - {e}")
            return False
    
    def stop_all_sfx(self):
        """全ての効果音を停止"""
        try:
            for channel in self.sound_channels:
                if channel.get_busy():
                    channel.stop()
            logger.debug("全効果音停止")
        except Exception as e:
            logger.error(f"効果音停止失敗: {e}")
    
    def stop_sfx(self, sound_name: str):
        """特定の効果音を停止"""
        try:
            # 簡易的に全チャンネルをチェック（実際は音声識別が必要）
            for channel in self.sound_channels:
                if channel.get_busy():
                    channel.stop()
            logger.debug(f"効果音停止: {sound_name}")
        except Exception as e:
            logger.error(f"効果音停止失敗: {e}")
    
    def set_master_volume(self, volume: float):
        """マスター音量を設定 (0.0-1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
        self._update_volumes()
        logger.info(f"マスター音量設定: {self.master_volume}")
    
    def set_bgm_volume(self, volume: float):
        """BGM音量を設定 (0.0-1.0)"""
        self.bgm_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.bgm_volume * self.master_volume)
        logger.info(f"BGM音量設定: {self.bgm_volume}")
    
    def set_sfx_volume(self, volume: float):
        """効果音音量を設定 (0.0-1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
        self._update_sfx_volumes()
        logger.info(f"効果音音量設定: {self.sfx_volume}")
    
    def _update_volumes(self):
        """全音量を更新"""
        # BGM音量更新
        pygame.mixer.music.set_volume(self.bgm_volume * self.master_volume)
        
        # 効果音音量更新
        self._update_sfx_volumes()
    
    def _update_sfx_volumes(self):
        """効果音音量を更新"""
        for sound in self.sound_effects.values():
            sound.set_volume(self.sfx_volume * self.master_volume)
    
    def get_bgm_list(self) -> List[str]:
        """利用可能なBGMトラック一覧を取得"""
        return list(self.bgm_tracks.keys())
    
    def get_sfx_list(self) -> List[str]:
        """利用可能な効果音一覧を取得"""
        return list(self.sound_effects.keys())
    
    def is_bgm_playing(self) -> bool:
        """BGMが再生中かチェック"""
        return pygame.mixer.music.get_busy()
    
    def get_current_bgm(self) -> Optional[str]:
        """現在再生中のBGMトラック名を取得"""
        return self.current_bgm if self.is_bgm_playing() else None
    
    def cleanup(self):
        """リソースをクリーンアップ"""
        self.stop_bgm(fade_out=False)
        for channel in self.sound_channels:
            channel.stop()
        logger.info("AudioSystem クリーンアップ完了")


# グローバルインスタンス
_audio_system: Optional[AudioSystem] = None

def get_audio_system() -> AudioSystem:
    """AudioSystemのシングルトンインスタンスを取得"""
    global _audio_system
    if _audio_system is None:
        _audio_system = AudioSystem()
    return _audio_system

def cleanup_audio_system():
    """AudioSystemをクリーンアップ"""
    global _audio_system
    if _audio_system is not None:
        _audio_system.cleanup()
        _audio_system = None
