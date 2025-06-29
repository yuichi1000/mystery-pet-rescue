"""
結果画面シーン
ゲーム終了時の結果表示とスコア計算
"""

import pygame
from typing import Optional, Dict, Any, List
from src.core.scene import Scene
from src.utils.font_manager import get_font_manager
from src.utils.language_manager import get_language_manager, get_text
from src.utils.asset_manager import get_asset_manager

class ResultButton:
    """結果画面のボタンクラス"""
    def __init__(self, text: str, action: str, rect: pygame.Rect):
        self.text = text
        self.action = action
        self.rect = rect
        self.hovered = False
        self.selected = False

class ResultScene(Scene):
    """結果画面シーン"""
    
    def __init__(self, screen: pygame.Surface, game_result: Dict[str, Any]):
        super().__init__(screen)
        self.game_result = game_result
        self.font_manager = get_font_manager()
        self.asset_manager = get_asset_manager()
        
        # 結果データ
        self.victory = game_result.get('victory', False)
        self.game_over = game_result.get('game_over', False)
        self.defeat_reason = game_result.get('defeat_reason', None)
        self.pets_rescued = game_result.get('pets_rescued', 0)
        self.total_pets = game_result.get('total_pets', 4)
        self.time_taken = game_result.get('time_taken', 0)
        self.remaining_time = game_result.get('remaining_time', 0)
        self.score = game_result.get('score', 0)
        self.completion_rate = (self.pets_rescued / self.total_pets) * 100 if self.total_pets > 0 else 0
        
        # ボタン
        self.buttons: List[ResultButton] = []
        self.selected_index = 0
        
        # 背景画像の読み込み
        self.background_image = None
        self.background_color = (30, 50, 80)  # フォールバック色
        self._load_background()
        
        # 色設定
        self.normal_color = (255, 255, 255)
        self.hover_color = (255, 255, 0)
        self.selected_color = (0, 255, 0)
        
        self._create_buttons()
    
    def _create_buttons(self):
        """ボタンを作成"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # ボタン配置
        button_y = screen_height - 150
        button_width = 150
        button_height = 50
        button_spacing = 180
        
        # ボタンデータ
        button_data = [
            (get_text("play_again"), "game"),
            (get_text("return_to_menu"), "menu"),
            (get_text("quit"), "quit")
        ]
        
        for i, (text, action) in enumerate(button_data):
            x = screen_width//2 - button_spacing + i * button_spacing - button_width//2
            rect = pygame.Rect(x, button_y, button_width, button_height)
            button = ResultButton(text, action, rect)
            self.buttons.append(button)
        
        # 最初のボタンを選択
        if self.buttons:
            self.buttons[self.selected_index].selected = True
    
    def _calculate_score(self) -> int:
        """スコアを計算"""
        base_score = self.pets_rescued * 1000
        time_bonus = max(0, 300 - int(self.time_taken)) * 10  # 5分以内でボーナス
        completion_bonus = 2000 if self.pets_rescued == self.total_pets else 0
        
        return base_score + time_bonus + completion_bonus
    
    def _get_rank(self) -> str:
        """ランクを取得"""
        if self.victory and self.completion_rate == 100:
            if self.remaining_time > 120:  # 2分以上残り
                return get_text("perfect")
            elif self.remaining_time > 60:  # 1分以上残り
                return get_text("excellent")
            else:
                return get_text("good")
        elif self.completion_rate >= 75:
            return get_text("good")
        elif self.completion_rate >= 50:
            return get_text("try_again")
        else:
            return get_text("try_again")
    
    def _load_background(self):
        """背景画像を読み込み"""
        try:
            self.background_image = self.asset_manager.get_image("backgrounds/result_background.png")
            if self.background_image:
                print(f"✅ リザルト背景画像読み込み成功: {self.background_image.get_size()}")
                # 画面サイズに合わせてスケール
                screen_size = (self.screen.get_width(), self.screen.get_height())
                self.background_image = pygame.transform.scale(self.background_image, screen_size)
                print(f"✅ リザルト背景画像スケール完了: {screen_size}")
            else:
                print("⚠️ リザルト背景画像が見つかりません")
        except Exception as e:
            print(f"❌ リザルト背景画像読み込みエラー: {e}")
            self.background_image = None
    
    def enter(self) -> None:
        """シーンに入る時の処理"""
        # スコアを再計算
        self.score = self._calculate_score()
    
    def exit(self) -> None:
        """シーンから出る時の処理"""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                self._move_selection(-1)
            elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                self._move_selection(1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self._activate_selected()
            elif event.key == pygame.K_ESCAPE:
                return "menu"
            elif event.key == pygame.K_r:
                return "game"
            elif event.key == pygame.K_q:
                return "quit"
        
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_hover(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                return self._handle_mouse_click(event.pos)
        
        return None
    
    def _move_selection(self, direction: int):
        """選択を移動"""
        if not self.buttons:
            return
        
        # 現在の選択を解除
        self.buttons[self.selected_index].selected = False
        
        # 新しい選択インデックス
        self.selected_index = (self.selected_index + direction) % len(self.buttons)
        
        # 新しい選択を設定
        self.buttons[self.selected_index].selected = True
    
    def _activate_selected(self) -> str:
        """選択されたボタンを実行"""
        if self.buttons and 0 <= self.selected_index < len(self.buttons):
            return self.buttons[self.selected_index].action
        return "menu"
    
    def _handle_mouse_hover(self, pos: tuple):
        """マウスホバー処理"""
        for i, button in enumerate(self.buttons):
            if button.rect.collidepoint(pos):
                button.hovered = True
                if i != self.selected_index:
                    self.buttons[self.selected_index].selected = False
                    self.selected_index = i
                    button.selected = True
            else:
                button.hovered = False
    
    def _handle_mouse_click(self, pos: tuple) -> Optional[str]:
        """マウスクリック処理"""
        for button in self.buttons:
            if button.rect.collidepoint(pos):
                return button.action
        return None
    
    def update(self, time_delta: float) -> Optional[str]:
        """更新処理"""
        return None
    
    def draw(self, surface: pygame.Surface) -> None:
        """描画処理"""
        # 背景画像または背景色
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            # フォールバック：背景色とグラデーション
            surface.fill(self.background_color)
            
            # グラデーション効果（簡易版）
            for i in range(surface.get_height() // 4):
                alpha = int(50 * (1 - i / (surface.get_height() // 4)))
                color = (self.background_color[0] + alpha, 
                        self.background_color[1] + alpha, 
                        self.background_color[2] + alpha)
                pygame.draw.line(surface, color, (0, i * 4), (surface.get_width(), i * 4))
        
        # タイトル描画
        self._draw_title(surface)
        
        # 統計情報描画
        self._draw_stats(surface)
        
        # ランク表示
        self._draw_rank(surface)
        
        # 完全クリア時の特別メッセージ
        if self.victory and self.pets_rescued == self.total_pets:
            self._draw_congratulations(surface)
        
        # ボタン描画
        self._draw_buttons(surface)
        
        # 操作説明
        self._draw_controls_help(surface)
    
    def _draw_title(self, surface: pygame.Surface):
        """タイトルを描画"""
        # 結果に応じたタイトルと色を決定
        if self.victory:
            title_text = get_text("game_complete")
            title_color = (0, 255, 0)  # 緑色（勝利）
        elif self.defeat_reason == "time_up":
            title_text = get_text("time_up")
            title_color = (255, 165, 0)  # オレンジ色（時間切れ）
        elif self.game_over:
            title_text = get_text("mission_failed")
            title_color = (255, 100, 100)  # 赤色（失敗）
        else:
            title_text = get_text("game_result")
            title_color = (255, 255, 255)  # 白色（デフォルト）
        
        title_font = self.font_manager.get_font("default", 72)
        title_surface = title_font.render(title_text, True, title_color)
        title_rect = title_surface.get_rect(center=(surface.get_width()//2, 100))
        surface.blit(title_surface, title_rect)
    
    def _draw_stats(self, surface: pygame.Surface):
        """統計情報を描画"""
        stats_font = self.font_manager.get_font("default", 36)
        stats_y = 180
        stats_spacing = 50
        
        # 統計データ（言語対応）
        stats_data = [
            f"{get_text('pets_rescued')}: {self.pets_rescued} / {self.total_pets}",
            f"{get_text('completion_rate')}: {self.completion_rate:.1f}%",
            f"{get_text('time_taken')}: {int(self.time_taken // 60):02d}:{int(self.time_taken % 60):02d}",
            f"{get_text('total_score')}: {self.score:,}"
        ]
        
        # 時間切れでない場合はタイムボーナスを表示
        if self.victory or (self.remaining_time > 0):
            time_bonus = int(self.remaining_time * 10)
            stats_data.insert(-1, f"{get_text('time_bonus')}: {time_bonus:,}")
        
        for i, text in enumerate(stats_data):
            stats_surface = stats_font.render(text, True, (255, 255, 255))
            stats_rect = stats_surface.get_rect(center=(surface.get_width()//2, stats_y + i * stats_spacing))
            surface.blit(stats_surface, stats_rect)
    
    def _draw_rank(self, surface: pygame.Surface):
        """ランクを描画"""
        rank = self._get_rank()
        rank_color = self._get_rank_color(rank)
        rank_font = self.font_manager.get_font("default", 72)
        rank_surface = rank_font.render(f"{get_text('rank')}: {rank}", True, rank_color)
        rank_rect = rank_surface.get_rect(center=(surface.get_width()//2, 400))
        surface.blit(rank_surface, rank_rect)
    
    def _draw_congratulations(self, surface: pygame.Surface):
        """おめでとうメッセージを描画"""
        congrats_text = get_text("congratulations") + get_text("exclamation") + get_text("all_pets_rescued")
        congrats_font = self.font_manager.get_font("default", 36)
        congrats_surface = congrats_font.render(congrats_text, True, (255, 215, 0))
        congrats_rect = congrats_surface.get_rect(center=(surface.get_width()//2, 450))
        surface.blit(congrats_surface, congrats_rect)
    
    def _draw_buttons(self, surface: pygame.Surface):
        """ボタンを描画"""
        button_font = self.font_manager.get_font("default", 32)
        
        for button in self.buttons:
            # 背景色を決定
            if button.selected:
                bg_color = (100, 100, 100)
                text_color = self.selected_color
            elif button.hovered:
                bg_color = (80, 80, 80)
                text_color = self.hover_color
            else:
                bg_color = (60, 60, 60)
                text_color = self.normal_color
            
            # 背景を描画
            pygame.draw.rect(surface, bg_color, button.rect)
            pygame.draw.rect(surface, text_color, button.rect, 2)
            
            # テキストを描画
            text_surface = button_font.render(button.text, True, text_color)
            text_rect = text_surface.get_rect(center=button.rect.center)
            surface.blit(text_surface, text_rect)
    
    def _draw_controls_help(self, surface: pygame.Surface):
        """操作説明を描画"""
        help_font = self.font_manager.get_font("default", 18)
        help_texts = [
            get_text("controls_select"),
            get_text("controls_confirm"),
            get_text("controls_restart_menu_quit")
        ]
        
        y_offset = surface.get_height() - 80
        for i, text in enumerate(help_texts):
            help_surface = help_font.render(text, True, (150, 150, 150))
            help_rect = help_surface.get_rect(center=(surface.get_width()//2, y_offset + i * 25))
            surface.blit(help_surface, help_rect)
    
    def _get_rank_color(self, rank: str) -> tuple:
        """ランクに応じた色を取得"""
        if rank == get_text("perfect"):
            return (255, 215, 0)    # ゴールド
        elif rank == get_text("excellent"):
            return (192, 192, 192)  # シルバー
        elif rank == get_text("good"):
            return (0, 255, 0)      # グリーン
        elif rank == get_text("try_again"):
            return (255, 165, 0)    # オレンジ
        else:
            return (255, 255, 255)  # 白（デフォルト）
