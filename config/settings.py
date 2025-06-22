"""
ゲーム設定クラス

ゲームの各種設定を管理するクラス
"""

from pathlib import Path
from .constants import *


class GameSettings:
    """ゲーム設定を管理するクラス"""
    
    def __init__(self):
        # 基本設定
        self.title = GAME_TITLE
        self.version = GAME_VERSION
        self.debug_mode = False
        self.profile_mode = False
        
        # 画面設定
        self.screen_width = SCREEN_WIDTH
        self.screen_height = SCREEN_HEIGHT
        self.fullscreen = False
        self.fps = TARGET_FPS
        
        # 音声設定
        self.master_volume = 0.7
        self.bgm_volume = 0.5
        self.sfx_volume = 0.8
        self.voice_volume = 0.6
        
        # 言語設定
        self.language = "ja"  # ja: 日本語, en: 英語
        
        # パス設定
        self.project_root = Path(__file__).parent.parent
        self.assets_path = self.project_root / "assets"
        self.data_path = self.project_root / "data"
        self.saves_path = self.project_root / "saves"
        self.exports_path = self.project_root / "exports"
        
        # ゲームプレイ設定
        self.auto_save_interval = 300  # 秒
        self.max_save_slots = 3
        self.tutorial_enabled = True
        
        # デバッグ設定
        self.show_fps = False
        self.show_collision_boxes = False
        self.god_mode = False
    
    def load_from_file(self, config_file: Path):
        """設定ファイルから設定を読み込み"""
        # TODO: JSON形式の設定ファイルから読み込み
        pass
    
    def save_to_file(self, config_file: Path):
        """設定をファイルに保存"""
        # TODO: JSON形式で設定ファイルに保存
        pass
    
    def reset_to_defaults(self):
        """設定をデフォルト値にリセット"""
        self.__init__()
    
    def validate_settings(self):
        """設定値の妥当性をチェック"""
        # 画面サイズの検証
        if self.screen_width < MIN_SCREEN_WIDTH:
            self.screen_width = MIN_SCREEN_WIDTH
        if self.screen_height < MIN_SCREEN_HEIGHT:
            self.screen_height = MIN_SCREEN_HEIGHT
        
        # 音量の検証
        self.master_volume = max(0.0, min(1.0, self.master_volume))
        self.bgm_volume = max(0.0, min(1.0, self.bgm_volume))
        self.sfx_volume = max(0.0, min(1.0, self.sfx_volume))
        self.voice_volume = max(0.0, min(1.0, self.voice_volume))
        
        # FPSの検証
        if self.fps < MIN_FPS:
            self.fps = MIN_FPS
        elif self.fps > MAX_FPS:
            self.fps = MAX_FPS
