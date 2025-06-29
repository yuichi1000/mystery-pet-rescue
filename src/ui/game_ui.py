"""
ゲーム内UIシステム
ヘルスバー、スタミナバー、通知システムなど（エラーハンドリング強化版）
"""

import pygame
import math
import time
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from src.utils.font_manager import get_font_manager
from src.utils.asset_manager import get_asset_manager
from src.utils.language_manager import get_language_manager, get_text
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
        self.language_manager = get_language_manager()
        print("🔧 フォント・言語管理初期化完了")
        
        # 通知システム
        self.notifications: List[Notification] = []
        self.max_notifications = 5
        
        # 救出されたペットのリスト
        self.rescued_pets = []
        
        # クイックスロット
        self.quick_slots: List[Optional[QuickSlotItem]] = [None] * 4
        self.selected_slot = 0
        
        # 目標システム
        self.current_objective: Optional[GameObjective] = None
        
        # 色設定
        self.colors = {
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
        print("🎨 色設定完了")
        
        # アセットマネージャー取得
        self.asset_manager = get_asset_manager()
        
        print("🎮 ゲーム内UI初期化完了")
    
    def _load_ui_images(self):
        """UI画像を読み込み"""
        self.ui_images = {}
        ui_image_files = [
            'pet_rescue_icon.png',
            'score_icon.png', 
            'time_icon.png',
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
        print("🔧 UIレイアウト設定開始")
        
        # クイックスロットの位置
        slot_size = int(50 * self.ui_scale)
        slot_spacing = int(60 * self.ui_scale)
        start_x = (self.screen_width - (4 * slot_spacing - 10)) // 2
        
        self.quick_slot_rects = []
        for i in range(4):
            rect = pygame.Rect(
                start_x + i * slot_spacing,
                self.screen_height - int(80 * self.ui_scale),
                slot_size,
                slot_size
            )
            self.quick_slot_rects.append(rect)
        
        # 目標表示の位置
        self.objective_rect = pygame.Rect(
            int(20 * self.ui_scale),
            int(100 * self.ui_scale),
            int(300 * self.ui_scale),
            int(80 * self.ui_scale)
        )
    
    def set_timer_system(self, timer_system):
        """タイマーシステムを設定"""
        self.timer_system = timer_system
    
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
        # クイックスロット
        self._draw_quick_slots()
        
        # 現在の目標
        self._draw_objective()
        
        # 残り時間表示
        self._draw_timer()
        
        # 通知システム
        self._draw_notifications()
    
    def _draw_quick_slots(self):
        """救出されたペットを表示（クイックスロット枠を使用）"""
        for i, rect in enumerate(self.quick_slot_rects):
            # スロット背景
            bg_color = (60, 60, 60)
            border_color = (150, 150, 150)
            
            pygame.draw.rect(self.screen, bg_color, rect)
            pygame.draw.rect(self.screen, border_color, rect, 2)
            
            # 救出されたペットがあれば表示
            if i < len(self.rescued_pets):
                pet = self.rescued_pets[i]
                
                # ペット画像を読み込んで表示
                pet_type_str = str(pet['type']).lower().replace('pettype.', '')
                
                # ペットタイプに応じた画像パスを生成
                sprite_paths = {
                    'dog': f"pets/pet_dog_001_front.png",
                    'cat': f"pets/pet_cat_001_front.png", 
                    'rabbit': f"pets/pet_rabbit_001_front.png",
                    'bird': f"pets/pet_bird_001_front.png"
                }
                
                sprite_path = sprite_paths.get(pet_type_str)
                if sprite_path:
                    # 画像を枠サイズに合わせて読み込み
                    pet_image = self.asset_manager.load_image(sprite_path, (rect.width - 10, rect.height - 20))
                    
                    if pet_image:
                        # 画像を中央に配置
                        image_x = rect.x + 5
                        image_y = rect.y + 5
                        self.screen.blit(pet_image, (image_x, image_y))
                    else:
                        # 画像読み込み失敗時はフォールバック（円）
                        self._draw_pet_fallback_icon(rect, pet_type_str)
                else:
                    # 未知のペットタイプの場合もフォールバック
                    self._draw_pet_fallback_icon(rect, pet_type_str)
                
                # ペット名（小さく表示）
                name_font = self.font_manager.get_font('default', 10)
                name_surface = name_font.render(pet['name'], True, (255, 255, 255))
                name_x = rect.centerx - name_surface.get_width() // 2
                name_y = rect.bottom - 15
                self.screen.blit(name_surface, (name_x, name_y))
            
            # スロット番号
            num_surface = self.font_manager.render_text(
                str(i + 1), "default", int(12 * self.ui_scale), (200, 200, 200)
            )
            self.screen.blit(num_surface, (rect.x + 2, rect.y + 2))
    
    def _draw_pet_fallback_icon(self, rect: pygame.Rect, pet_type_str: str):
        """ペット画像のフォールバック表示（円アイコン）"""
        pet_colors = {
            'dog': (139, 69, 19),    # 茶色
            'cat': (255, 165, 0),    # オレンジ
            'rabbit': (255, 192, 203), # ピンク
            'bird': (135, 206, 235)   # 水色
        }
        
        color = pet_colors.get(pet_type_str, (128, 128, 128))
        
        # ペットアイコン（円）
        center_x = rect.centerx
        center_y = rect.centery - 5
        radius = min(rect.width, rect.height) // 3
        
        pygame.draw.circle(self.screen, color, (center_x, center_y), radius)
        pygame.draw.circle(self.screen, (255, 255, 255), (center_x, center_y), radius, 2)
    
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
            get_text("current_objective"), "default", int(14 * self.ui_scale), self.colors['text']
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
    
    def _draw_notifications(self):
        """通知を描画（左下に表示）"""
        notification_height = int(40 * self.ui_scale)
        notification_width = int(300 * self.ui_scale)
        margin = int(20 * self.ui_scale)
        
        # 左下から上に向かって表示
        for i, notification in enumerate(self.notifications):
            # 下から上に向かって配置
            y_pos = (self.screen_height - margin - 
                    (i + 1) * (notification_height + 5))
            
            # フェードアウト効果
            alpha = 255
            if notification.remaining_time < notification.fade_time:
                alpha = int(255 * (notification.remaining_time / notification.fade_time))
            
            # 通知背景
            bg_color = self.colors['notification_bg'][notification.notification_type]
            notification_surface = pygame.Surface((notification_width, notification_height), 
                                                pygame.SRCALPHA)
            notification_surface.fill((*bg_color, alpha))
            
            # 左下に配置
            notification_rect = pygame.Rect(
                margin,  # 左端からマージン
                y_pos,   # 下から上に向かって配置
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
    
    def _draw_timer(self):
        """残り時間を描画"""
        # タイマーシステムから残り時間を取得
        if hasattr(self, 'timer_system') and self.timer_system:
            remaining_time = self.timer_system.get_remaining_time()
        else:
            remaining_time = 300.0  # デフォルト5分
        
        # 時間を分:秒形式に変換
        minutes = int(remaining_time // 60)
        seconds = int(remaining_time % 60)
        time_text = f"{minutes:02d}:{seconds:02d}"
        
        # 警告色の判定
        is_warning = remaining_time <= 30
        text_color = (255, 100, 100) if is_warning else (255, 255, 255)
        
        # タイマー背景
        timer_bg_rect = pygame.Rect(
            self.screen_width // 2 - 80,
            20,
            160,
            50
        )
        
        # 警告時は赤色、通常時は黒色
        bg_color = (200, 50, 50, 180) if is_warning else (0, 0, 0, 180)
        timer_surface = pygame.Surface((160, 50), pygame.SRCALPHA)
        timer_surface.fill(bg_color)
        self.screen.blit(timer_surface, timer_bg_rect.topleft)
        
        # 枠線
        pygame.draw.rect(self.screen, text_color, timer_bg_rect, 2)
        
        # 時間テキスト
        timer_font = self.font_manager.get_font('default', 24)
        timer_text_surface = timer_font.render(time_text, True, text_color)
        text_rect = timer_text_surface.get_rect(center=timer_bg_rect.center)
        self.screen.blit(timer_text_surface, text_rect)
        
        # "残り時間" ラベル
        label_font = self.font_manager.get_font('default', 18)
        label_text = label_font.render(get_text("time_remaining"), True, text_color)
        label_rect = label_text.get_rect(centerx=timer_bg_rect.centerx, bottom=timer_bg_rect.top - 5)
        self.screen.blit(label_text, label_rect)
    
    def add_rescued_pet(self, pet_name: str, pet_type: str):
        """救出されたペットを追加"""
        rescued_pet = {
            'name': pet_name,
            'type': pet_type,
            'rescued_time': time.time()
        }
        self.rescued_pets.append(rescued_pet)
        print(f"🎉 救出ペット追加: {pet_name} ({pet_type})")
    
    def update_language(self):
        """言語設定を更新"""
        self.language_manager = get_language_manager()
        current_lang = self.language_manager.get_current_language()
        print(f"🌐 GameUI言語更新: {current_lang.value}")
    
    def clear_rescued_pets(self):
        """救出されたペットリストをクリア"""
        self.rescued_pets = []
    
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
                self.add_notification(get_text("objective_completed"), NotificationType.SUCCESS)
                print(f"🎉 目標達成: {self.current_objective.title}")
    
    def clear_objective(self):
        """目標をクリア"""
        self.current_objective = None
    
    def handle_input(self, event: pygame.event.Event):
        """入力処理"""
        if event.type == pygame.KEYDOWN:
            # クイックスロット選択
            if pygame.K_1 <= event.key <= pygame.K_4:
                slot_index = event.key - pygame.K_1
                self.selected_slot = slot_index
            
            # クイックスロット使用
            elif event.key == pygame.K_SPACE:
                self.use_quick_slot(self.selected_slot)
    
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
    
    def draw_timer(self, time_string: str, is_warning: bool = False):
        """タイマー表示"""
        # タイマー背景
        timer_bg_rect = pygame.Rect(
            self.screen_width // 2 - 80,
            20,
            160,
            50
        )
        
        # 警告時は赤色、通常時は黒色
        bg_color = (200, 50, 50, 180) if is_warning else (0, 0, 0, 180)
        timer_surface = pygame.Surface((160, 50), pygame.SRCALPHA)
        timer_surface.fill(bg_color)
        self.screen.blit(timer_surface, timer_bg_rect.topleft)
        
        # 枠線
        border_color = (255, 100, 100) if is_warning else (255, 255, 255)
        pygame.draw.rect(self.screen, border_color, timer_bg_rect, 2)
        
        # タイマーテキスト
        text_color = (255, 255, 255) if not is_warning else (255, 255, 100)
        timer_font = self.font_manager.get_font('default', 32)
        timer_text = timer_font.render(time_string, True, text_color)
        
        # 中央配置
        text_rect = timer_text.get_rect(center=timer_bg_rect.center)
        self.screen.blit(timer_text, text_rect)
        
        # "残り時間" ラベル
        label_font = self.font_manager.get_font('default', 18)
        label_text = label_font.render(get_text("time_remaining"), True, text_color)
        label_rect = label_text.get_rect(centerx=timer_bg_rect.centerx, bottom=timer_bg_rect.top - 5)
        self.screen.blit(label_text, label_rect)
    def _draw_rescued_pets(self):
        """救出されたペットを描画"""
        if not self.rescued_pets:
            return
        
