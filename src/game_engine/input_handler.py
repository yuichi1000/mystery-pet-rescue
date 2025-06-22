"""
入力処理システム

キーボードとマウスの入力を管理
"""

import pygame
from typing import Dict, Set, Tuple, Optional
from config.constants import *


class InputHandler:
    """入力処理クラス"""
    
    def __init__(self):
        # キー状態管理
        self.keys_pressed: Set[int] = set()
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()
        
        # マウス状態管理
        self.mouse_pos: Tuple[int, int] = (0, 0)
        self.mouse_buttons_pressed: Set[int] = set()
        self.mouse_buttons_just_pressed: Set[int] = set()
        self.mouse_buttons_just_released: Set[int] = set()
        
        # ゲーム用キーマッピング
        self.key_mapping = {
            pygame.K_UP: KEY_UP,
            pygame.K_w: KEY_UP,
            pygame.K_DOWN: KEY_DOWN,
            pygame.K_s: KEY_DOWN,
            pygame.K_LEFT: KEY_LEFT,
            pygame.K_a: KEY_LEFT,
            pygame.K_RIGHT: KEY_RIGHT,
            pygame.K_d: KEY_RIGHT,
            pygame.K_SPACE: KEY_ACTION,
            pygame.K_RETURN: KEY_ACTION,
            pygame.K_ESCAPE: KEY_CANCEL,
            pygame.K_BACKSPACE: KEY_CANCEL,
            pygame.K_TAB: KEY_MENU,
            pygame.K_i: KEY_INVENTORY,
        }
    
    def handle_key_down(self, key: int):
        """キー押下処理"""
        if key not in self.keys_pressed:
            self.keys_just_pressed.add(key)
        self.keys_pressed.add(key)
    
    def handle_key_up(self, key: int):
        """キー離上処理"""
        if key in self.keys_pressed:
            self.keys_just_released.add(key)
            self.keys_pressed.remove(key)
    
    def handle_mouse_down(self, button: int, pos: Tuple[int, int]):
        """マウスボタン押下処理"""
        self.mouse_pos = pos
        if button not in self.mouse_buttons_pressed:
            self.mouse_buttons_just_pressed.add(button)
        self.mouse_buttons_pressed.add(button)
    
    def handle_mouse_up(self, button: int, pos: Tuple[int, int]):
        """マウスボタン離上処理"""
        self.mouse_pos = pos
        if button in self.mouse_buttons_pressed:
            self.mouse_buttons_just_released.add(button)
            self.mouse_buttons_pressed.remove(button)
    
    def handle_mouse_motion(self, pos: Tuple[int, int]):
        """マウス移動処理"""
        self.mouse_pos = pos
    
    def update(self):
        """入力状態を更新（フレーム終了時に呼び出し）"""
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        self.mouse_buttons_just_pressed.clear()
        self.mouse_buttons_just_released.clear()
    
    # キー状態チェック関数
    def is_key_pressed(self, key: int) -> bool:
        """キーが押されているかチェック"""
        return key in self.keys_pressed
    
    def is_key_just_pressed(self, key: int) -> bool:
        """キーが今フレームで押されたかチェック"""
        return key in self.keys_just_pressed
    
    def is_key_just_released(self, key: int) -> bool:
        """キーが今フレームで離されたかチェック"""
        return key in self.keys_just_released
    
    # ゲーム用入力チェック関数
    def is_game_key_pressed(self, game_key: str) -> bool:
        """ゲーム用キーが押されているかチェック"""
        for pygame_key, mapped_key in self.key_mapping.items():
            if mapped_key == game_key and self.is_key_pressed(pygame_key):
                return True
        return False
    
    def is_game_key_just_pressed(self, game_key: str) -> bool:
        """ゲーム用キーが今フレームで押されたかチェック"""
        for pygame_key, mapped_key in self.key_mapping.items():
            if mapped_key == game_key and self.is_key_just_pressed(pygame_key):
                return True
        return False
    
    def is_game_key_just_released(self, game_key: str) -> bool:
        """ゲーム用キーが今フレームで離されたかチェック"""
        for pygame_key, mapped_key in self.key_mapping.items():
            if mapped_key == game_key and self.is_key_just_released(pygame_key):
                return True
        return False
    
    # マウス状態チェック関数
    def is_mouse_button_pressed(self, button: int) -> bool:
        """マウスボタンが押されているかチェック"""
        return button in self.mouse_buttons_pressed
    
    def is_mouse_button_just_pressed(self, button: int) -> bool:
        """マウスボタンが今フレームで押されたかチェック"""
        return button in self.mouse_buttons_just_pressed
    
    def is_mouse_button_just_released(self, button: int) -> bool:
        """マウスボタンが今フレームで離されたかチェック"""
        return button in self.mouse_buttons_just_released
    
    def get_mouse_pos(self) -> Tuple[int, int]:
        """マウス位置を取得"""
        return self.mouse_pos
    
    # 方向入力取得
    def get_movement_vector(self) -> Tuple[int, int]:
        """移動ベクトルを取得 (-1, 0, 1)"""
        x, y = 0, 0
        
        if self.is_game_key_pressed(KEY_LEFT):
            x -= 1
        if self.is_game_key_pressed(KEY_RIGHT):
            x += 1
        if self.is_game_key_pressed(KEY_UP):
            y -= 1
        if self.is_game_key_pressed(KEY_DOWN):
            y += 1
        
        return (x, y)
