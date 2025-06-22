"""
謎解きUIシステム
謎解きゲームのユーザーインターフェース
"""

import pygame
from typing import List, Dict, Optional, Tuple, Callable
from dataclasses import dataclass
from enum import Enum

from src.systems.puzzle_system import PuzzleSystem, PuzzleState
from src.systems.hint_system import HintSystem
from src.utils.font_manager import get_font_manager

class UIState(Enum):
    """UI状態"""
    PUZZLE_SELECT = "puzzle_select"
    PUZZLE_ACTIVE = "puzzle_active"
    ITEM_COMBINATION = "item_combination"
    HINT_DISPLAY = "hint_display"
    RESULT_DISPLAY = "result_display"

@dataclass
class UIColors:
    """UI色定義"""
    background = (240, 248, 255)
    panel = (255, 255, 255, 220)
    border = (200, 200, 200)
    text = (50, 50, 50)
    success = (76, 175, 80)
    error = (244, 67, 54)
    warning = (255, 193, 7)
    info = (33, 150, 243)
    hint = (156, 39, 176)

class PuzzleUI:
    """謎解きUIクラス"""
    
    def __init__(self, screen: pygame.Surface, puzzle_system: PuzzleSystem):
        self.screen = screen
        self.puzzle_system = puzzle_system
        self.hint_system = HintSystem(puzzle_system)
        
        # UI状態
        self.current_state = UIState.PUZZLE_SELECT
        self.active_puzzle_id: Optional[str] = None
        self.selected_items: List[str] = []
        self.available_items: List[str] = []
        
        # フォントマネージャー
        self.font_manager = get_font_manager()
        
        # 色設定
        self.colors = UIColors()
        
        # UI要素の位置
        self.setup_ui_layout()
        
        # メッセージ表示
        self.current_message = ""
        self.message_timer = 0.0
        self.message_type = "info"
        
        # アニメーション
        self.animation_timer = 0.0
        
    def setup_ui_layout(self):
        """UIレイアウトを設定"""
        self.screen_width = self.screen.get_width()
        self.screen_height = self.screen.get_height()
        
        # パネル領域（サイズ調整）
        self.main_panel = pygame.Rect(50, 50, self.screen_width - 100, self.screen_height - 100)
        self.info_panel = pygame.Rect(50, 50, 500, 220)  # 幅と高さを拡大
        self.items_panel = pygame.Rect(570, 50, 280, 400)  # 位置調整
        self.combination_panel = pygame.Rect(50, 290, 500, 180)  # 幅拡大、位置調整
        self.hint_panel = pygame.Rect(50, 490, self.screen_width - 100, 150)
        
        # ボタン領域
        self.button_height = 40
        self.button_margin = 10
    
    def update(self, time_delta: float, events: List[pygame.event.Event]):
        """UI更新"""
        self.animation_timer += time_delta
        
        # メッセージタイマー更新
        if self.message_timer > 0:
            self.message_timer -= time_delta
            if self.message_timer <= 0:
                self.current_message = ""
        
        # イベント処理
        for event in events:
            result = self.handle_event(event)
            if result == "quit":
                return "quit"
        
        return None
    
    def handle_event(self, event: pygame.event.Event):
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.current_state == UIState.PUZZLE_ACTIVE:
                    # 謎解き実行中の場合は選択画面に戻る
                    self.current_state = UIState.PUZZLE_SELECT
                    self.active_puzzle_id = None
                    self.selected_items = []
                    self.show_message("謎解き選択に戻りました", "info")
                else:
                    # 選択画面の場合は終了フラグを設定
                    return "quit"
            elif event.key == pygame.K_h:
                # ヒント要求
                self.request_hint()
            elif event.key == pygame.K_r:
                # リセット
                self.reset_current_puzzle()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                self.handle_mouse_click(event.pos)
        
        return None
    
    def handle_mouse_click(self, pos: Tuple[int, int]):
        """マウスクリック処理"""
        if self.current_state == UIState.PUZZLE_SELECT:
            self.handle_puzzle_selection_click(pos)
        elif self.current_state == UIState.PUZZLE_ACTIVE:
            self.handle_puzzle_active_click(pos)
    
    def handle_puzzle_selection_click(self, pos: Tuple[int, int]):
        """謎解き選択画面のクリック処理"""
        puzzles = self.puzzle_system.get_available_puzzles()
        
        y_start = 130
        for i, puzzle in enumerate(puzzles):
            button_rect = pygame.Rect(80, y_start + i * 90, 640, 80)  # 調整されたサイズに合わせる
            if button_rect.collidepoint(pos):
                self.start_puzzle(puzzle['id'])
                break
    
    def handle_puzzle_active_click(self, pos: Tuple[int, int]):
        """謎解き実行中のクリック処理"""
        # アイテム選択
        if self.items_panel.collidepoint(pos):
            self.handle_item_selection(pos)
        
        # 組み合わせ実行ボタン
        combine_button = pygame.Rect(50, 480, 150, 40)  # 位置調整
        if combine_button.collidepoint(pos):
            self.try_combination()
        
        # ヒントボタン
        hint_button = pygame.Rect(220, 480, 100, 40)  # 位置調整
        if hint_button.collidepoint(pos):
            self.request_hint()
        
        # リセットボタン
        reset_button = pygame.Rect(340, 480, 100, 40)  # 位置調整
        if reset_button.collidepoint(pos):
            self.reset_current_puzzle()
    
    def handle_item_selection(self, pos: Tuple[int, int]):
        """アイテム選択処理"""
        item_y = self.items_panel.y + 45
        item_height = 40  # 調整された高さ
        
        for i, item in enumerate(self.available_items):
            item_rect = pygame.Rect(self.items_panel.x + 15, item_y + i * item_height, 
                                  self.items_panel.width - 30, 35)
            if item_rect.collidepoint(pos):
                if item in self.selected_items:
                    self.selected_items.remove(item)
                else:
                    self.selected_items.append(item)
                break
    
    def start_puzzle(self, puzzle_id: str):
        """謎解きを開始"""
        if self.puzzle_system.start_puzzle(puzzle_id):
            self.active_puzzle_id = puzzle_id
            self.current_state = UIState.PUZZLE_ACTIVE
            self.selected_items = []
            
            # サンプルアイテムを設定（実際のゲームではインベントリから取得）
            puzzle_data = self.puzzle_system.get_puzzle_data(puzzle_id)
            if puzzle_data:
                self.available_items = puzzle_data.get('required_items', []) + puzzle_data.get('optional_items', [])
            
            self.show_message("謎解きを開始しました！", "success")
    
    def try_combination(self):
        """アイテム組み合わせを試行"""
        if not self.active_puzzle_id or len(self.selected_items) < 2:
            self.show_message("2つ以上のアイテムを選択してください", "warning")
            return
        
        success, result, message = self.puzzle_system.check_item_combination(
            self.active_puzzle_id, self.selected_items
        )
        
        if success:
            self.show_message(f"成功！ {message}", "success")
            
            # ステージ完了チェック
            self.puzzle_system.check_stage_completion(self.active_puzzle_id, self.available_items)
            
            # 謎解き完了チェック
            if self.puzzle_system.check_puzzle_completion(self.active_puzzle_id):
                self.show_message("謎解き完了！おめでとうございます！", "success")
        else:
            self.show_message(message, "error")
        
        # 選択をクリア
        self.selected_items = []
    
    def request_hint(self):
        """ヒントを要求"""
        if not self.active_puzzle_id:
            return
        
        # アクティブな謎解きが存在するかチェック
        if self.active_puzzle_id not in self.puzzle_system.active_puzzles:
            self.show_message("謎解きが開始されていません", "warning")
            return
        
        hint = self.hint_system.get_contextual_hint(
            self.active_puzzle_id, 
            self.available_items,
            self.puzzle_system.active_puzzles[self.active_puzzle_id].failed_attempts
        )
        
        if hint:
            self.show_message(f"ヒント: {hint}", "hint")
        else:
            self.show_message("ヒントが利用できません", "warning")
    
    def reset_current_puzzle(self):
        """現在の謎解きをリセット"""
        if self.active_puzzle_id:
            self.puzzle_system.reset_puzzle(self.active_puzzle_id)
            self.selected_items = []
            self.current_state = UIState.PUZZLE_SELECT  # 謎解き選択に戻る
            self.active_puzzle_id = None
            self.show_message("謎解きをリセットしました", "info")
    
    def show_message(self, message: str, message_type: str = "info"):
        """メッセージを表示"""
        self.current_message = message
        self.message_type = message_type
        self.message_timer = 3.0  # 3秒間表示
    
    def draw(self):
        """UI描画"""
        self.screen.fill(self.colors.background)
        
        if self.current_state == UIState.PUZZLE_SELECT:
            self.draw_puzzle_selection()
        elif self.current_state == UIState.PUZZLE_ACTIVE:
            self.draw_puzzle_active()
        
        # メッセージ表示
        if self.current_message:
            self.draw_message()
    
    def draw_puzzle_selection(self):
        """謎解き選択画面を描画"""
        # タイトル
        title_text = self.font_manager.render_text("謎解き選択", 32, self.colors.text)
        title_rect = title_text.get_rect(center=(self.screen_width // 2, 60))
        self.screen.blit(title_text, title_rect)
        
        # 操作説明
        help_text = self.font_manager.render_text("クリックで謎解きを選択、ESCで終了", 16, self.colors.text)
        help_rect = help_text.get_rect(center=(self.screen_width // 2, 90))
        self.screen.blit(help_text, help_rect)
        
        # 謎解き一覧
        puzzles = self.puzzle_system.get_available_puzzles()
        y_start = 130
        
        for i, puzzle in enumerate(puzzles):
            # ボタン背景
            button_rect = pygame.Rect(80, y_start + i * 90, 640, 80)  # さらに高さを増加
            button_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
            button_surface.fill(self.colors.panel)
            self.screen.blit(button_surface, button_rect)
            pygame.draw.rect(self.screen, self.colors.border, button_rect, 2)
            
            # 謎解き情報（行間をさらに調整）
            title_text = self.font_manager.render_text(puzzle['title'], 22, self.colors.text)
            
            # 説明文を改行処理
            desc_lines = self._wrap_text(puzzle['description'], 20, 500)
            diff_text = self.font_manager.render_text(f"難易度: {puzzle['difficulty']}", 16, self.colors.text)
            
            # テキスト配置
            self.screen.blit(title_text, (button_rect.x + 20, button_rect.y + 15))
            
            # 説明文（複数行対応）
            for j, line in enumerate(desc_lines):
                line_surface = self.font_manager.render_text(line, 16, self.colors.text)
                self.screen.blit(line_surface, (button_rect.x + 20, button_rect.y + 40 + j * 20))
            
            # 難易度表示
            self.screen.blit(diff_text, (button_rect.x + 500, button_rect.y + 15))
    
    def draw_puzzle_active(self):
        """謎解き実行画面を描画"""
        if not self.active_puzzle_id:
            return
        
        puzzle_status = self.puzzle_system.get_puzzle_status(self.active_puzzle_id)
        
        # 謎解き情報パネル
        self.draw_panel(self.info_panel, "謎解き情報")
        
        info_y = self.info_panel.y + 40
        title_text = self.font_manager.render_text(puzzle_status['title'], 18, self.colors.text)  # フォントサイズ縮小
        
        # 説明文を改行処理（パネル幅に合わせて調整）
        desc_lines = self._wrap_text(puzzle_status['description'], 14, 450)  # 幅を450pxに調整
        stage_text = self.font_manager.render_text(f"現在のステージ: {puzzle_status.get('current_stage', 1)}", 14, self.colors.text)
        
        self.screen.blit(title_text, (self.info_panel.x + 15, info_y))
        
        # 説明文（複数行）- 行間を調整
        for i, line in enumerate(desc_lines):
            line_surface = self.font_manager.render_text(line, 14, self.colors.text)
            self.screen.blit(line_surface, (self.info_panel.x + 15, info_y + 25 + i * 18))  # 行間を18pxに調整
        
        # ステージ情報 - 位置を動的に計算
        stage_y = info_y + 25 + len(desc_lines) * 18 + 15
        # パネル内に収まるかチェック
        if stage_y + 20 <= self.info_panel.y + self.info_panel.height - 10:
            self.screen.blit(stage_text, (self.info_panel.x + 15, stage_y))
        
        # アイテムパネル
        self.draw_panel(self.items_panel, "アイテム")
        self.draw_items()
        
        # 組み合わせパネル
        self.draw_panel(self.combination_panel, "選択中のアイテム")
        self.draw_selected_items()
        
        # ボタン
        self.draw_buttons()
        
        # 進行状況
        self.draw_progress()
    
    def draw_panel(self, rect: pygame.Rect, title: str):
        """パネルを描画"""
        panel_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        panel_surface.fill(self.colors.panel)
        self.screen.blit(panel_surface, rect)
        pygame.draw.rect(self.screen, self.colors.border, rect, 2)
        
        title_text = self.font_manager.render_text(title, 18, self.colors.text)  # フォントサイズ縮小
        self.screen.blit(title_text, (rect.x + 15, rect.y + 8))
    
    def draw_items(self):
        """アイテム一覧を描画"""
        item_y = self.items_panel.y + 45
        
        for i, item in enumerate(self.available_items):
            item_rect = pygame.Rect(self.items_panel.x + 15, item_y + i * 40, 
                                  self.items_panel.width - 30, 35)  # 高さとマージンを調整
            
            # 選択状態の背景
            if item in self.selected_items:
                pygame.draw.rect(self.screen, self.colors.info, item_rect)
            else:
                pygame.draw.rect(self.screen, (255, 255, 255), item_rect)
            
            pygame.draw.rect(self.screen, self.colors.border, item_rect, 1)
            
            # アイテム名
            item_text = self.font_manager.render_text(item, 18, self.colors.text)
            self.screen.blit(item_text, (item_rect.x + 8, item_rect.y + 8))
    
    def draw_selected_items(self):
        """選択中のアイテムを描画"""
        if not self.selected_items:
            no_selection_text = self.font_manager.render_text("アイテムを選択してください", 16, self.colors.text)
            self.screen.blit(no_selection_text, (self.combination_panel.x + 15, self.combination_panel.y + 50))
            return
        
        # 選択されたアイテムを改行して表示（パネル幅に合わせて調整）
        selected_lines = self._wrap_items(self.selected_items, 16, 450)  # 幅を450pxに調整
        for i, line in enumerate(selected_lines):
            text_surface = self.font_manager.render_text(line, 16, self.colors.text)
            # パネル内に収まるかチェック
            y_pos = self.combination_panel.y + 50 + i * 22
            if y_pos + 22 <= self.combination_panel.y + self.combination_panel.height - 10:
                self.screen.blit(text_surface, (self.combination_panel.x + 15, y_pos))
    
    def draw_buttons(self):
        """ボタンを描画"""
        buttons = [
            (pygame.Rect(50, 480, 150, 40), "組み合わせ実行", self.colors.success),  # 位置調整
            (pygame.Rect(220, 480, 100, 40), "ヒント", self.colors.hint),  # 位置調整
            (pygame.Rect(340, 480, 100, 40), "リセット", self.colors.warning)  # 位置調整
        ]
        
        for button_rect, text, color in buttons:
            pygame.draw.rect(self.screen, color, button_rect)
            pygame.draw.rect(self.screen, self.colors.border, button_rect, 2)
            
            button_text = self.font_manager.render_text(text, 16, (255, 255, 255))  # フォントサイズ縮小
            text_rect = button_text.get_rect(center=button_rect.center)
            self.screen.blit(button_text, text_rect)
    
    def draw_progress(self):
        """進行状況を描画"""
        if not self.active_puzzle_id:
            return
        
        # アクティブな謎解きが存在するかチェック
        if self.active_puzzle_id not in self.puzzle_system.active_puzzles:
            return
        
        puzzle_status = self.puzzle_system.get_puzzle_status(self.active_puzzle_id)
        hint_status = self.hint_system.get_hint_status(self.active_puzzle_id)
        
        progress_y = 540  # 位置をさらに下に調整
        
        # 試行回数
        attempts_text = f"試行回数: {puzzle_status.get('attempts', 0)}"
        attempts_surface = self.font_manager.render_text(attempts_text, 16, self.colors.text)
        self.screen.blit(attempts_surface, (50, progress_y))
        
        # ヒント使用状況
        hints_text = f"ヒント: {hint_status.get('used_hints', 0)}/{hint_status.get('max_hints', 3)}"
        hints_surface = self.font_manager.render_text(hints_text, 16, self.colors.text)
        self.screen.blit(hints_surface, (200, progress_y))
        
        # 発見した組み合わせ
        combinations = puzzle_status.get('discovered_combinations', [])
        if combinations:
            combo_lines = self._wrap_items(combinations, 14, 700)  # 幅を拡大
            combo_text = f"発見した組み合わせ: {combo_lines[0] if combo_lines else ''}"
            combo_surface = self.font_manager.render_text(combo_text, 14, self.colors.success)
            self.screen.blit(combo_surface, (50, progress_y + 20))
            
            # 追加の組み合わせがある場合
            for i, line in enumerate(combo_lines[1:], 1):
                additional_surface = self.font_manager.render_text(f"  {line}", 14, self.colors.success)
                y_pos = progress_y + 20 + i * 18
                # 画面内に収まるかチェック
                if y_pos + 18 <= self.screen_height - 20:
                    self.screen.blit(additional_surface, (50, y_pos))
    
    def draw_message(self):
        """メッセージを描画"""
        if not self.current_message:
            return
        
        # メッセージの色を決定
        color_map = {
            "success": self.colors.success,
            "error": self.colors.error,
            "warning": self.colors.warning,
            "info": self.colors.info,
            "hint": self.colors.hint
        }
        text_color = color_map.get(self.message_type, self.colors.text)
        
        # メッセージ背景
        # 長いメッセージを改行処理
        message_lines = self._wrap_text(self.current_message, 20, 800)
        
        if message_lines:
            # 最初の行でサイズを計算
            first_line_surface = self.font_manager.render_text(message_lines[0], 20, text_color)
            message_rect = first_line_surface.get_rect(center=(self.screen_width // 2, self.screen_height - 80))
            
            # 背景パネル（複数行対応）
            panel_height = len(message_lines) * 25 + 20
            panel_rect = pygame.Rect(message_rect.x - 30, message_rect.y - 10, 
                                   max(600, message_rect.width + 60), panel_height)
            panel_surface = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
            panel_surface.fill(self.colors.panel)
            self.screen.blit(panel_surface, panel_rect)
            pygame.draw.rect(self.screen, text_color, panel_rect, 2)
            
            # メッセージテキスト（複数行）
            for i, line in enumerate(message_lines):
                line_surface = self.font_manager.render_text(line, 20, text_color)
                line_rect = line_surface.get_rect(center=(self.screen_width // 2, message_rect.y + i * 25))
                self.screen.blit(line_surface, line_rect)
    
    def _wrap_text(self, text: str, font_size: int, max_width: int) -> List[str]:
        """テキストを指定幅で改行"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            text_width = self.font_manager.get_text_size(test_line, font_size)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        return lines
    
    def _wrap_items(self, items: List[str], font_size: int, max_width: int) -> List[str]:
        """アイテムリストを指定幅で改行"""
        if not items:
            return []
        
        lines = []
        current_line = ""
        
        for i, item in enumerate(items):
            separator = " + " if i > 0 else ""
            test_line = current_line + separator + item
            text_width = self.font_manager.get_text_size(test_line, font_size)[0]
            
            if text_width <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = item
        
        if current_line:
            lines.append(current_line)
        
        return lines
