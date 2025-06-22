"""
メニューシーン
タイトル画面とメインメニューを管理
"""

import pygame
from typing import Optional, List
from src.core.scene import Scene
from src.utils.asset_manager import get_asset_manager
from src.utils.font_manager import get_font_manager

class MenuItem:
    """メニューアイテムクラス"""
    def __init__(self, text: str, action: str, rect: pygame.Rect):
        self.text = text
        self.action = action
        self.rect = rect
        self.hovered = False
        self.selected = False

class MenuScene(Scene):
    """メニューシーン"""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        
        # アセットマネージャー
        self.asset_manager = get_asset_manager()
        self.font_manager = get_font_manager()
        
        # 背景画像
        self.background_image = None
        self._load_background()
        
        # メニューアイテム
        self.menu_items: List[MenuItem] = []
        self.selected_index = 0
        
        # アニメーション用
        self.title_alpha = 255
        self.title_fade_direction = -1
        self.fade_speed = 50
        
        # 色設定
        self.normal_color = (255, 255, 255)
        self.hover_color = (255, 255, 0)
        self.selected_color = (0, 255, 0)
        
        self._create_menu_items()
    
    def _load_background(self):
        """背景画像を読み込み"""
        try:
            self.background_image = self.asset_manager.get_image("backgrounds/menu_background.png")
            if self.background_image:
                # 画面サイズに合わせてスケール
                screen_size = (self.screen.get_width(), self.screen.get_height())
                self.background_image = pygame.transform.scale(self.background_image, screen_size)
        except Exception as e:
            print(f"背景画像の読み込みに失敗: {e}")
            self.background_image = None
    
    def _create_menu_items(self):
        """メニューアイテムを作成"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # ボタンの配置
        button_width = 200
        button_height = 50
        button_x = screen_width // 2 - button_width // 2
        button_start_y = screen_height // 2
        button_spacing = 70
        
        # メニューアイテムを作成
        menu_data = [
            ("ゲーム開始", "game"),
            ("設定", "settings"),
            ("ゲーム終了", "quit")
        ]
        
        for i, (text, action) in enumerate(menu_data):
            rect = pygame.Rect(button_x, button_start_y + i * button_spacing, button_width, button_height)
            item = MenuItem(text, action, rect)
            self.menu_items.append(item)
        
        # 最初のアイテムを選択
        if self.menu_items:
            self.menu_items[self.selected_index].selected = True
    
    def enter(self) -> None:
        """シーンに入る時の処理"""
        print("メニューシーンに入りました")
        # タイトルアニメーションをリセット
        self.title_alpha = 255
        self.title_fade_direction = -1
    
    def exit(self) -> None:
        """シーンから出る時の処理"""
        print("メニューシーンから出ます")
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self._move_selection(-1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self._move_selection(1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self._activate_selected()
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                return "quit"
        
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_hover(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                return self._handle_mouse_click(event.pos)
        
        return None
    
    def _move_selection(self, direction: int):
        """選択を移動"""
        if not self.menu_items:
            return
        
        # 現在の選択を解除
        self.menu_items[self.selected_index].selected = False
        
        # 新しい選択インデックス
        self.selected_index = (self.selected_index + direction) % len(self.menu_items)
        
        # 新しい選択を設定
        self.menu_items[self.selected_index].selected = True
    
    def _activate_selected(self) -> str:
        """選択されたアイテムを実行"""
        if self.menu_items and 0 <= self.selected_index < len(self.menu_items):
            return self.menu_items[self.selected_index].action
        return "game"
    
    def _handle_mouse_hover(self, pos: tuple):
        """マウスホバー処理"""
        for i, item in enumerate(self.menu_items):
            if item.rect.collidepoint(pos):
                # ホバー状態を設定
                item.hovered = True
                # 選択も変更
                if i != self.selected_index:
                    self.menu_items[self.selected_index].selected = False
                    self.selected_index = i
                    item.selected = True
            else:
                item.hovered = False
    
    def _handle_mouse_click(self, pos: tuple) -> Optional[str]:
        """マウスクリック処理"""
        for item in self.menu_items:
            if item.rect.collidepoint(pos):
                return item.action
        return None
    
    def update(self, time_delta: float) -> Optional[str]:
        """更新処理"""
        # タイトルのフェードアニメーション
        self.title_alpha += self.title_fade_direction * self.fade_speed * time_delta
        
        if self.title_alpha <= 150:
            self.title_alpha = 150
            self.title_fade_direction = 1
        elif self.title_alpha >= 255:
            self.title_alpha = 255
            self.title_fade_direction = -1
        
        return None
    
    def draw(self, surface: pygame.Surface) -> None:
        """描画処理"""
        # 背景描画
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            # 背景画像がない場合はグラデーション背景
            self._draw_gradient_background(surface)
        
        # タイトルテキストを手動描画（アニメーション効果付き）
        self._draw_animated_title(surface)
        
        # メニューアイテムを描画
        self._draw_menu_items(surface)
        
        # 操作説明を描画
        self._draw_controls_help(surface)
    
    def _draw_menu_items(self, surface: pygame.Surface):
        """メニューアイテムを描画"""
        button_font = self.font_manager.get_font("default", 32)
        
        for item in self.menu_items:
            # 背景色を決定
            if item.selected:
                bg_color = (100, 100, 100)
                text_color = self.selected_color
            elif item.hovered:
                bg_color = (80, 80, 80)
                text_color = self.hover_color
            else:
                bg_color = (60, 60, 60)
                text_color = self.normal_color
            
            # 背景を描画
            pygame.draw.rect(surface, bg_color, item.rect)
            pygame.draw.rect(surface, text_color, item.rect, 2)
            
            # テキストを描画
            text_surface = button_font.render(item.text, True, text_color)
            text_rect = text_surface.get_rect(center=item.rect.center)
            surface.blit(text_surface, text_rect)
    
    def _draw_gradient_background(self, surface: pygame.Surface):
        """グラデーション背景を描画"""
        # 上から下へのグラデーション
        for y in range(surface.get_height()):
            ratio = y / surface.get_height()
            r = int(30 + (80 - 30) * ratio)
            g = int(50 + (120 - 50) * ratio)
            b = int(80 + (160 - 80) * ratio)
            color = (r, g, b)
            pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))
    
    def _draw_animated_title(self, surface: pygame.Surface):
        """アニメーション付きタイトルを描画"""
        # 大きなフォントでタイトルを描画
        title_font = self.font_manager.get_font("default", 48)
        title_text = "ミステリー・ペット・レスキュー"
        
        # アルファ値を適用したサーフェスを作成
        title_surface = title_font.render(title_text, True, (255, 255, 255))
        title_surface.set_alpha(int(self.title_alpha))
        
        # 中央に配置
        title_rect = title_surface.get_rect(center=(surface.get_width()//2, 150))
        surface.blit(title_surface, title_rect)
        
        # サブタイトル
        subtitle_font = self.font_manager.get_font("default", 24)
        subtitle_text = "〜 迷子のペットを救出するアドベンチャー 〜"
        subtitle_surface = subtitle_font.render(subtitle_text, True, (200, 200, 200))
        subtitle_rect = subtitle_surface.get_rect(center=(surface.get_width()//2, 200))
        surface.blit(subtitle_surface, subtitle_rect)
    
    def _draw_controls_help(self, surface: pygame.Surface):
        """操作説明を描画"""
        help_font = self.font_manager.get_font("default", 18)
        help_texts = [
            "↑↓/WS: 選択移動",
            "ENTER/SPACE: 決定",
            "ESC/Q: ゲーム終了",
            "マウス: ホバー＆クリック"
        ]
        
        y_offset = surface.get_height() - 80
        for i, text in enumerate(help_texts):
            help_surface = help_font.render(text, True, (150, 150, 150))
            help_rect = help_surface.get_rect(center=(surface.get_width()//2, y_offset + i * 25))
            surface.blit(help_surface, help_rect)
