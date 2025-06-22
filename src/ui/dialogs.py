"""
ダイアログシステム

会話、確認、情報表示などのダイアログを管理
"""

import pygame
from typing import List, Dict, Any, Optional, Callable
from config.constants import *


class Dialog:
    """ダイアログ基底クラス"""
    
    def __init__(self, title: str = "", width: int = 400, height: int = 200):
        self.title = title
        self.width = width
        self.height = height
        self.x = (SCREEN_WIDTH - width) // 2
        self.y = (SCREEN_HEIGHT - height) // 2
        self.visible = False
        self.result = None
        
        # フォント
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # 色設定
        self.bg_color = UI_BACKGROUND
        self.border_color = UI_BORDER
        self.title_color = UI_TEXT
        self.text_color = UI_TEXT
    
    def show(self):
        """ダイアログを表示"""
        self.visible = True
        self.result = None
    
    def hide(self):
        """ダイアログを非表示"""
        self.visible = False
    
    def update(self, input_handler):
        """ダイアログを更新"""
        pass
    
    def render(self, screen: pygame.Surface):
        """ダイアログを描画"""
        if not self.visible:
            return
        
        # 背景オーバーレイ
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(COLOR_BLACK)
        screen.blit(overlay, (0, 0))
        
        # ダイアログ背景
        dialog_rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(screen, self.bg_color, dialog_rect)
        pygame.draw.rect(screen, self.border_color, dialog_rect, 3)
        
        # タイトル
        if self.title:
            title_surface = self.title_font.render(self.title, True, self.title_color)
            title_rect = title_surface.get_rect(centerx=self.x + self.width // 2, y=self.y + 10)
            screen.blit(title_surface, title_rect)


class MessageDialog(Dialog):
    """メッセージダイアログ"""
    
    def __init__(self, title: str, message: str, callback: Callable = None):
        super().__init__(title, 500, 250)
        self.message = message
        self.callback = callback
        self.message_lines = self._wrap_text(message, self.width - 40)
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """テキストを折り返し"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_surface = self.text_font.render(test_line, True, self.text_color)
            
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def update(self, input_handler):
        """更新処理"""
        if not self.visible:
            return
        
        # 任意のキーで閉じる
        if (input_handler.is_game_key_just_pressed(KEY_ACTION) or
            input_handler.is_game_key_just_pressed(KEY_CANCEL) or
            input_handler.is_mouse_button_just_pressed(1)):
            
            self.result = "ok"
            self.hide()
            
            if self.callback:
                self.callback()
    
    def render(self, screen: pygame.Surface):
        """描画処理"""
        super().render(screen)
        
        if not self.visible:
            return
        
        # メッセージテキスト
        y_offset = 60 if self.title else 20
        for i, line in enumerate(self.message_lines):
            text_surface = self.text_font.render(line, True, self.text_color)
            text_rect = text_surface.get_rect(centerx=self.x + self.width // 2, 
                                            y=self.y + y_offset + i * 40)
            screen.blit(text_surface, text_rect)
        
        # 操作ヒント
        hint_text = self.small_font.render("任意のキーで閉じる", True, COLOR_GRAY)
        hint_rect = hint_text.get_rect(centerx=self.x + self.width // 2, 
                                     y=self.y + self.height - 30)
        screen.blit(hint_text, hint_rect)


class ConfirmDialog(Dialog):
    """確認ダイアログ"""
    
    def __init__(self, title: str, message: str, 
                 on_yes: Callable = None, on_no: Callable = None):
        super().__init__(title, 400, 200)
        self.message = message
        self.on_yes = on_yes
        self.on_no = on_no
        self.selected_button = 0  # 0: Yes, 1: No
        self.message_lines = self._wrap_text(message, self.width - 40)
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """テキストを折り返し"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_surface = self.text_font.render(test_line, True, self.text_color)
            
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def update(self, input_handler):
        """更新処理"""
        if not self.visible:
            return
        
        # 左右キーでボタン選択
        if input_handler.is_game_key_just_pressed(KEY_LEFT):
            self.selected_button = 0
        elif input_handler.is_game_key_just_pressed(KEY_RIGHT):
            self.selected_button = 1
        
        # 決定キー
        elif input_handler.is_game_key_just_pressed(KEY_ACTION):
            if self.selected_button == 0:
                self.result = "yes"
                if self.on_yes:
                    self.on_yes()
            else:
                self.result = "no"
                if self.on_no:
                    self.on_no()
            self.hide()
        
        # キャンセルキー
        elif input_handler.is_game_key_just_pressed(KEY_CANCEL):
            self.result = "no"
            if self.on_no:
                self.on_no()
            self.hide()
        
        # マウス操作
        self._handle_mouse_input(input_handler)
    
    def _handle_mouse_input(self, input_handler):
        """マウス入力処理"""
        mouse_pos = input_handler.get_mouse_pos()
        mouse_clicked = input_handler.is_mouse_button_just_pressed(1)
        
        # Yesボタン
        yes_rect = pygame.Rect(self.x + 50, self.y + self.height - 60, 100, 40)
        if yes_rect.collidepoint(mouse_pos):
            self.selected_button = 0
            if mouse_clicked:
                self.result = "yes"
                if self.on_yes:
                    self.on_yes()
                self.hide()
        
        # Noボタン
        no_rect = pygame.Rect(self.x + self.width - 150, self.y + self.height - 60, 100, 40)
        if no_rect.collidepoint(mouse_pos):
            self.selected_button = 1
            if mouse_clicked:
                self.result = "no"
                if self.on_no:
                    self.on_no()
                self.hide()
    
    def render(self, screen: pygame.Surface):
        """描画処理"""
        super().render(screen)
        
        if not self.visible:
            return
        
        # メッセージテキスト
        y_offset = 60 if self.title else 20
        for i, line in enumerate(self.message_lines):
            text_surface = self.text_font.render(line, True, self.text_color)
            text_rect = text_surface.get_rect(centerx=self.x + self.width // 2, 
                                            y=self.y + y_offset + i * 30)
            screen.blit(text_surface, text_rect)
        
        # ボタン
        self._render_button(screen, "はい", self.x + 50, self.y + self.height - 60, 
                          100, 40, self.selected_button == 0)
        self._render_button(screen, "いいえ", self.x + self.width - 150, self.y + self.height - 60,
                          100, 40, self.selected_button == 1)
    
    def _render_button(self, screen: pygame.Surface, text: str, x: int, y: int, 
                      width: int, height: int, selected: bool):
        """ボタンを描画"""
        button_rect = pygame.Rect(x, y, width, height)
        
        if selected:
            pygame.draw.rect(screen, UI_HIGHLIGHT, button_rect)
            text_color = COLOR_WHITE
        else:
            pygame.draw.rect(screen, UI_BUTTON, button_rect)
            text_color = UI_TEXT
        
        pygame.draw.rect(screen, UI_BORDER, button_rect, 2)
        
        text_surface = self.text_font.render(text, True, text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)


class ConversationDialog(Dialog):
    """会話ダイアログ"""
    
    def __init__(self, speaker_name: str, dialogue_lines: List[str]):
        super().__init__("", 600, 200)
        self.speaker_name = speaker_name
        self.dialogue_lines = dialogue_lines
        self.current_line = 0
        self.text_display = ""
        self.text_speed = 2  # 文字表示速度
        self.text_timer = 0
        self.full_text_displayed = False
        
        # ダイアログの位置を下部に設定
        self.y = SCREEN_HEIGHT - self.height - 20
    
    def update(self, input_handler):
        """更新処理"""
        if not self.visible:
            return
        
        if self.current_line >= len(self.dialogue_lines):
            self.hide()
            return
        
        current_text = self.dialogue_lines[self.current_line]
        
        # テキストアニメーション
        if not self.full_text_displayed:
            self.text_timer += 1
            if self.text_timer >= self.text_speed:
                self.text_timer = 0
                if len(self.text_display) < len(current_text):
                    self.text_display += current_text[len(self.text_display)]
                else:
                    self.full_text_displayed = True
        
        # 次の行に進む
        if input_handler.is_game_key_just_pressed(KEY_ACTION):
            if self.full_text_displayed:
                self.current_line += 1
                if self.current_line < len(self.dialogue_lines):
                    self.text_display = ""
                    self.full_text_displayed = False
            else:
                # テキストを即座に全表示
                self.text_display = current_text
                self.full_text_displayed = True
        
        # スキップ
        if input_handler.is_game_key_just_pressed(KEY_CANCEL):
            self.hide()
    
    def render(self, screen: pygame.Surface):
        """描画処理"""
        super().render(screen)
        
        if not self.visible:
            return
        
        # 話者名
        if self.speaker_name:
            name_surface = self.text_font.render(self.speaker_name, True, UI_HIGHLIGHT)
            screen.blit(name_surface, (self.x + 20, self.y + 10))
        
        # 会話テキスト
        y_offset = 50 if self.speaker_name else 20
        
        # テキストを折り返し
        wrapped_lines = self._wrap_text(self.text_display, self.width - 40)
        for i, line in enumerate(wrapped_lines):
            text_surface = self.text_font.render(line, True, self.text_color)
            screen.blit(text_surface, (self.x + 20, self.y + y_offset + i * 35))
        
        # 進行インジケーター
        if self.full_text_displayed:
            indicator_text = self.small_font.render("▼", True, UI_HIGHLIGHT)
            screen.blit(indicator_text, (self.x + self.width - 30, self.y + self.height - 30))
        
        # 操作ヒント
        hint_text = self.small_font.render("SPACE: 次へ  ESC: スキップ", True, COLOR_GRAY)
        screen.blit(hint_text, (self.x + 20, self.y + self.height - 25))
    
    def _wrap_text(self, text: str, max_width: int) -> List[str]:
        """テキストを折り返し"""
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            test_surface = self.text_font.render(test_line, True, self.text_color)
            
            if test_surface.get_width() <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines


class DialogSystem:
    """ダイアログシステム管理クラス"""
    
    def __init__(self):
        self.current_dialog: Optional[Dialog] = None
        self.dialog_queue: List[Dialog] = []
    
    def show_message(self, title: str, message: str, callback: Callable = None):
        """メッセージダイアログを表示"""
        dialog = MessageDialog(title, message, callback)
        self._show_dialog(dialog)
    
    def show_confirm(self, title: str, message: str, 
                    on_yes: Callable = None, on_no: Callable = None):
        """確認ダイアログを表示"""
        dialog = ConfirmDialog(title, message, on_yes, on_no)
        self._show_dialog(dialog)
    
    def show_conversation(self, speaker_name: str, dialogue_lines: List[str]):
        """会話ダイアログを表示"""
        dialog = ConversationDialog(speaker_name, dialogue_lines)
        self._show_dialog(dialog)
    
    def _show_dialog(self, dialog: Dialog):
        """ダイアログを表示"""
        if self.current_dialog and self.current_dialog.visible:
            # 現在のダイアログがある場合はキューに追加
            self.dialog_queue.append(dialog)
        else:
            self.current_dialog = dialog
            dialog.show()
    
    def update(self, input_handler):
        """ダイアログシステムを更新"""
        if self.current_dialog:
            self.current_dialog.update(input_handler)
            
            # ダイアログが閉じられた場合
            if not self.current_dialog.visible:
                self.current_dialog = None
                
                # キューに次のダイアログがある場合
                if self.dialog_queue:
                    next_dialog = self.dialog_queue.pop(0)
                    self.current_dialog = next_dialog
                    next_dialog.show()
    
    def render(self, screen: pygame.Surface):
        """ダイアログシステムを描画"""
        if self.current_dialog:
            self.current_dialog.render(screen)
    
    def is_dialog_active(self) -> bool:
        """ダイアログがアクティブかチェック"""
        return self.current_dialog is not None and self.current_dialog.visible
    
    def close_current_dialog(self):
        """現在のダイアログを閉じる"""
        if self.current_dialog:
            self.current_dialog.hide()
    
    def clear_all_dialogs(self):
        """全てのダイアログをクリア"""
        self.current_dialog = None
        self.dialog_queue.clear()
