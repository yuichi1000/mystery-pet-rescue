"""
シーン管理システム

ゲームの各シーン（画面）を管理
"""

import pygame
from typing import Dict, Optional, Any
from abc import ABC, abstractmethod

from config.settings import GameSettings
from config.constants import *


class Scene(ABC):
    """シーンの基底クラス"""
    
    def __init__(self, scene_manager: 'SceneManager'):
        self.scene_manager = scene_manager
        self.settings = scene_manager.settings
    
    @abstractmethod
    def update(self):
        """シーンの更新処理"""
        pass
    
    @abstractmethod
    def render(self, screen: pygame.Surface):
        """シーンの描画処理"""
        pass
    
    def on_enter(self):
        """シーンに入る時の処理"""
        pass
    
    def on_exit(self):
        """シーンから出る時の処理"""
        pass


class TitleScene(Scene):
    """タイトルシーン"""
    
    def __init__(self, scene_manager: 'SceneManager'):
        super().__init__(scene_manager)
        self.font = pygame.font.Font(None, 72)
        self.title_text = self.font.render(GAME_TITLE, True, COLOR_WHITE)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.subtitle_text = self.subtitle_font.render("Press SPACE to start", True, COLOR_LIGHT_GRAY)
    
    def update(self):
        """更新処理"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE]:
            self.scene_manager.change_scene(SCENE_MAIN_MENU)
    
    def render(self, screen: pygame.Surface):
        """描画処理"""
        screen.fill(COLOR_DARK_GRAY)
        
        # タイトルを中央に描画
        title_rect = self.title_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 - 50))
        screen.blit(self.title_text, title_rect)
        
        # サブタイトルを描画
        subtitle_rect = self.subtitle_text.get_rect(center=(screen.get_width()//2, screen.get_height()//2 + 50))
        screen.blit(self.subtitle_text, subtitle_rect)


class MainMenuScene(Scene):
    """メインメニューシーン"""
    
    def __init__(self, scene_manager: 'SceneManager'):
        super().__init__(scene_manager)
        self.font = pygame.font.Font(None, 48)
        self.menu_items = ["ゲーム開始", "ペット図鑑", "設定", "終了"]
        self.selected_index = 0
    
    def update(self):
        """更新処理"""
        keys = pygame.key.get_pressed()
        # TODO: メニュー選択処理を実装
    
    def render(self, screen: pygame.Surface):
        """描画処理"""
        screen.fill(COLOR_GRAY)
        
        # メニュー項目を描画
        for i, item in enumerate(self.menu_items):
            color = COLOR_YELLOW if i == self.selected_index else COLOR_WHITE
            text = self.font.render(item, True, color)
            y = 200 + i * 80
            text_rect = text.get_rect(center=(screen.get_width()//2, y))
            screen.blit(text, text_rect)


class GameWorldScene(Scene):
    """ゲーム世界シーン"""
    
    def __init__(self, scene_manager: 'SceneManager'):
        super().__init__(scene_manager)
        # TODO: ゲーム世界の初期化
    
    def update(self):
        """更新処理"""
        # TODO: ゲーム世界の更新処理
        pass
    
    def render(self, screen: pygame.Surface):
        """描画処理"""
        screen.fill(COLOR_GREEN)
        # TODO: ゲーム世界の描画処理


class SceneManager:
    """シーン管理クラス"""
    
    def __init__(self, settings: GameSettings):
        self.settings = settings
        self.scenes: Dict[str, Scene] = {}
        self.current_scene: Optional[Scene] = None
        self.current_scene_name: Optional[str] = None
        
        # シーンを登録
        self._register_scenes()
        
        # 初期シーンを設定
        self.change_scene(SCENE_TITLE)
    
    def _register_scenes(self):
        """シーンを登録"""
        self.scenes[SCENE_TITLE] = TitleScene(self)
        self.scenes[SCENE_MAIN_MENU] = MainMenuScene(self)
        self.scenes[SCENE_GAME_WORLD] = GameWorldScene(self)
    
    def change_scene(self, scene_name: str, **kwargs):
        """シーンを変更"""
        if scene_name not in self.scenes:
            print(f"警告: シーン '{scene_name}' が見つかりません")
            return
        
        # 現在のシーンから退出
        if self.current_scene:
            self.current_scene.on_exit()
        
        # 新しいシーンに変更
        self.current_scene = self.scenes[scene_name]
        self.current_scene_name = scene_name
        self.current_scene.on_enter()
        
        if self.settings.debug_mode:
            print(f"シーンを変更: {scene_name}")
    
    def update(self):
        """現在のシーンを更新"""
        if self.current_scene:
            self.current_scene.update()
    
    def render(self, screen: pygame.Surface):
        """現在のシーンを描画"""
        if self.current_scene:
            self.current_scene.render(screen)
    
    def get_current_scene_name(self) -> Optional[str]:
        """現在のシーン名を取得"""
        return self.current_scene_name
