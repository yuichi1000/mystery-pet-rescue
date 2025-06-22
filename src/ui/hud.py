"""
HUD (Head-Up Display)

ゲーム中の情報表示UI
"""

import pygame
from typing import Dict, Any, Optional
from config.constants import *


class HUD:
    """HUDクラス"""
    
    def __init__(self):
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.visible = True
        
        # プレイヤー情報
        self.player_health = 100
        self.player_energy = 100
        self.player_level = 1
        self.player_exp = 0
        
        # ゲーム情報
        self.pets_found = 0
        self.pets_rescued = 0
        self.current_location = "住宅街"
        self.play_time = 0
        
        # ミニマップ
        self.minimap_size = 150
        self.minimap_x = SCREEN_WIDTH - self.minimap_size - 10
        self.minimap_y = 10
        
        # 通知システム
        self.notifications = []
        self.notification_duration = 3000  # ミリ秒
    
    def update(self, game_data: Dict[str, Any]):
        """HUDを更新"""
        # プレイヤー情報を更新
        player_data = game_data.get("player", {})
        self.player_health = player_data.get("health", 100)
        self.player_energy = player_data.get("energy", 100)
        self.player_level = player_data.get("level", 1)
        self.player_exp = player_data.get("exp", 0)
        
        # ゲーム情報を更新
        self.pets_found = game_data.get("pets_found", 0)
        self.pets_rescued = game_data.get("pets_rescued", 0)
        self.current_location = game_data.get("location", "住宅街")
        self.play_time = game_data.get("play_time", 0)
        
        # 通知を更新
        self._update_notifications()
    
    def render(self, screen: pygame.Surface):
        """HUDを描画"""
        if not self.visible:
            return
        
        # プレイヤー情報パネル
        self._render_player_info(screen)
        
        # ゲーム情報パネル
        self._render_game_info(screen)
        
        # ミニマップ
        self._render_minimap(screen)
        
        # 通知
        self._render_notifications(screen)
        
        # 操作ヒント
        self._render_controls_hint(screen)
    
    def _render_player_info(self, screen: pygame.Surface):
        """プレイヤー情報を描画"""
        panel_x = 10
        panel_y = 10
        panel_width = 200
        panel_height = 120
        
        # パネル背景
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, UI_BACKGROUND, panel_rect)
        pygame.draw.rect(screen, UI_BORDER, panel_rect, 2)
        
        # 体力バー
        self._render_bar(screen, panel_x + 10, panel_y + 20, 180, 15, 
                        self.player_health, 100, COLOR_RED, "体力")
        
        # エネルギーバー
        self._render_bar(screen, panel_x + 10, panel_y + 50, 180, 15,
                        self.player_energy, 100, COLOR_BLUE, "エネルギー")
        
        # レベル表示
        level_text = self.small_font.render(f"レベル: {self.player_level}", True, UI_TEXT)
        screen.blit(level_text, (panel_x + 10, panel_y + 80))
        
        # 経験値表示
        exp_text = self.small_font.render(f"EXP: {self.player_exp}", True, UI_TEXT)
        screen.blit(exp_text, (panel_x + 10, panel_y + 100))
    
    def _render_game_info(self, screen: pygame.Surface):
        """ゲーム情報を描画"""
        panel_x = 10
        panel_y = 140
        panel_width = 200
        panel_height = 100
        
        # パネル背景
        panel_rect = pygame.Rect(panel_x, panel_y, panel_width, panel_height)
        pygame.draw.rect(screen, UI_BACKGROUND, panel_rect)
        pygame.draw.rect(screen, UI_BORDER, panel_rect, 2)
        
        # 発見ペット数
        found_text = self.small_font.render(f"発見: {self.pets_found}", True, UI_TEXT)
        screen.blit(found_text, (panel_x + 10, panel_y + 10))
        
        # 救助ペット数
        rescued_text = self.small_font.render(f"救助: {self.pets_rescued}", True, UI_TEXT)
        screen.blit(rescued_text, (panel_x + 10, panel_y + 30))
        
        # 現在地
        location_text = self.small_font.render(f"場所: {self.current_location}", True, UI_TEXT)
        screen.blit(location_text, (panel_x + 10, panel_y + 50))
        
        # プレイ時間
        hours = self.play_time // 3600
        minutes = (self.play_time % 3600) // 60
        time_text = self.small_font.render(f"時間: {hours:02d}:{minutes:02d}", True, UI_TEXT)
        screen.blit(time_text, (panel_x + 10, panel_y + 70))
    
    def _render_minimap(self, screen: pygame.Surface):
        """ミニマップを描画"""
        # ミニマップ背景
        minimap_rect = pygame.Rect(self.minimap_x, self.minimap_y, 
                                  self.minimap_size, self.minimap_size)
        pygame.draw.rect(screen, UI_BACKGROUND, minimap_rect)
        pygame.draw.rect(screen, UI_BORDER, minimap_rect, 2)
        
        # タイトル
        title_text = self.small_font.render("マップ", True, UI_TEXT)
        screen.blit(title_text, (self.minimap_x + 5, self.minimap_y + 5))
        
        # プレイヤー位置（中央の赤い点）
        player_x = self.minimap_x + self.minimap_size // 2
        player_y = self.minimap_y + self.minimap_size // 2
        pygame.draw.circle(screen, COLOR_RED, (player_x, player_y), 3)
        
        # TODO: 実際のマップデータに基づいてペットや重要な場所を表示
        # 仮のペット位置表示
        for i in range(3):
            pet_x = self.minimap_x + 30 + i * 40
            pet_y = self.minimap_y + 40 + i * 20
            pygame.draw.circle(screen, COLOR_YELLOW, (pet_x, pet_y), 2)
    
    def _render_bar(self, screen: pygame.Surface, x: int, y: int, width: int, height: int,
                   current: int, maximum: int, color: tuple, label: str):
        """バーを描画"""
        # ラベル
        label_text = self.small_font.render(label, True, UI_TEXT)
        screen.blit(label_text, (x, y - 18))
        
        # 背景
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(screen, COLOR_GRAY, bg_rect)
        
        # バー
        if maximum > 0:
            bar_width = int(width * (current / maximum))
            bar_rect = pygame.Rect(x, y, bar_width, height)
            pygame.draw.rect(screen, color, bar_rect)
        
        # 枠線
        pygame.draw.rect(screen, UI_BORDER, bg_rect, 1)
        
        # 数値表示
        value_text = self.small_font.render(f"{current}/{maximum}", True, COLOR_WHITE)
        text_rect = value_text.get_rect(center=(x + width // 2, y + height // 2))
        screen.blit(value_text, text_rect)
    
    def _render_notifications(self, screen: pygame.Surface):
        """通知を描画"""
        for i, notification in enumerate(self.notifications):
            y = 50 + i * 40
            self._render_notification(screen, notification, y)
    
    def _render_notification(self, screen: pygame.Surface, notification: Dict[str, Any], y: int):
        """個別の通知を描画"""
        text = notification["text"]
        color = notification.get("color", COLOR_WHITE)
        
        # 背景
        text_surface = self.font.render(text, True, color)
        text_width = text_surface.get_width()
        
        bg_rect = pygame.Rect(SCREEN_WIDTH - text_width - 20, y, text_width + 10, 30)
        pygame.draw.rect(screen, COLOR_BLACK, bg_rect)
        pygame.draw.rect(screen, color, bg_rect, 2)
        
        # テキスト
        screen.blit(text_surface, (SCREEN_WIDTH - text_width - 15, y + 5))
    
    def _render_controls_hint(self, screen: pygame.Surface):
        """操作ヒントを描画"""
        hints = [
            "WASD: 移動",
            "SPACE: アクション",
            "TAB: メニュー",
            "I: インベントリ"
        ]
        
        y_start = SCREEN_HEIGHT - len(hints) * 25 - 10
        
        for i, hint in enumerate(hints):
            hint_text = self.small_font.render(hint, True, COLOR_WHITE)
            screen.blit(hint_text, (10, y_start + i * 25))
    
    def _update_notifications(self):
        """通知を更新"""
        current_time = pygame.time.get_ticks()
        
        # 期限切れの通知を削除
        self.notifications = [
            notification for notification in self.notifications
            if current_time - notification["timestamp"] < self.notification_duration
        ]
    
    def add_notification(self, text: str, color: tuple = COLOR_WHITE):
        """通知を追加"""
        notification = {
            "text": text,
            "color": color,
            "timestamp": pygame.time.get_ticks()
        }
        self.notifications.append(notification)
        
        # 最大5個まで
        if len(self.notifications) > 5:
            self.notifications.pop(0)
    
    def show(self):
        """HUDを表示"""
        self.visible = True
    
    def hide(self):
        """HUDを非表示"""
        self.visible = False
    
    def toggle(self):
        """HUDの表示/非表示を切り替え"""
        self.visible = not self.visible
