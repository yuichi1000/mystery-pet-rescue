#!/usr/bin/env python3
"""
ゲーム内UIデモ
ヘルスバー、スタミナバー、ミニマップ、通知システムなどの動作確認
"""

import sys
import pygame
import random
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.game_ui import GameUI, NotificationType, QuickSlotItem
from src.entities.player import Player
from src.entities.pet import Pet, PetData, PetType
from src.utils.font_manager import get_font_manager

class GameUIDemo:
    """ゲーム内UIデモクラス"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        pygame.display.set_caption("ゲーム内UIデモ - 解像度対応UI")
        self.clock = pygame.time.Clock()
        
        # UI システム
        self.game_ui = GameUI(self.screen)
        self.font_manager = get_font_manager()
        
        # プレイヤー
        self.player = Player(400, 300)
        
        # ペット（ミニマップ表示用）
        self.pets = self._create_demo_pets()
        
        # デモ用タイマー
        self.demo_timer = 0.0
        self.notification_timer = 0.0
        self.damage_timer = 0.0
        
        # デモ設定
        self.auto_demo = True
        self.show_help = True
        
        # 初期設定
        self._setup_demo()
        
        print("🎮 ゲーム内UIデモ起動完了")
        print("🎯 機能:")
        print("  - ヘルス・スタミナバー")
        print("  - クイックスロット (1-6キー)")
        print("  - ミニマップ")
        print("  - 目標表示・進捗管理")
        print("  - 通知システム")
        print("  - 時間表示 (Tキーで切り替え)")
        print("  - 解像度対応スケーリング")
    
    def _create_demo_pets(self) -> list:
        """デモ用ペットを作成"""
        pets = []
        
        positions = [(600, 200), (800, 400), (300, 500), (900, 150)]
        pet_types = [PetType.CAT, PetType.DOG, PetType.CAT, PetType.DOG]
        names = ["ミケ", "ポチ", "シロ", "タロウ"]
        
        for i, (pos, pet_type, name) in enumerate(zip(positions, pet_types, names)):
            pet_data = PetData(
                pet_id=f"demo_pet_{i}",
                name=name,
                pet_type=pet_type,
                personality="フレンドリー",
                rarity="common",
                description=f"デモ用の{name}"
            )
            pet = Pet(pet_data, pos[0], pos[1])
            pets.append(pet)
        
        return pets
    
    def _setup_demo(self):
        """デモ初期設定"""
        # クイックスロットにアイテムを設定
        items = [
            QuickSlotItem("potion", "回復ポーション", "", 5, 0.0, 3.0),
            QuickSlotItem("food", "ペットフード", "", 10, 0.0, 1.0),
            QuickSlotItem("rope", "ロープ", "", 1, 0.0, 0.0),
            QuickSlotItem("flashlight", "懐中電灯", "", 1, 0.0, 5.0),
            QuickSlotItem("whistle", "笛", "", 1, 0.0, 2.0),
            QuickSlotItem("treat", "おやつ", "", 3, 0.0, 1.5)
        ]
        
        for i, item in enumerate(items):
            self.game_ui.set_quick_slot(i, item)
        
        # 初期目標設定
        self.game_ui.set_objective("ペットを見つけよう", "迷子のペットを3匹見つけて救出する", 3)
        
        # 初期通知
        self.game_ui.add_notification("ゲーム開始！", NotificationType.INFO)
        self.game_ui.add_notification("ペットを探しましょう", NotificationType.INFO, 4.0)
    
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
                
                elif event.type == pygame.VIDEORESIZE:
                    # 解像度変更対応
                    self.screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                    self.game_ui.resize(event.w, event.h)
                    self.game_ui.add_notification(f"解像度変更: {event.w}x{event.h}", NotificationType.INFO)
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_F1:
                        self.show_help = not self.show_help
                    elif event.key == pygame.K_F2:
                        self.auto_demo = not self.auto_demo
                        status = "ON" if self.auto_demo else "OFF"
                        self.game_ui.add_notification(f"自動デモ: {status}", NotificationType.INFO)
                    elif event.key == pygame.K_n:
                        self._trigger_random_notification()
                    elif event.key == pygame.K_h:
                        self._simulate_damage()
                    elif event.key == pygame.K_r:
                        self._simulate_heal()
                    elif event.key == pygame.K_o:
                        self._advance_objective()
                
                # UI入力処理
                self.game_ui.handle_input(event)
            
            # 更新
            self.update(time_delta)
            
            # 描画
            self.draw()
            
            pygame.display.flip()
        
        pygame.quit()
        print("🎉 ゲーム内UIデモ終了")
    
    def update(self, time_delta: float):
        """更新処理"""
        self.demo_timer += time_delta
        self.notification_timer += time_delta
        self.damage_timer += time_delta
        
        # プレイヤー更新
        keys = pygame.key.get_pressed()
        keys_pressed = set()
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            keys_pressed.add(pygame.K_LEFT)
            keys_pressed.add(pygame.K_a)
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            keys_pressed.add(pygame.K_RIGHT)
            keys_pressed.add(pygame.K_d)
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            keys_pressed.add(pygame.K_UP)
            keys_pressed.add(pygame.K_w)
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            keys_pressed.add(pygame.K_DOWN)
            keys_pressed.add(pygame.K_s)
        if keys[pygame.K_LSHIFT]:
            keys_pressed.add(pygame.K_LSHIFT)
        
        self.player.update(time_delta, keys_pressed)
        
        # ペット更新
        player_pos = self.player.get_position()
        for pet in self.pets:
            pet.update(time_delta, player_pos)
        
        # UI更新
        self.game_ui.update(time_delta)
        
        # 自動デモ
        if self.auto_demo:
            self._update_auto_demo(time_delta)
    
    def _update_auto_demo(self, time_delta: float):
        """自動デモ更新"""
        # 定期的な通知
        if self.notification_timer >= 8.0:
            self._trigger_random_notification()
            self.notification_timer = 0.0
        
        # 定期的なダメージ・回復
        if self.damage_timer >= 5.0:
            if random.random() < 0.6:
                self._simulate_damage()
            else:
                self._simulate_heal()
            self.damage_timer = 0.0
    
    def _trigger_random_notification(self):
        """ランダム通知を発生"""
        messages = [
            ("新しいエリアを発見しました", NotificationType.INFO),
            ("ペットを発見！", NotificationType.SUCCESS),
            ("スタミナが少なくなっています", NotificationType.WARNING),
            ("アイテムを入手しました", NotificationType.SUCCESS),
            ("危険なエリアに近づいています", NotificationType.WARNING),
            ("実績解除：探検家", NotificationType.ACHIEVEMENT),
            ("セーブが完了しました", NotificationType.INFO),
            ("ペットとの信頼関係が向上しました", NotificationType.SUCCESS)
        ]
        
        message, msg_type = random.choice(messages)
        self.game_ui.add_notification(message, msg_type)
    
    def _simulate_damage(self):
        """ダメージシミュレーション"""
        stats = self.player.get_stats()
        damage = random.randint(10, 30)
        stats.health = max(0, stats.health - damage)
        self.game_ui.add_notification(f"ダメージ: -{damage}", NotificationType.ERROR, 2.0)
    
    def _simulate_heal(self):
        """回復シミュレーション"""
        stats = self.player.get_stats()
        heal = random.randint(15, 25)
        stats.health = min(stats.max_health, stats.health + heal)
        self.game_ui.add_notification(f"回復: +{heal}", NotificationType.SUCCESS, 2.0)
    
    def _advance_objective(self):
        """目標進捗を進める"""
        if self.game_ui.current_objective and not self.game_ui.current_objective.completed:
            current_progress = self.game_ui.current_objective.progress
            self.game_ui.update_objective_progress(current_progress + 1)
            
            if self.game_ui.current_objective.completed:
                # 新しい目標を設定
                new_objectives = [
                    ("すべてのペットを救出", "残りのペットをすべて見つけて救出する", 5),
                    ("隠されたアイテムを発見", "秘密のアイテムを3つ見つける", 3),
                    ("エリアを完全探索", "マップの90%を探索する", 90)
                ]
                
                title, desc, max_prog = random.choice(new_objectives)
                self.game_ui.set_objective(title, desc, max_prog)
    
    def draw(self):
        """描画処理"""
        # 背景
        self.screen.fill((50, 100, 50))
        
        # 簡易マップ描画
        self._draw_demo_world()
        
        # プレイヤー描画
        self.player.draw(self.screen)
        
        # ペット描画
        for pet in self.pets:
            pet.draw(self.screen)
        
        # ゲームUI描画
        player_stats = {
            'health': self.player.stats.health,
            'max_health': self.player.stats.max_health,
            'stamina': self.player.stats.stamina,
            'max_stamina': self.player.stats.max_stamina
        }
        
        self.game_ui.draw(player_stats, self.pets, self.player.get_position())
        
        # ヘルプ表示
        if self.show_help:
            self._draw_help()
        
        # FPS表示
        fps_text = f"FPS: {int(self.clock.get_fps())}"
        fps_surface = self.font_manager.render_text(fps_text, 16, (255, 255, 0))
        self.screen.blit(fps_surface, (10, self.screen.get_height() - 30))
    
    def _draw_demo_world(self):
        """デモ用世界を描画"""
        # グリッド描画
        grid_size = 64
        for x in range(0, self.screen.get_width(), grid_size):
            pygame.draw.line(self.screen, (80, 120, 80), (x, 0), (x, self.screen.get_height()))
        for y in range(0, self.screen.get_height(), grid_size):
            pygame.draw.line(self.screen, (80, 120, 80), (0, y), (self.screen.get_width(), y))
        
        # ランダムな障害物
        obstacles = [
            (200, 150, 100, 50),
            (500, 300, 80, 80),
            (800, 100, 60, 120),
            (300, 400, 120, 40)
        ]
        
        for obstacle in obstacles:
            pygame.draw.rect(self.screen, (100, 50, 50), obstacle)
    
    def _draw_help(self):
        """ヘルプを描画"""
        help_texts = [
            "=== ゲーム内UIデモ ===",
            "WASD: プレイヤー移動",
            "1-6: クイックスロット選択",
            "Space: アイテム使用",
            "T: 時間表示切り替え",
            "",
            "=== デモ操作 ===",
            "N: ランダム通知",
            "H: ダメージシミュレーション",
            "R: 回復シミュレーション",
            "O: 目標進捗",
            "",
            "F1: ヘルプ表示切り替え",
            "F2: 自動デモ切り替え",
            "ESC: 終了"
        ]
        
        # ヘルプ背景
        help_width = 300
        help_height = len(help_texts) * 20 + 20
        help_rect = pygame.Rect(
            self.screen.get_width() - help_width - 20,
            self.screen.get_height() - help_height - 20,
            help_width,
            help_height
        )
        
        help_surface = pygame.Surface((help_width, help_height), pygame.SRCALPHA)
        help_surface.fill((0, 0, 0, 200))
        self.screen.blit(help_surface, help_rect)
        pygame.draw.rect(self.screen, (255, 255, 255), help_rect, 2)
        
        # ヘルプテキスト
        for i, text in enumerate(help_texts):
            if text.startswith("==="):
                color = (255, 255, 0)
                size = 14
            elif text == "":
                continue
            else:
                color = (255, 255, 255)
                size = 12
            
            text_surface = self.font_manager.render_text(text, size, color)
            self.screen.blit(text_surface, (help_rect.x + 10, help_rect.y + 10 + i * 20))

def main():
    """メイン関数"""
    print("🎮 ゲーム内UIデモ起動中...")
    
    try:
        demo = GameUIDemo()
        demo.run()
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
