#!/usr/bin/env python3
"""
アセット統合デモ
実際の画像素材を使用したゲームデモ
"""

import sys
import pygame
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.asset_manager import get_asset_manager
from src.entities.player import Player
from src.entities.pet import Pet, PetData, PetType
from src.systems.sprite_manager import SpriteManager
from src.utils.font_manager import get_font_manager

class AssetIntegrationDemo:
    """アセット統合デモクラス"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("アセット統合デモ - 実際の素材を使用")
        self.clock = pygame.time.Clock()
        
        # アセット管理
        self.asset_manager = get_asset_manager()
        self.font_manager = get_font_manager()
        
        # スプライト管理
        self.sprite_manager = SpriteManager()
        
        # プレイヤー
        self.player = Player(400, 300)
        
        # ペット
        self.pets = self._create_pets()
        
        # カメラ
        self.camera_x = 0
        self.camera_y = 0
        
        # UI
        self.show_debug = True
        self.interaction_message = ""
        self.message_timer = 0.0
        
        # アセット事前読み込み
        self.loaded_assets = self.asset_manager.preload_all_assets()
        
        print("🎨 アセット統合デモ起動完了")
        print("🎯 機能:")
        print("  - 実際のプレイヤー・ペットスプライト表示")
        print("  - タイルベースマップ")
        print("  - ペットとの相互作用")
        print("  - 信頼度システム")
        print("  - F1: デバッグ表示切り替え")
    
    def _create_pets(self) -> list:
        """ペットを作成"""
        pets = []
        
        # 猫
        cat_data = PetData(
            pet_id="pet_cat_001",
            name="ミケ",
            pet_type=PetType.CAT,
            personality="好奇心旺盛",
            rarity="common",
            description="人懐っこい三毛猫"
        )
        cat = Pet(cat_data, 600, 200)
        pets.append(cat)
        
        # 犬
        dog_data = PetData(
            pet_id="pet_dog_001",
            name="ポチ",
            pet_type=PetType.DOG,
            personality="忠実",
            rarity="common",
            description="忠実な柴犬"
        )
        dog = Pet(dog_data, 800, 400)
        pets.append(dog)
        
        return pets
    
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
                    if event.key == pygame.K_F1:
                        self.show_debug = not self.show_debug
                    elif event.key == pygame.K_SPACE:
                        self._interact_with_pets()
            
            # 更新
            self.update(time_delta)
            
            # 描画
            self.draw()
            
            pygame.display.flip()
        
        pygame.quit()
        print("🎉 アセット統合デモ終了")
    
    def update(self, time_delta: float):
        """更新処理"""
        # キー入力取得（修正版）
        keys = pygame.key.get_pressed()
        keys_pressed = set()
        
        # 移動キーをチェック
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
        
        # プレイヤー更新
        self.player.update(time_delta, keys_pressed)
        
        # ペット更新
        player_pos = self.player.get_position()
        for pet in self.pets:
            pet.update(time_delta, player_pos)
        
        # カメラ更新
        self._update_camera()
        
        # メッセージタイマー更新
        if self.message_timer > 0:
            self.message_timer -= time_delta
            if self.message_timer <= 0:
                self.interaction_message = ""
    
    def _update_camera(self):
        """カメラを更新"""
        # プレイヤーを中心にカメラを配置
        player_center = self.player.get_center()
        self.camera_x = player_center[0] - self.screen.get_width() // 2
        self.camera_y = player_center[1] - self.screen.get_height() // 2
    
    def _interact_with_pets(self):
        """ペットとの相互作用"""
        player_pos = self.player.get_position()
        
        for pet in self.pets:
            if pet.interact(player_pos):
                # 救出可能
                if pet.rescue():
                    self.interaction_message = f"{pet.data.name}を救出しました！"
                    self.message_timer = 3.0
                else:
                    self.interaction_message = f"{pet.data.name}との信頼関係を築いています..."
                    self.message_timer = 2.0
                break
    
    def draw(self):
        """描画処理"""
        # 背景
        self.screen.fill((50, 150, 50))  # 緑の背景
        
        # タイル描画（簡易版）
        self._draw_simple_tiles()
        
        # プレイヤー描画
        self.player.draw(self.screen, (self.camera_x, self.camera_y))
        
        # ペット描画
        for pet in self.pets:
            pet.draw(self.screen, (self.camera_x, self.camera_y))
        
        # UI描画
        self._draw_ui()
        
        # デバッグ情報
        if self.show_debug:
            self._draw_debug_info()
    
    def _draw_simple_tiles(self):
        """簡易タイル描画"""
        # タイルサイズ
        tile_size = 64
        
        # 画面に表示される範囲のタイルを計算
        start_x = int(self.camera_x // tile_size) - 1
        start_y = int(self.camera_y // tile_size) - 1
        end_x = start_x + (self.screen.get_width() // tile_size) + 3
        end_y = start_y + (self.screen.get_height() // tile_size) + 3
        
        # タイル描画
        for y in range(start_y, end_y):
            for x in range(start_x, end_x):
                tile_x = x * tile_size - self.camera_x
                tile_y = y * tile_size - self.camera_y
                
                # 簡易的なタイルパターン
                if (x + y) % 4 == 0:
                    color = (100, 200, 100)  # 明るい緑
                else:
                    color = (80, 180, 80)    # 暗い緑
                
                pygame.draw.rect(self.screen, color, (tile_x, tile_y, tile_size, tile_size))
                pygame.draw.rect(self.screen, (60, 160, 60), (tile_x, tile_y, tile_size, tile_size), 1)
    
    def _draw_ui(self):
        """UI描画"""
        # プレイヤー情報
        player_stats = self.player.get_stats()
        
        # スタミナ表示
        stamina_text = f"スタミナ: {int(player_stats.stamina)}/{player_stats.max_stamina}"
        stamina_surface = self.font_manager.render_text(stamina_text, 18, (255, 255, 255))
        self.screen.blit(stamina_surface, (10, 10))
        
        # ペット情報
        y_offset = 40
        for i, pet in enumerate(self.pets):
            pet_info = f"{pet.data.name}: 信頼度 {pet.get_trust_level():.1f}% ({pet.get_state().value})"
            pet_surface = self.font_manager.render_text(pet_info, 16, (255, 255, 255))
            self.screen.blit(pet_surface, (10, y_offset + i * 25))
        
        # 相互作用メッセージ
        if self.interaction_message:
            message_surface = self.font_manager.render_text(self.interaction_message, 24, (255, 255, 0))
            message_rect = message_surface.get_rect(center=(self.screen.get_width() // 2, 100))
            
            # 背景
            bg_rect = pygame.Rect(message_rect.x - 20, message_rect.y - 10, 
                                message_rect.width + 40, message_rect.height + 20)
            pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
            
            self.screen.blit(message_surface, message_rect)
        
        # 操作説明
        controls = [
            "WASD: 移動",
            "Shift: 走行",
            "Space: ペットと相互作用",
            "F1: デバッグ表示"
        ]
        
        for i, control in enumerate(controls):
            control_surface = self.font_manager.render_text(control, 14, (255, 255, 255))
            self.screen.blit(control_surface, (self.screen.get_width() - 200, 10 + i * 20))
    
    def _draw_debug_info(self):
        """デバッグ情報描画"""
        debug_info = [
            f"FPS: {int(self.clock.get_fps())}",
            f"プレイヤー位置: ({int(self.player.x)}, {int(self.player.y)})",
            f"カメラ位置: ({int(self.camera_x)}, {int(self.camera_y)})",
            f"読み込み済みアセット: {self.asset_manager.get_asset_info()}",
        ]
        
        # 背景
        debug_bg = pygame.Rect(10, self.screen.get_height() - 120, 400, 110)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), debug_bg)
        
        for i, info in enumerate(debug_info):
            debug_surface = self.font_manager.render_text(info, 14, (255, 255, 255))
            self.screen.blit(debug_surface, (15, self.screen.get_height() - 115 + i * 20))

def main():
    """メイン関数"""
    print("🎨 アセット統合デモ起動中...")
    
    try:
        demo = AssetIntegrationDemo()
        demo.run()
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
