"""
メインゲームループ

ゲームの中核となるループ処理を管理
"""

import pygame
import sys
from typing import Optional

from config.settings import GameSettings
from config.constants import *
from .scene_manager import SceneManager
from .input_handler import InputHandler


class GameLoop:
    """メインゲームループクラス"""
    
    def __init__(self, settings: GameSettings):
        """
        ゲームループを初期化
        
        Args:
            settings: ゲーム設定
        """
        self.settings = settings
        self.running = False
        self.clock = None
        self.screen = None
        self.scene_manager = None
        self.input_handler = None
        
        # Pygameを初期化
        self._initialize_pygame()
    
    def _initialize_pygame(self):
        """Pygameを初期化"""
        pygame.init()
        pygame.mixer.init(
            frequency=AUDIO_FREQUENCY,
            size=AUDIO_SIZE,
            channels=AUDIO_CHANNELS,
            buffer=AUDIO_BUFFER
        )
        
        # 画面を作成
        if self.settings.fullscreen:
            self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height),
                pygame.FULLSCREEN
            )
        else:
            self.screen = pygame.display.set_mode(
                (self.settings.screen_width, self.settings.screen_height)
            )
        
        pygame.display.set_caption(self.settings.title)
        
        # クロックを作成
        self.clock = pygame.time.Clock()
        
        # マネージャーを初期化
        self.scene_manager = SceneManager(self.settings)
        self.input_handler = InputHandler()
    
    def run(self):
        """メインループを実行"""
        self.running = True
        
        try:
            while self.running:
                # イベント処理
                self._handle_events()
                
                # 更新処理
                self._update()
                
                # 描画処理
                self._render()
                
                # FPS制御
                self.clock.tick(self.settings.fps)
                
        except Exception as e:
            print(f"ゲームループでエラーが発生: {e}")
            if self.settings.debug_mode:
                import traceback
                traceback.print_exc()
        finally:
            self._cleanup()
    
    def _handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                else:
                    self.input_handler.handle_key_down(event.key)
            elif event.type == pygame.KEYUP:
                self.input_handler.handle_key_up(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.input_handler.handle_mouse_down(event.button, event.pos)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.input_handler.handle_mouse_up(event.button, event.pos)
            elif event.type == pygame.MOUSEMOTION:
                self.input_handler.handle_mouse_motion(event.pos)
    
    def _update(self):
        """更新処理"""
        # 現在のシーンを更新
        if self.scene_manager:
            self.scene_manager.update()
        
        # 入力状態を更新
        if self.input_handler:
            self.input_handler.update()
    
    def _render(self):
        """描画処理"""
        # 画面をクリア
        self.screen.fill(COLOR_BLACK)
        
        # 現在のシーンを描画
        if self.scene_manager:
            self.scene_manager.render(self.screen)
        
        # デバッグ情報を描画
        if self.settings.debug_mode:
            self._render_debug_info()
        
        # 画面を更新
        pygame.display.flip()
    
    def _render_debug_info(self):
        """デバッグ情報を描画"""
        if self.settings.show_fps:
            fps = self.clock.get_fps()
            font = pygame.font.Font(None, 36)
            fps_text = font.render(f"FPS: {fps:.1f}", True, COLOR_WHITE)
            self.screen.blit(fps_text, (10, 10))
    
    def _cleanup(self):
        """クリーンアップ処理"""
        pygame.quit()
        print("ゲームを終了しました")
    
    def quit(self):
        """ゲームを終了"""
        self.running = False
