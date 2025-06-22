#!/usr/bin/env python3
"""
UI解像度スケーリングテスト
異なる解像度でのUI表示確認
"""

import sys
import pygame
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.game_ui import GameUI, NotificationType, QuickSlotItem
from src.utils.font_manager import get_font_manager

class UIScalingTest:
    """UI解像度スケーリングテストクラス"""
    
    def __init__(self):
        pygame.init()
        
        # テスト解像度リスト
        self.resolutions = [
            (800, 600),    # 4:3
            (1024, 768),   # 4:3
            (1280, 720),   # 16:9 (基準)
            (1366, 768),   # 16:9
            (1920, 1080),  # 16:9
            (2560, 1440),  # 16:9
            (1280, 1024),  # 5:4
            (1440, 900),   # 16:10
        ]
        
        self.current_resolution_index = 2  # 1280x720から開始
        self.screen = pygame.display.set_mode(self.resolutions[self.current_resolution_index])
        pygame.display.set_caption("UI解像度スケーリングテスト")
        self.clock = pygame.time.Clock()
        
        # UI システム
        self.game_ui = GameUI(self.screen)
        self.font_manager = get_font_manager()
        
        # テスト用データ
        self._setup_test_data()
        
        print("🖥️ UI解像度スケーリングテスト起動完了")
        print("🎯 操作方法:")
        print("  R: 解像度切り替え")
        print("  N: 通知テスト")
        print("  ESC: 終了")
        print(f"📐 現在の解像度: {self.resolutions[self.current_resolution_index]}")
    
    def _setup_test_data(self):
        """テスト用データを設定"""
        # クイックスロット設定
        test_items = [
            QuickSlotItem("health_potion", "体力ポーション", "", 3, 0.0, 5.0),
            QuickSlotItem("mana_potion", "マナポーション", "", 2, 0.0, 3.0),
            QuickSlotItem("food", "食べ物", "", 10, 0.0, 1.0),
            QuickSlotItem("tool", "道具", "", 1, 0.0, 0.0),
            QuickSlotItem("key", "鍵", "", 1, 0.0, 0.0),
            QuickSlotItem("scroll", "巻物", "", 5, 2.5, 8.0)  # クールダウン中
        ]
        
        for i, item in enumerate(test_items):
            self.game_ui.set_quick_slot(i, item)
        
        # 目標設定
        self.game_ui.set_objective("UI表示テスト", "すべての解像度でUIが正しく表示されることを確認", 8)
        self.game_ui.update_objective_progress(self.current_resolution_index)
        
        # 初期通知
        self.game_ui.add_notification("UIスケーリングテスト開始", NotificationType.INFO)
        self.game_ui.add_notification("Rキーで解像度を切り替えてください", NotificationType.INFO, 5.0)
    
    def run(self):
        """メインループ"""
        running = True
        
        while running:
            time_delta = self.clock.tick(60) / 1000.0
            events = pygame.event.get()
            
            # イベント処理
            for event in events:
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_r:
                        self._switch_resolution()
                    elif event.key == pygame.K_n:
                        self._test_notification()
                
                # UI入力処理
                self.game_ui.handle_input(event)
            
            # 更新
            self.update(time_delta)
            
            # 描画
            self.draw()
            
            pygame.display.flip()
        
        pygame.quit()
        print("🎉 UI解像度スケーリングテスト終了")
    
    def _switch_resolution(self):
        """解像度を切り替え"""
        self.current_resolution_index = (self.current_resolution_index + 1) % len(self.resolutions)
        new_resolution = self.resolutions[self.current_resolution_index]
        
        # 画面サイズ変更
        self.screen = pygame.display.set_mode(new_resolution)
        
        # UIシステムに解像度変更を通知
        self.game_ui.resize(new_resolution[0], new_resolution[1])
        
        # 目標進捗更新
        self.game_ui.update_objective_progress(self.current_resolution_index + 1)
        
        # 通知
        resolution_text = f"{new_resolution[0]}x{new_resolution[1]}"
        aspect_ratio = f"{new_resolution[0]/new_resolution[1]:.2f}"
        scale_info = f"スケール: {self.game_ui.ui_scale:.2f}"
        
        self.game_ui.add_notification(f"解像度: {resolution_text}", NotificationType.INFO)
        self.game_ui.add_notification(f"アスペクト比: {aspect_ratio} | {scale_info}", NotificationType.INFO, 4.0)
        
        print(f"📐 解像度変更: {resolution_text} (スケール: {self.game_ui.ui_scale:.2f})")
    
    def _test_notification(self):
        """通知テスト"""
        import random
        
        test_notifications = [
            ("短いメッセージ", NotificationType.INFO),
            ("これは少し長めのメッセージです", NotificationType.SUCCESS),
            ("警告：非常に長いメッセージのテストです。UIが正しく表示されるかチェック", NotificationType.WARNING),
            ("エラーが発生しました", NotificationType.ERROR),
            ("実績解除：テスター", NotificationType.ACHIEVEMENT)
        ]
        
        message, msg_type = random.choice(test_notifications)
        self.game_ui.add_notification(message, msg_type)
    
    def update(self, time_delta: float):
        """更新処理"""
        # UI更新
        self.game_ui.update(time_delta)
    
    def draw(self):
        """描画処理"""
        # 背景グラデーション
        self._draw_gradient_background()
        
        # テスト用グリッド
        self._draw_test_grid()
        
        # ゲームUI描画
        test_player_stats = {
            'health': 75,
            'max_health': 100,
            'stamina': 60,
            'max_stamina': 100
        }
        
        # テスト用オブジェクト（ミニマップ表示用）
        test_objects = []
        
        self.game_ui.draw(test_player_stats, test_objects, (640, 360))
        
        # 解像度情報表示
        self._draw_resolution_info()
        
        # スケーリング情報表示
        self._draw_scaling_info()
    
    def _draw_gradient_background(self):
        """グラデーション背景を描画"""
        width, height = self.screen.get_size()
        
        for y in range(height):
            color_value = int(50 + (y / height) * 100)
            color = (color_value // 3, color_value // 2, color_value)
            pygame.draw.line(self.screen, color, (0, y), (width, y))
    
    def _draw_test_grid(self):
        """テスト用グリッドを描画"""
        width, height = self.screen.get_size()
        grid_size = int(50 * self.game_ui.ui_scale)
        
        # 縦線
        for x in range(0, width, grid_size):
            pygame.draw.line(self.screen, (100, 100, 100, 50), (x, 0), (x, height))
        
        # 横線
        for y in range(0, height, grid_size):
            pygame.draw.line(self.screen, (100, 100, 100, 50), (0, y), (width, y))
    
    def _draw_resolution_info(self):
        """解像度情報を描画"""
        width, height = self.screen.get_size()
        resolution_text = f"解像度: {width}x{height}"
        
        text_surface = self.font_manager.render_text(resolution_text, 24, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(width // 2, 50))
        
        # 背景
        bg_rect = pygame.Rect(text_rect.x - 20, text_rect.y - 10, 
                            text_rect.width + 40, text_rect.height + 20)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect, 2)
        
        self.screen.blit(text_surface, text_rect)
    
    def _draw_scaling_info(self):
        """スケーリング情報を描画"""
        width, height = self.screen.get_size()
        
        scaling_info = [
            f"UIスケール: {self.game_ui.ui_scale:.3f}",
            f"基準解像度: {self.game_ui.base_width}x{self.game_ui.base_height}",
            f"スケールX: {self.game_ui.scale_x:.3f}",
            f"スケールY: {self.game_ui.scale_y:.3f}",
            f"アスペクト比: {width/height:.3f}"
        ]
        
        info_y = height - 150
        for i, info in enumerate(scaling_info):
            info_surface = self.font_manager.render_text(info, 14, (255, 255, 255))
            self.screen.blit(info_surface, (20, info_y + i * 20))
        
        # 操作説明
        controls = [
            "R: 解像度切り替え",
            "N: 通知テスト",
            "1-6: クイックスロット",
            "T: 時間表示切り替え"
        ]
        
        control_y = height - 120
        for i, control in enumerate(controls):
            control_surface = self.font_manager.render_text(control, 12, (200, 200, 200))
            self.screen.blit(control_surface, (width - 200, control_y + i * 18))

def main():
    """メイン関数"""
    print("🖥️ UI解像度スケーリングテスト起動中...")
    
    try:
        test = UIScalingTest()
        test.run()
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
