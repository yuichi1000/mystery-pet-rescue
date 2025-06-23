"""
ゲーム内UIシステム
ヘルスバー、スタミナバー、ミニマップ、通知システムなど（エラーハンドリング強化版）
"""

import pygame
import math
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from src.utils.font_manager import get_font_manager
from src.utils.asset_manager import get_asset_manager
from src.utils.exceptions import UIError
from src.utils.error_handler import handle_error, safe_execute

class NotificationType(Enum):
    """通知タイプ"""
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    ERROR = "error"
    ACHIEVEMENT = "achievement"

@dataclass
class Notification:
    """通知データ"""
    message: str
    notification_type: NotificationType
    duration: float
    remaining_time: float
    fade_time: float = 1.0

@dataclass
class GameObjective:
    """ゲーム目標"""
    title: str
    description: str
    progress: int = 0
    max_progress: int = 1
    completed: bool = False

@dataclass
class QuickSlotItem:
    """クイックスロットアイテム"""
    item_id: str
    name: str
    icon_path: str = ""
    quantity: int = 1
    cooldown: float = 0.0
    max_cooldown: float = 0.0

class GameUI:
    """ゲーム内UIクラス"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # UI スケーリング
        self.base_width = 1280
        self.base_height = 720
        self.scale_x = self.screen_width / self.base_width
        self.scale_y = self.screen_height / self.base_height
        self.ui_scale = min(self.scale_x, self.scale_y)
        
        # フォント・アセット管理
        self.font_manager = get_font_manager()
        self.asset_manager = get_asset_manager()
        
        # UI画像の読み込み
        self._load_ui_images()
        
        # UI要素の位置とサイズ
        self._setup_ui_layout()
        
        # 通知システム
        self.notifications: List[Notification] = []
        self.max_notifications = 5
        
        # クイックスロット
        self.quick_slots: List[Optional[QuickSlotItem]] = [None] * 6
        self.selected_slot = 0
        
        # 目標システム
        self.current_objective: Optional[GameObjective] = None
        
        # 時間システム
        self.game_start_time = time.time()
        self.show_real_time = False
        
        # 色設定
        self.colors = {
            'health': (220, 20, 60),
            'health_bg': (100, 20, 20),
            'stamina': (255, 215, 0),
            'stamina_bg': (100, 100, 20),
            'ui_bg': (0, 0, 0, 180),
            'ui_border': (255, 255, 255, 100),
            'text': (255, 255, 255),
            'notification_bg': {
                NotificationType.INFO: (70, 130, 180),
                NotificationType.SUCCESS: (34, 139, 34),
                NotificationType.WARNING: (255, 140, 0),
                NotificationType.ERROR: (220, 20, 60),
                NotificationType.ACHIEVEMENT: (148, 0, 211)
            }
        }
        
        print("🎮 ゲーム内UI初期化完了")
    
    def _load_ui_images(self):
        """UI画像を読み込み"""
        self.ui_images = {}
        ui_image_files = [
            'pet_rescue_icon.png',
            'score_icon.png', 
            'time_icon.png',
            'settings_icon.png',
            'volume_icon.png'
        ]
        
        for image_file in ui_image_files:
            try:
                image = self.asset_manager.get_image(f"ui/{image_file}")
                if image:
                    # アイコンサイズを統一（32x32）
                    icon_size = int(32 * self.ui_scale)
                    image = pygame.transform.scale(image, (icon_size, icon_size))
                    self.ui_images[image_file.replace('.png', '')] = image
                    print(f"✅ UI画像読み込み: {image_file}")
                else:
                    print(f"⚠️ UI画像が見つかりません: {image_file}")
            except Exception as e:
                print(f"❌ UI画像読み込みエラー {image_file}: {e}")
    
    def _setup_ui_layout(self):
        """UIレイアウトを設定"""
        # ミニマップサイズを先に計算
        self.minimap_size = int(200 * self.ui_scale)
        self.minimap_zoom = 0.1
        self.minimap_surface = pygame.Surface((self.minimap_size, self.minimap_size))
        
        # ヘルス・スタミナバーの位置
        self.health_bar_rect = pygame.Rect(
            int(20 * self.ui_scale),
            int(20 * self.ui_scale),
            int(200 * self.ui_scale),
            int(20 * self.ui_scale)
        )
        
        self.stamina_bar_rect = pygame.Rect(
            int(20 * self.ui_scale),
            int(50 * self.ui_scale),
            int(200 * self.ui_scale),
            int(15 * self.ui_scale)
        )
        
        # クイックスロットの位置
        slot_size = int(50 * self.ui_scale)
        slot_spacing = int(60 * self.ui_scale)
        start_x = (self.screen_width - (6 * slot_spacing - 10)) // 2
        
        self.quick_slot_rects = []
        for i in range(6):
            rect = pygame.Rect(
                start_x + i * slot_spacing,
                self.screen_height - int(80 * self.ui_scale),
                slot_size,
                slot_size
            )
            self.quick_slot_rects.append(rect)
        
        # ミニマップの位置
        self.minimap_rect = pygame.Rect(
            self.screen_width - self.minimap_size - int(20 * self.ui_scale),
            int(20 * self.ui_scale),
            self.minimap_size,
            self.minimap_size
        )
        
        # 目標表示の位置
        self.objective_rect = pygame.Rect(
            int(20 * self.ui_scale),
            int(100 * self.ui_scale),
            int(300 * self.ui_scale),
            int(80 * self.ui_scale)
        )
        
        # 時間表示の位置
        self.time_rect = pygame.Rect(
            self.screen_width - int(150 * self.ui_scale),
            self.screen_height - int(40 * self.ui_scale),
            int(130 * self.ui_scale),
            int(30 * self.ui_scale)
        )
    
    def update(self, time_delta: float):
        """UI更新"""
        # 通知システム更新
        self._update_notifications(time_delta)
        
        # クイックスロットのクールダウン更新
        self._update_quick_slots(time_delta)
    
    def _update_notifications(self, time_delta: float):
        """通知を更新"""
        for notification in self.notifications[:]:
            notification.remaining_time -= time_delta
            if notification.remaining_time <= 0:
                self.notifications.remove(notification)
    
    def _update_quick_slots(self, time_delta: float):
        """クイックスロットを更新"""
        for slot in self.quick_slots:
            if slot and slot.cooldown > 0:
                slot.cooldown -= time_delta
                slot.cooldown = max(0, slot.cooldown)
    
    def draw(self, player_stats: Dict[str, Any], world_objects: List[Any] = None, 
             player_pos: Tuple[float, float] = (0, 0)):
        """UIを描画"""
        # ヘルス・スタミナバー
        self._draw_health_stamina_bars(player_stats)
        
        # クイックスロット
        self._draw_quick_slots()
        
        # ミニマップ
        self._draw_minimap(world_objects or [], player_pos)
        
        # 現在の目標
        self._draw_objective()
        
        # 時間表示
        self._draw_time()
        
        # 通知システム
        self._draw_notifications()
    
    def _draw_health_stamina_bars(self, player_stats: Dict[str, Any]):
        """ヘルス・スタミナバーを描画"""
        # ヘルスバー
        health = player_stats.get('health', 100)
        max_health = player_stats.get('max_health', 100)
        health_ratio = health / max_health if max_health > 0 else 0
        
        # ヘルスバー背景
        pygame.draw.rect(self.screen, self.colors['health_bg'], self.health_bar_rect)
        pygame.draw.rect(self.screen, self.colors['ui_border'], self.health_bar_rect, 2)
        
        # ヘルスバー本体
        health_width = int(self.health_bar_rect.width * health_ratio)
        health_fill_rect = pygame.Rect(
            self.health_bar_rect.x, self.health_bar_rect.y,
            health_width, self.health_bar_rect.height
        )
        pygame.draw.rect(self.screen, self.colors['health'], health_fill_rect)
        
        # ヘルステキスト
        health_text = f"HP: {int(health)}/{int(max_health)}"
        health_surface = self.font_manager.render_text(
            health_text, "default", int(14 * self.ui_scale), self.colors['text']
        )
        text_x = self.health_bar_rect.centerx - health_surface.get_width() // 2
        text_y = self.health_bar_rect.centery - health_surface.get_height() // 2
        self.screen.blit(health_surface, (text_x, text_y))
        
        # スタミナバー
        stamina = player_stats.get('stamina', 100)
        max_stamina = player_stats.get('max_stamina', 100)
        stamina_ratio = stamina / max_stamina if max_stamina > 0 else 0
        
        # スタミナバー背景
        pygame.draw.rect(self.screen, self.colors['stamina_bg'], self.stamina_bar_rect)
        pygame.draw.rect(self.screen, self.colors['ui_border'], self.stamina_bar_rect, 2)
        
        # スタミナバー本体
        stamina_width = int(self.stamina_bar_rect.width * stamina_ratio)
        stamina_fill_rect = pygame.Rect(
            self.stamina_bar_rect.x, self.stamina_bar_rect.y,
            stamina_width, self.stamina_bar_rect.height
        )
        pygame.draw.rect(self.screen, self.colors['stamina'], stamina_fill_rect)
        
        # スタミナテキスト
        stamina_text = f"SP: {int(stamina)}/{int(max_stamina)}"
        stamina_surface = self.font_manager.render_text(
            stamina_text, "default", int(12 * self.ui_scale), self.colors['text']
        )
        text_x = self.stamina_bar_rect.centerx - stamina_surface.get_width() // 2
        text_y = self.stamina_bar_rect.centery - stamina_surface.get_height() // 2
        self.screen.blit(stamina_surface, (text_x, text_y))
    
    def _draw_quick_slots(self):
        """クイックスロットを描画"""
        for i, (rect, slot) in enumerate(zip(self.quick_slot_rects, self.quick_slots)):
            # スロット背景
            is_selected = i == self.selected_slot
            bg_color = (100, 100, 150) if is_selected else (60, 60, 60)
            border_color = (255, 255, 255) if is_selected else (150, 150, 150)
            
            pygame.draw.rect(self.screen, bg_color, rect)
            pygame.draw.rect(self.screen, border_color, rect, 2)
            
            if slot:
                # アイテムアイコン（仮の色表示）
                icon_rect = pygame.Rect(
                    rect.x + 5, rect.y + 5,
                    rect.width - 10, rect.height - 20
                )
                pygame.draw.rect(self.screen, (200, 150, 100), icon_rect)
                
                # アイテム数量
                if slot.quantity > 1:
                    qty_text = str(slot.quantity)
                    qty_surface = self.font_manager.render_text(
                        qty_text, "default", int(12 * self.ui_scale), self.colors['text']
                    )
                    qty_x = rect.right - qty_surface.get_width() - 2
                    qty_y = rect.bottom - qty_surface.get_height() - 2
                    self.screen.blit(qty_surface, (qty_x, qty_y))
                
                # クールダウン表示
                if slot.cooldown > 0:
                    cooldown_ratio = slot.cooldown / slot.max_cooldown
                    cooldown_height = int(rect.height * cooldown_ratio)
                    cooldown_rect = pygame.Rect(
                        rect.x, rect.bottom - cooldown_height,
                        rect.width, cooldown_height
                    )
                    cooldown_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                    cooldown_surface.fill((0, 0, 0, 128))
                    self.screen.blit(cooldown_surface, rect)
            
            # スロット番号
            slot_num = str(i + 1)
            num_surface = self.font_manager.render_text(
                slot_num, "default", int(10 * self.ui_scale), self.colors['text']
            )
            self.screen.blit(num_surface, (rect.x + 2, rect.y + 2))
    
    def _draw_minimap(self, world_objects: List[Any], player_pos: Tuple[float, float]):
        """ミニマップを描画"""
        # ミニマップ背景
        self.minimap_surface.fill((50, 50, 50))
        
        # 世界の境界を計算（仮の値）
        world_width = 2000
        world_height = 2000
        
        # プレイヤー位置をミニマップ座標に変換
        map_player_x = int((player_pos[0] / world_width) * self.minimap_size)
        map_player_y = int((player_pos[1] / world_height) * self.minimap_size)
        
        # プレイヤーを中心とした表示範囲
        view_range = int(self.minimap_size * 0.3)
        
        # 地形の簡易表示（グリッド）
        grid_size = 20
        for x in range(0, self.minimap_size, grid_size):
            for y in range(0, self.minimap_size, grid_size):
                if (x + y) % 40 == 0:
                    pygame.draw.rect(self.minimap_surface, (80, 120, 80), 
                                   (x, y, grid_size, grid_size))
        
        # オブジェクト表示（ペットなど）
        for obj in world_objects:
            if hasattr(obj, 'get_position'):
                obj_pos = obj.get_position()
                map_obj_x = int((obj_pos[0] / world_width) * self.minimap_size)
                map_obj_y = int((obj_pos[1] / world_height) * self.minimap_size)
                
                # オブジェクトタイプに応じた色
                if hasattr(obj, 'data') and hasattr(obj.data, 'pet_type'):
                    color = (255, 100, 100)  # ペット
                else:
                    color = (100, 100, 255)  # その他
                
                pygame.draw.circle(self.minimap_surface, color, (map_obj_x, map_obj_y), 3)
        
        # プレイヤー位置
        pygame.draw.circle(self.minimap_surface, (255, 255, 0), 
                         (map_player_x, map_player_y), 4)
        
        # 視野範囲
        pygame.draw.circle(self.minimap_surface, (255, 255, 255), 
                         (map_player_x, map_player_y), view_range, 1)
        
        # ミニマップをメイン画面に描画
        pygame.draw.rect(self.screen, (0, 0, 0), self.minimap_rect)
        self.screen.blit(self.minimap_surface, self.minimap_rect)
        pygame.draw.rect(self.screen, self.colors['ui_border'], self.minimap_rect, 2)
        
        # ミニマップタイトル
        minimap_title = "ミニマップ"
        title_surface = self.font_manager.render_text(
            minimap_title, "default", int(12 * self.ui_scale), self.colors['text']
        )
        title_x = self.minimap_rect.centerx - title_surface.get_width() // 2
        title_y = self.minimap_rect.bottom + 5
        self.screen.blit(title_surface, (title_x, title_y))
    
    def _draw_objective(self):
        """現在の目標を描画"""
        if not self.current_objective:
            return
        
        # 目標パネル背景
        panel_surface = pygame.Surface((self.objective_rect.width, self.objective_rect.height), 
                                     pygame.SRCALPHA)
        panel_surface.fill(self.colors['ui_bg'])
        self.screen.blit(panel_surface, self.objective_rect)
        pygame.draw.rect(self.screen, self.colors['ui_border'], self.objective_rect, 2)
        
        # 目標タイトル
        title_surface = self.font_manager.render_text(
            "現在の目標", "default", int(14 * self.ui_scale), self.colors['text']
        )
        self.screen.blit(title_surface, (self.objective_rect.x + 10, self.objective_rect.y + 5))
        
        # 目標内容
        obj_title_surface = self.font_manager.render_text(
            self.current_objective.title, "default", int(16 * self.ui_scale), (255, 255, 0)
        )
        self.screen.blit(obj_title_surface, (self.objective_rect.x + 10, self.objective_rect.y + 25))
        
        # 進捗バー
        if self.current_objective.max_progress > 1:
            progress_ratio = self.current_objective.progress / self.current_objective.max_progress
            progress_bar_rect = pygame.Rect(
                self.objective_rect.x + 10, self.objective_rect.y + 50,
                self.objective_rect.width - 20, 15
            )
            
            # 進捗バー背景
            pygame.draw.rect(self.screen, (100, 100, 100), progress_bar_rect)
            
            # 進捗バー本体
            progress_width = int(progress_bar_rect.width * progress_ratio)
            progress_fill_rect = pygame.Rect(
                progress_bar_rect.x, progress_bar_rect.y,
                progress_width, progress_bar_rect.height
            )
            pygame.draw.rect(self.screen, (0, 255, 0), progress_fill_rect)
            
            # 進捗テキスト
            progress_text = f"{self.current_objective.progress}/{self.current_objective.max_progress}"
            progress_surface = self.font_manager.render_text(
                progress_text, "default", int(12 * self.ui_scale), self.colors['text']
            )
            text_x = progress_bar_rect.centerx - progress_surface.get_width() // 2
            text_y = progress_bar_rect.centery - progress_surface.get_height() // 2
            self.screen.blit(progress_surface, (text_x, text_y))
    
    def _draw_time(self):
        """時間表示を描画"""
        # 時間パネル背景
        panel_surface = pygame.Surface((self.time_rect.width, self.time_rect.height), 
                                     pygame.SRCALPHA)
        panel_surface.fill(self.colors['ui_bg'])
        self.screen.blit(panel_surface, self.time_rect)
        pygame.draw.rect(self.screen, self.colors['ui_border'], self.time_rect, 1)
        
        # 時間アイコンを表示
        icon_x = self.time_rect.x + 5
        if 'time_icon' in self.ui_images:
            icon = self.ui_images['time_icon']
            icon_y = self.time_rect.centery - icon.get_height() // 2
            self.screen.blit(icon, (icon_x, icon_y))
            text_start_x = icon_x + icon.get_width() + 5
        else:
            text_start_x = icon_x
        
        if self.show_real_time:
            # リアルタイム表示
            current_time = time.strftime("%H:%M:%S")
            time_text = f"時刻: {current_time}"
        else:
            # ゲーム時間表示
            elapsed_time = time.time() - self.game_start_time
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            time_text = f"プレイ時間: {hours:02d}:{minutes:02d}:{seconds:02d}"
        
        time_surface = self.font_manager.render_text(
            time_text, "default", int(12 * self.ui_scale), self.colors['text']
        )
        text_x = text_start_x
        text_y = self.time_rect.centery - time_surface.get_height() // 2
        self.screen.blit(time_surface, (text_x, text_y))
    
    def _draw_notifications(self):
        """通知を描画"""
        notification_height = int(40 * self.ui_scale)
        notification_width = int(300 * self.ui_scale)
        start_y = int(100 * self.ui_scale)
        
        for i, notification in enumerate(self.notifications):
            y_pos = start_y + i * (notification_height + 5)
            
            # フェードアウト効果
            alpha = 255
            if notification.remaining_time < notification.fade_time:
                alpha = int(255 * (notification.remaining_time / notification.fade_time))
            
            # 通知背景
            bg_color = self.colors['notification_bg'][notification.notification_type]
            notification_surface = pygame.Surface((notification_width, notification_height), 
                                                pygame.SRCALPHA)
            notification_surface.fill((*bg_color, alpha))
            
            notification_rect = pygame.Rect(
                self.screen_width - notification_width - 20,
                y_pos,
                notification_width,
                notification_height
            )
            
            self.screen.blit(notification_surface, notification_rect)
            pygame.draw.rect(self.screen, (255, 255, 255, alpha), notification_rect, 2)
            
            # 通知テキスト
            text_surface = self.font_manager.render_text(
                notification.message, "default", int(14 * self.ui_scale), self.colors['text']
            )
            text_surface.set_alpha(alpha)
            
            text_x = notification_rect.x + 10
            text_y = notification_rect.centery - text_surface.get_height() // 2
            self.screen.blit(text_surface, (text_x, text_y))
    
    # 公開メソッド
    def add_notification(self, message: str, notification_type: NotificationType = NotificationType.INFO, 
                        duration: float = 3.0):
        """通知を追加"""
        notification = Notification(
            message=message,
            notification_type=notification_type,
            duration=duration,
            remaining_time=duration
        )
        
        self.notifications.append(notification)
        
        # 最大数を超えた場合は古いものを削除
        if len(self.notifications) > self.max_notifications:
            self.notifications.pop(0)
        
        print(f"📢 通知追加: {message}")
    
    def set_quick_slot(self, slot_index: int, item: QuickSlotItem):
        """クイックスロットにアイテムを設定"""
        if 0 <= slot_index < len(self.quick_slots):
            self.quick_slots[slot_index] = item
            print(f"🎒 クイックスロット{slot_index + 1}に{item.name}を設定")
    
    def use_quick_slot(self, slot_index: int) -> Optional[QuickSlotItem]:
        """クイックスロットのアイテムを使用"""
        if 0 <= slot_index < len(self.quick_slots):
            slot = self.quick_slots[slot_index]
            if slot and slot.cooldown <= 0:
                # クールダウン開始
                slot.cooldown = slot.max_cooldown
                
                # 数量減少
                slot.quantity -= 1
                if slot.quantity <= 0:
                    self.quick_slots[slot_index] = None
                
                print(f"🎯 {slot.name}を使用")
                return slot
        return None
    
    def set_objective(self, title: str, description: str, max_progress: int = 1):
        """目標を設定"""
        self.current_objective = GameObjective(
            title=title,
            description=description,
            max_progress=max_progress
        )
        print(f"🎯 新しい目標: {title}")
    
    def update_stats(self, stats: dict):
        """統計情報を更新"""
        # プレイヤー統計の更新
        if 'player' in stats:
            player_stats = stats['player']
            # 必要に応じてプレイヤー統計を表示用に保存
            
        # ペット統計の更新
        if 'pets' in stats:
            pet_stats = stats['pets']
            # ペット統計を表示用に保存
            
        # その他の統計情報の更新
        # 実際の表示は draw メソッドで行う
    
    def update_objective_progress(self, progress: int):
        """目標の進捗を更新"""
        if self.current_objective:
            self.current_objective.progress = min(progress, self.current_objective.max_progress)
            
            if self.current_objective.progress >= self.current_objective.max_progress:
                self.current_objective.completed = True
                self.add_notification("目標達成！", NotificationType.SUCCESS)
                print(f"🎉 目標達成: {self.current_objective.title}")
    
    def clear_objective(self):
        """目標をクリア"""
        self.current_objective = None
    
    def toggle_time_display(self):
        """時間表示を切り替え"""
        self.show_real_time = not self.show_real_time
    
    def handle_input(self, event: pygame.event.Event):
        """入力処理"""
        if event.type == pygame.KEYDOWN:
            # クイックスロット選択
            if pygame.K_1 <= event.key <= pygame.K_6:
                slot_index = event.key - pygame.K_1
                self.selected_slot = slot_index
            
            # クイックスロット使用
            elif event.key == pygame.K_SPACE:
                self.use_quick_slot(self.selected_slot)
            
            # 時間表示切り替え
            elif event.key == pygame.K_t:
                self.toggle_time_display()
    
    def resize(self, new_width: int, new_height: int):
        """画面サイズ変更に対応"""
        self.screen_width = new_width
        self.screen_height = new_height
        
        # スケーリング再計算
        self.scale_x = self.screen_width / self.base_width
        self.scale_y = self.screen_height / self.base_height
        self.ui_scale = min(self.scale_x, self.scale_y)
        
        # UIレイアウト再設定
        self._setup_ui_layout()
        
        print(f"🖥️ UI解像度変更: {new_width}x{new_height} (スケール: {self.ui_scale:.2f})")
