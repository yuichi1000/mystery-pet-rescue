"""
設定メニューUI
音量設定、キーコンフィグ、画面設定
"""

import pygame
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum

from src.utils.font_manager import get_font_manager

class SettingType(Enum):
    """設定タイプ"""
    SLIDER = "slider"
    TOGGLE = "toggle"
    KEY_BIND = "key_bind"
    DROPDOWN = "dropdown"

@dataclass
class SettingItem:
    """設定項目"""
    key: str
    label: str
    setting_type: SettingType
    value: Any
    min_value: float = 0.0
    max_value: float = 1.0
    options: List[str] = None
    rect: pygame.Rect = None

class SettingsMenu:
    """設定メニュークラス"""
    
    def __init__(self, screen: pygame.Surface, settings: Dict[str, Any]):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        self.settings = settings
        
        # フォントマネージャー
        self.font_manager = get_font_manager()
        
        # UI状態
        self.selected_item = 0
        self.is_editing = False
        self.waiting_for_key = False
        self.editing_key = None
        
        # 色設定
        self.colors = {
            'background': (47, 79, 79),
            'panel': (70, 70, 70),
            'selected': (100, 149, 237),
            'text': (255, 255, 255),
            'slider_bg': (100, 100, 100),
            'slider_fg': (70, 130, 180),
            'button': (60, 60, 60),
            'button_hover': (80, 80, 80)
        }
        
        # 設定項目を初期化
        self._setup_settings()
    
    def _setup_settings(self):
        """設定項目を設定"""
        self.setting_items = [
            # 音量設定
            SettingItem("master_volume", "マスター音量", SettingType.SLIDER, 
                       self.settings.get("master_volume", 0.8), 0.0, 1.0),
            SettingItem("music_volume", "BGM音量", SettingType.SLIDER, 
                       self.settings.get("music_volume", 0.7), 0.0, 1.0),
            SettingItem("sfx_volume", "効果音音量", SettingType.SLIDER, 
                       self.settings.get("sfx_volume", 0.8), 0.0, 1.0),
            
            # 画面設定
            SettingItem("fullscreen", "フルスクリーン", SettingType.TOGGLE, 
                       self.settings.get("fullscreen", False)),
            
            # キー設定
            SettingItem("key_up", "上移動", SettingType.KEY_BIND, 
                       self.settings.get("key_bindings", {}).get("up", pygame.K_UP)),
            SettingItem("key_down", "下移動", SettingType.KEY_BIND, 
                       self.settings.get("key_bindings", {}).get("down", pygame.K_DOWN)),
            SettingItem("key_left", "左移動", SettingType.KEY_BIND, 
                       self.settings.get("key_bindings", {}).get("left", pygame.K_LEFT)),
            SettingItem("key_right", "右移動", SettingType.KEY_BIND, 
                       self.settings.get("key_bindings", {}).get("right", pygame.K_RIGHT)),
            SettingItem("key_action", "決定", SettingType.KEY_BIND, 
                       self.settings.get("key_bindings", {}).get("action", pygame.K_SPACE)),
            SettingItem("key_cancel", "キャンセル", SettingType.KEY_BIND, 
                       self.settings.get("key_bindings", {}).get("cancel", pygame.K_ESCAPE)),
        ]
        
        # 設定項目の位置を計算
        self._calculate_positions()
    
    def _calculate_positions(self):
        """設定項目の位置を計算"""
        start_y = 150
        item_height = 60
        
        for i, item in enumerate(self.setting_items):
            y = start_y + i * item_height
            item.rect = pygame.Rect(100, y, self.screen_width - 200, 50)
    
    def update(self, events: List[pygame.event.Event]) -> Dict[str, Any]:
        """設定メニューを更新"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if self.waiting_for_key:
                    self._handle_key_binding(event.key)
                else:
                    self._handle_navigation(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左クリック
                    self._handle_mouse_click(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_hover(event.pos)
        
        return self._get_updated_settings()
    
    def _handle_navigation(self, key: int):
        """ナビゲーション処理"""
        if key == pygame.K_UP:
            self.selected_item = (self.selected_item - 1) % len(self.setting_items)
            self.is_editing = False
        
        elif key == pygame.K_DOWN:
            self.selected_item = (self.selected_item + 1) % len(self.setting_items)
            self.is_editing = False
        
        elif key == pygame.K_RETURN or key == pygame.K_SPACE:
            self._activate_setting()
        
        elif key == pygame.K_LEFT:
            if self.is_editing:
                self._adjust_setting(-1)
        
        elif key == pygame.K_RIGHT:
            if self.is_editing:
                self._adjust_setting(1)
    
    def _handle_key_binding(self, key: int):
        """キーバインド処理"""
        if self.waiting_for_key and self.editing_key is not None:
            current_item = self.setting_items[self.selected_item]
            current_item.value = key
            self.waiting_for_key = False
            self.editing_key = None
            self.is_editing = False
            print(f"🔑 キー設定: {current_item.label} = {pygame.key.name(key)}")
    
    def _handle_mouse_click(self, pos: Tuple[int, int]):
        """マウスクリック処理"""
        for i, item in enumerate(self.setting_items):
            if item.rect and item.rect.collidepoint(pos):
                self.selected_item = i
                self._activate_setting()
                break
    
    def _handle_mouse_hover(self, pos: Tuple[int, int]):
        """マウスホバー処理"""
        for i, item in enumerate(self.setting_items):
            if item.rect and item.rect.collidepoint(pos):
                self.selected_item = i
                break
    
    def _activate_setting(self):
        """設定を有効化"""
        current_item = self.setting_items[self.selected_item]
        
        if current_item.setting_type == SettingType.TOGGLE:
            current_item.value = not current_item.value
            print(f"🔄 設定変更: {current_item.label} = {current_item.value}")
        
        elif current_item.setting_type == SettingType.SLIDER:
            self.is_editing = not self.is_editing
            print(f"🎚️ スライダー編集: {current_item.label}")
        
        elif current_item.setting_type == SettingType.KEY_BIND:
            self.waiting_for_key = True
            self.editing_key = current_item.key
            self.is_editing = True
            print(f"⌨️ キー入力待ち: {current_item.label}")
    
    def _adjust_setting(self, direction: int):
        """設定値を調整"""
        current_item = self.setting_items[self.selected_item]
        
        if current_item.setting_type == SettingType.SLIDER:
            step = 0.1 * direction
            new_value = current_item.value + step
            current_item.value = max(current_item.min_value, 
                                   min(current_item.max_value, new_value))
            print(f"🎚️ 音量調整: {current_item.label} = {current_item.value:.1f}")
    
    def _get_updated_settings(self) -> Dict[str, Any]:
        """更新された設定を取得"""
        updated_settings = self.settings.copy()
        
        for item in self.setting_items:
            if item.key.startswith("key_"):
                # キーバインド設定
                key_name = item.key[4:]  # "key_"を除去
                if "key_bindings" not in updated_settings:
                    updated_settings["key_bindings"] = {}
                updated_settings["key_bindings"][key_name] = item.value
            else:
                # その他の設定
                updated_settings[item.key] = item.value
        
        return updated_settings
    
    def draw(self):
        """設定メニューを描画"""
        # 背景
        self.screen.fill(self.colors['background'])
        
        # タイトル
        title_surface = self.font_manager.render_text("設定", 36, self.colors['text'])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 80))
        self.screen.blit(title_surface, title_rect)
        
        # 設定項目を描画
        for i, item in enumerate(self.setting_items):
            self._draw_setting_item(item, i == self.selected_item)
        
        # キー入力待ちメッセージ
        if self.waiting_for_key:
            self._draw_key_waiting_message()
        
        # 操作説明
        self._draw_controls_help()
    
    def _draw_setting_item(self, item: SettingItem, is_selected: bool):
        """設定項目を描画"""
        if not item.rect:
            return
        
        # 背景
        bg_color = self.colors['selected'] if is_selected else self.colors['panel']
        pygame.draw.rect(self.screen, bg_color, item.rect)
        pygame.draw.rect(self.screen, self.colors['text'], item.rect, 2)
        
        # ラベル
        label_surface = self.font_manager.render_text(item.label, 18, self.colors['text'])
        label_rect = pygame.Rect(item.rect.x + 20, item.rect.y + 15, 200, 20)
        self.screen.blit(label_surface, label_rect)
        
        # 設定値の描画
        value_rect = pygame.Rect(item.rect.x + 250, item.rect.y + 10, 
                               item.rect.width - 270, item.rect.height - 20)
        
        if item.setting_type == SettingType.SLIDER:
            self._draw_slider(value_rect, item.value, item.min_value, item.max_value, 
                            is_selected and self.is_editing)
        
        elif item.setting_type == SettingType.TOGGLE:
            self._draw_toggle(value_rect, item.value)
        
        elif item.setting_type == SettingType.KEY_BIND:
            self._draw_key_bind(value_rect, item.value, 
                              is_selected and self.waiting_for_key)
    
    def _draw_slider(self, rect: pygame.Rect, value: float, min_val: float, max_val: float, is_editing: bool):
        """スライダーを描画"""
        # スライダー背景
        slider_bg = pygame.Rect(rect.x, rect.y + rect.height // 2 - 5, rect.width - 80, 10)
        pygame.draw.rect(self.screen, self.colors['slider_bg'], slider_bg)
        
        # スライダー値
        progress = (value - min_val) / (max_val - min_val)
        slider_pos = int(slider_bg.x + progress * slider_bg.width)
        slider_handle = pygame.Rect(slider_pos - 5, slider_bg.y - 5, 10, 20)
        
        handle_color = self.colors['selected'] if is_editing else self.colors['slider_fg']
        pygame.draw.rect(self.screen, handle_color, slider_handle)
        
        # 値表示
        value_text = f"{int(value * 100)}%"
        value_surface = self.font_manager.render_text(value_text, 16, self.colors['text'])
        value_pos = (rect.x + rect.width - 70, rect.y + rect.height // 2 - 8)
        self.screen.blit(value_surface, value_pos)
    
    def _draw_toggle(self, rect: pygame.Rect, value: bool):
        """トグルを描画"""
        toggle_rect = pygame.Rect(rect.x, rect.y + rect.height // 2 - 10, 40, 20)
        
        # トグル背景
        bg_color = self.colors['selected'] if value else self.colors['slider_bg']
        pygame.draw.rect(self.screen, bg_color, toggle_rect)
        pygame.draw.rect(self.screen, self.colors['text'], toggle_rect, 2)
        
        # トグルハンドル
        handle_x = toggle_rect.x + 22 if value else toggle_rect.x + 2
        handle_rect = pygame.Rect(handle_x, toggle_rect.y + 2, 16, 16)
        pygame.draw.rect(self.screen, self.colors['text'], handle_rect)
        
        # 状態テキスト
        status_text = "ON" if value else "OFF"
        status_surface = self.font_manager.render_text(status_text, 16, self.colors['text'])
        status_pos = (rect.x + 60, rect.y + rect.height // 2 - 8)
        self.screen.blit(status_surface, status_pos)
    
    def _draw_key_bind(self, rect: pygame.Rect, key_code: int, is_waiting: bool):
        """キーバインドを描画"""
        # キー名取得
        try:
            key_name = pygame.key.name(key_code).upper()
        except:
            key_name = "UNKNOWN"
        
        # 背景
        bg_color = self.colors['selected'] if is_waiting else self.colors['button']
        key_rect = pygame.Rect(rect.x, rect.y + 5, 120, rect.height - 10)
        pygame.draw.rect(self.screen, bg_color, key_rect)
        pygame.draw.rect(self.screen, self.colors['text'], key_rect, 2)
        
        # キー名表示
        if is_waiting:
            display_text = "キー入力待ち..."
            text_color = (255, 255, 0)
        else:
            display_text = key_name
            text_color = self.colors['text']
        
        key_surface = self.font_manager.render_text(display_text, 14, text_color)
        key_pos = key_surface.get_rect(center=key_rect.center)
        self.screen.blit(key_surface, key_pos)
    
    def _draw_key_waiting_message(self):
        """キー入力待ちメッセージを描画"""
        message = "新しいキーを押してください（ESCでキャンセル）"
        message_surface = self.font_manager.render_text(message, 20, (255, 255, 0))
        message_rect = message_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 100))
        
        # 背景
        bg_rect = pygame.Rect(message_rect.x - 20, message_rect.y - 10, 
                            message_rect.width + 40, message_rect.height + 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(self.screen, (255, 255, 0), bg_rect, 2)
        
        self.screen.blit(message_surface, message_rect)
    
    def _draw_controls_help(self):
        """操作説明を描画"""
        help_texts = [
            "↑↓: 項目選択",
            "Enter/Space: 設定変更",
            "←→: スライダー調整",
            "ESC: 戻る"
        ]
        
        start_y = self.screen_height - 150
        for i, text in enumerate(help_texts):
            help_surface = self.font_manager.render_text(text, 14, self.colors['text'])
            self.screen.blit(help_surface, (50, start_y + i * 20))
    
    def reset_to_defaults(self):
        """デフォルト設定にリセット"""
        default_values = {
            "master_volume": 0.8,
            "music_volume": 0.7,
            "sfx_volume": 0.8,
            "fullscreen": False,
            "key_up": pygame.K_UP,
            "key_down": pygame.K_DOWN,
            "key_left": pygame.K_LEFT,
            "key_right": pygame.K_RIGHT,
            "key_action": pygame.K_SPACE,
            "key_cancel": pygame.K_ESCAPE,
        }
        
        for item in self.setting_items:
            if item.key in default_values:
                item.value = default_values[item.key]
        
        print("🔄 設定をデフォルトにリセットしました")
