"""
メニューシステム

ゲーム内メニューの管理
"""

import pygame
from typing import List, Dict, Any, Optional, Callable
from config.constants import *


class MenuItem:
    """メニュー項目クラス"""
    
    def __init__(self, text: str, action: Callable = None, enabled: bool = True):
        self.text = text
        self.action = action
        self.enabled = enabled
        self.selected = False


class MenuSystem:
    """メニューシステムクラス"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.items: List[MenuItem] = []
        self.selected_index = 0
        self.visible = False
        self.menu_type = "main"
        
        # メニューの位置とサイズ
        self.x = SCREEN_WIDTH // 4
        self.y = SCREEN_HEIGHT // 4
        self.width = SCREEN_WIDTH // 2
        self.height = SCREEN_HEIGHT // 2
        
        # 色設定
        self.bg_color = UI_BACKGROUND
        self.border_color = UI_BORDER
        self.text_color = UI_TEXT
        self.selected_color = UI_HIGHLIGHT
        self.disabled_color = COLOR_GRAY
    
    def show_main_menu(self):
        """メインメニューを表示"""
        self.items = [
            MenuItem("ゲーム開始", self._start_game),
            MenuItem("ゲーム続行", self._continue_game),
            MenuItem("ペット図鑑", self._show_collection),
            MenuItem("設定", self._show_settings),
            MenuItem("終了", self._quit_game)
        ]
        self.menu_type = "main"
        self.selected_index = 0
        self.visible = True
    
    def show_pause_menu(self):
        """ポーズメニューを表示"""
        self.items = [
            MenuItem("ゲーム再開", self._resume_game),
            MenuItem("インベントリ", self._show_inventory),
            MenuItem("ペット図鑑", self._show_collection),
            MenuItem("設定", self._show_settings),
            MenuItem("メインメニューに戻る", self._return_to_main),
            MenuItem("ゲーム終了", self._quit_game)
        ]
        self.menu_type = "pause"
        self.selected_index = 0
        self.visible = True
    
    def show_settings_menu(self):
        """設定メニューを表示"""
        self.items = [
            MenuItem("音量設定", self._audio_settings),
            MenuItem("画面設定", self._display_settings),
            MenuItem("言語設定", self._language_settings),
            MenuItem("キー設定", self._key_settings),
            MenuItem("戻る", self._back_to_previous)
        ]
        self.menu_type = "settings"
        self.selected_index = 0
        self.visible = True
    
    def hide(self):
        """メニューを非表示"""
        self.visible = False
    
    def update(self, input_handler):
        """メニューを更新"""
        if not self.visible:
            return
        
        # 上下キーでの選択
        if input_handler.is_game_key_just_pressed(KEY_UP):
            self._move_selection(-1)
        elif input_handler.is_game_key_just_pressed(KEY_DOWN):
            self._move_selection(1)
        
        # 決定キー
        elif input_handler.is_game_key_just_pressed(KEY_ACTION):
            self._execute_selected_action()
        
        # キャンセルキー
        elif input_handler.is_game_key_just_pressed(KEY_CANCEL):
            self._handle_cancel()
        
        # マウス操作
        self._handle_mouse_input(input_handler)
    
    def _move_selection(self, direction: int):
        """選択を移動"""
        if not self.items:
            return
        
        old_index = self.selected_index
        self.selected_index = (self.selected_index + direction) % len(self.items)
        
        # 無効な項目をスキップ
        attempts = 0
        while not self.items[self.selected_index].enabled and attempts < len(self.items):
            self.selected_index = (self.selected_index + direction) % len(self.items)
            attempts += 1
        
        if old_index != self.selected_index:
            # 選択音を再生（TODO: 音声システム実装後）
            pass
    
    def _execute_selected_action(self):
        """選択された項目のアクションを実行"""
        if (0 <= self.selected_index < len(self.items) and 
            self.items[self.selected_index].enabled and
            self.items[self.selected_index].action):
            
            self.items[self.selected_index].action()
    
    def _handle_cancel(self):
        """キャンセル処理"""
        if self.menu_type == "main":
            # メインメニューではゲーム終了確認
            pass
        else:
            # その他のメニューでは前のメニューに戻る
            self._back_to_previous()
    
    def _handle_mouse_input(self, input_handler):
        """マウス入力処理"""
        mouse_pos = input_handler.get_mouse_pos()
        mouse_clicked = input_handler.is_mouse_button_just_pressed(1)
        
        # メニュー項目上のマウス位置チェック
        for i, item in enumerate(self.items):
            item_y = self.y + 100 + i * 60
            item_rect = pygame.Rect(self.x + 50, item_y, self.width - 100, 50)
            
            if item_rect.collidepoint(mouse_pos):
                if item.enabled:
                    self.selected_index = i
                    
                    if mouse_clicked:
                        self._execute_selected_action()
    
    def render(self, screen: pygame.Surface):
        """メニューを描画"""
        if not self.visible:
            return
        
        # 背景オーバーレイ
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        # メニュー背景
        menu_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, menu_rect)
        pygame.draw.rect(screen, self.border_color, menu_rect, 3)
        
        # タイトル
        title_text = self._get_menu_title()
        title_surface = self.font.render(title_text, True, self.text_color)
        title_rect = title_surface.get_rect(centerx=self.x + self.width // 2, y=self.y + 20)
        screen.blit(title_surface, title_rect)
        
        # メニュー項目
        for i, item in enumerate(self.items):
            self._render_menu_item(screen, item, i)
    
    def _get_menu_title(self) -> str:
        """メニュータイトルを取得"""
        titles = {
            "main": "メインメニュー",
            "pause": "ポーズメニュー",
            "settings": "設定",
            "audio": "音量設定",
            "display": "画面設定",
            "language": "言語設定",
            "keys": "キー設定"
        }
        return titles.get(self.menu_type, "メニュー")
    
    def _render_menu_item(self, screen: pygame.Surface, item: MenuItem, index: int):
        """メニュー項目を描画"""
        y = self.y + 100 + index * 60
        
        # 選択状態の背景
        if index == self.selected_index:
            highlight_rect = pygame.Rect(self.x + 30, y - 5, self.width - 60, 50)
            pygame.draw.rect(screen, self.selected_color, highlight_rect)
        
        # テキスト色を決定
        if not item.enabled:
            text_color = self.disabled_color
        elif index == self.selected_index:
            text_color = COLOR_WHITE
        else:
            text_color = self.text_color
        
        # テキストを描画
        text_surface = self.font.render(item.text, True, text_color)
        text_rect = text_surface.get_rect(centerx=self.x + self.width // 2, y=y)
        screen.blit(text_surface, text_rect)
    
    # アクション関数
    def _start_game(self):
        """ゲーム開始"""
        print("新しいゲームを開始")
        self.hide()
        # TODO: ゲーム開始処理
    
    def _continue_game(self):
        """ゲーム続行"""
        print("ゲームを続行")
        self.hide()
        # TODO: セーブデータ読み込み
    
    def _show_collection(self):
        """ペット図鑑表示"""
        print("ペット図鑑を表示")
        # TODO: ペット図鑑画面に遷移
    
    def _show_settings(self):
        """設定表示"""
        self.show_settings_menu()
    
    def _quit_game(self):
        """ゲーム終了"""
        print("ゲームを終了")
        # TODO: 終了確認ダイアログ
    
    def _resume_game(self):
        """ゲーム再開"""
        print("ゲームを再開")
        self.hide()
    
    def _show_inventory(self):
        """インベントリ表示"""
        print("インベントリを表示")
        # TODO: インベントリ画面に遷移
    
    def _return_to_main(self):
        """メインメニューに戻る"""
        print("メインメニューに戻る")
        self.show_main_menu()
    
    def _audio_settings(self):
        """音量設定"""
        print("音量設定")
        # TODO: 音量設定画面
    
    def _display_settings(self):
        """画面設定"""
        print("画面設定")
        # TODO: 画面設定画面
    
    def _language_settings(self):
        """言語設定"""
        print("言語設定")
        # TODO: 言語設定画面
    
    def _key_settings(self):
        """キー設定"""
        print("キー設定")
        # TODO: キー設定画面
    
    def _back_to_previous(self):
        """前のメニューに戻る"""
        if self.menu_type == "settings":
            if hasattr(self, '_previous_menu'):
                if self._previous_menu == "pause":
                    self.show_pause_menu()
                else:
                    self.show_main_menu()
            else:
                self.show_main_menu()
        else:
            self.hide()
