#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
タイルベース2Dマップシステムデモ
マップ読み込み、カメラ追従、衝突判定をテスト
"""

import pygame
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.systems.map_system import MapSystem
from src.entities.player import Player
from config.constants import *

class MapDemo:
    """マップシステムデモクラス"""
    
    def __init__(self):
        self.screen = None
        self.clock = None
        self.running = False
        self.font = None
        self.small_font = None
        
        # マップシステム
        self.map_system = MapSystem(tile_size=32)
        
        # プレイヤー
        self.player = Player(100, 100)
        
        # デバッグ表示
        self.show_debug = True
        self.show_collision = True
        self.show_camera_info = True
        
        # フレーム情報
        self.frame_count = 0
        self.fps = 0
        
        # マップ選択
        self.current_map = 0
        self.map_files = [
            "sample",  # サンプルマップ（プログラム生成）
            "data/maps/sample_map.json"  # JSONファイル
        ]
    
    def initialize(self):
        """デモを初期化"""
        pygame.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tile-based 2D Map System Demo")
        
        self.clock = pygame.time.Clock()
        
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # 初期マップ読み込み
        self.load_current_map()
        
        self.running = True
        print("マップシステムデモ初期化完了")
    
    def load_current_map(self):
        """現在選択されているマップを読み込み"""
        map_file = self.map_files[self.current_map]
        
        if map_file == "sample":
            # サンプルマップ作成
            self.map_system.create_sample_map()
            print("サンプルマップを作成しました")
        else:
            # JSONファイル読み込み
            if self.map_system.load_from_json(map_file):
                print(f"マップファイル '{map_file}' を読み込みました")
            else:
                print(f"マップファイル '{map_file}' の読み込みに失敗しました")
                # フォールバック
                self.map_system.create_sample_map()
        
        # プレイヤー位置を安全な場所に設定（衝突しない場所）
        # タイル座標(3,3)の位置（96, 96）に配置
        safe_x, safe_y = 3 * 32, 3 * 32
        self.player.set_position(safe_x, safe_y)
        
        # 初期位置での衝突チェック
        collision = self.map_system.check_collision(safe_x, safe_y, self.player.width, self.player.height)
        print(f"プレイヤー初期位置: ({safe_x}, {safe_y}), 衝突: {collision}")
        
        # もし衝突する場合は、別の安全な位置を探す
        if collision:
            for test_x in range(2, 10):
                for test_y in range(2, 10):
                    pos_x, pos_y = test_x * 32, test_y * 32
                    if not self.map_system.check_collision(pos_x, pos_y, self.player.width, self.player.height):
                        self.player.set_position(pos_x, pos_y)
                        print(f"安全な位置に移動: ({pos_x}, {pos_y})")
                        return
            
            # それでも見つからない場合は警告
            print("警告: 安全な初期位置が見つかりませんでした")
    
    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F1:
                    self.show_debug = not self.show_debug
                elif event.key == pygame.K_F2:
                    self.show_collision = not self.show_collision
                elif event.key == pygame.K_F3:
                    self.show_camera_info = not self.show_camera_info
                elif event.key == pygame.K_r:
                    self.reset_demo()
                elif event.key == pygame.K_m:
                    self.switch_map()
                elif event.key == pygame.K_c:
                    self.center_camera()
    
    def switch_map(self):
        """マップを切り替え"""
        self.current_map = (self.current_map + 1) % len(self.map_files)
        self.load_current_map()
        print(f"マップを切り替えました: {self.map_files[self.current_map]}")
    
    def center_camera(self):
        """カメラをプレイヤーに即座に合わせる"""
        player_x, player_y = self.player.get_center()
        self.map_system.camera.x = player_x - SCREEN_WIDTH // 2
        self.map_system.camera.y = player_y - SCREEN_HEIGHT // 2
        self.map_system.camera.target_x = self.map_system.camera.x
        self.map_system.camera.target_y = self.map_system.camera.y
    
    def reset_demo(self):
        """デモをリセット"""
        self.load_current_map()
        self.frame_count = 0
        print("デモをリセットしました")
    
    def update(self, dt: float):
        """デモ更新"""
        self.frame_count += 1
        self.fps = self.clock.get_fps()
        
        # プレイヤー更新（マップシステムを渡す）
        old_x, old_y = self.player.get_position()
        self.player.update(dt, None, self.map_system)
        new_x, new_y = self.player.get_position()
        
        # 追加の衝突判定チェック（念のため）
        if self.map_system.check_collision(new_x, new_y, self.player.width, self.player.height):
            # 衝突した場合は元の位置に戻す
            self.player.set_position(old_x, old_y)
        
        # カメラをプレイヤーに追従
        player_center_x, player_center_y = self.player.get_center()
        self.map_system.set_camera_target(player_center_x, player_center_y)
        
        # マップシステム更新
        self.map_system.update(dt)
    
    def render(self):
        """画面描画"""
        # 背景
        self.screen.fill((20, 20, 30))
        
        # マップ描画
        self.map_system.render(self.screen)
        
        # プレイヤー描画（ワールド座標をスクリーン座標に変換）
        player_x, player_y = self.player.get_position()
        screen_x, screen_y = self.map_system.world_to_screen(player_x, player_y)
        
        # プレイヤーを一時的にスクリーン座標に移動して描画
        original_x, original_y = self.player.x, self.player.y
        self.player.x, self.player.y = screen_x, screen_y
        self.player.render(self.screen)
        self.player.x, self.player.y = original_x, original_y
        
        # デバッグ情報
        if self.show_debug:
            self.render_debug_info()
        
        # 衝突判定可視化
        if self.show_collision:
            self.render_collision_debug()
        
        # UI描画
        self.render_ui()
        
        pygame.display.flip()
    
    def render_debug_info(self):
        """デバッグ情報を描画"""
        player_x, player_y = self.player.get_position()
        player_center_x, player_center_y = self.player.get_center()
        
        debug_info = [
            f"Player Pos: ({player_x:.1f}, {player_y:.1f})",
            f"Player Center: ({player_center_x:.1f}, {player_center_y:.1f})",
            f"Camera Pos: ({self.map_system.camera.x:.1f}, {self.map_system.camera.y:.1f})",
            f"Camera Target: ({self.map_system.camera.target_x:.1f}, {self.map_system.camera.target_y:.1f})",
            f"Map Size: {self.map_system.get_map_size()}",
            f"Tile Size: {self.map_system.get_tile_size()}px"
        ]
        
        for i, info in enumerate(debug_info):
            text = self.small_font.render(info, True, COLOR_WHITE)
            self.screen.blit(text, (10, 10 + i * 20))
    
    def render_collision_debug(self):
        """衝突判定のデバッグ表示"""
        player_x, player_y = self.player.get_position()
        
        # プレイヤーの衝突矩形をスクリーン座標で描画
        screen_x, screen_y = self.map_system.world_to_screen(player_x, player_y)
        collision_rect = pygame.Rect(screen_x, screen_y, self.player.width, self.player.height)
        pygame.draw.rect(self.screen, COLOR_RED, collision_rect, 2)
        
        # 周囲のタイルの衝突判定を表示
        tile_size = self.map_system.get_tile_size()
        start_x = int((player_x - tile_size) // tile_size) * tile_size
        start_y = int((player_y - tile_size) // tile_size) * tile_size
        end_x = start_x + tile_size * 4
        end_y = start_y + tile_size * 4
        
        for y in range(int(start_y), int(end_y), tile_size):
            for x in range(int(start_x), int(end_x), tile_size):
                if self.map_system.check_collision(x, y, tile_size, tile_size):
                    screen_x, screen_y = self.map_system.world_to_screen(x, y)
                    tile_rect = pygame.Rect(screen_x, screen_y, tile_size, tile_size)
                    pygame.draw.rect(self.screen, COLOR_YELLOW, tile_rect, 1)
    
    def render_ui(self):
        """UI描画"""
        # タイトル
        title_text = self.font.render("Tile-based 2D Map System Demo", True, COLOR_WHITE)
        self.screen.blit(title_text, (10, SCREEN_HEIGHT - 200))
        
        # 現在のマップ情報
        map_name = self.map_files[self.current_map]
        if map_name == "sample":
            map_name = "Sample Map (Generated)"
        map_text = self.small_font.render(f"Current Map: {map_name}", True, COLOR_YELLOW)
        self.screen.blit(map_text, (10, SCREEN_HEIGHT - 170))
        
        # 操作説明
        instructions = [
            "WASD / Arrow Keys: Move Player",
            "Shift: Run",
            "M: Switch Map",
            "C: Center Camera",
            "R: Reset",
            "F1: Debug Info  F2: Collision  F3: Camera Info",
            "ESC: Quit"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, COLOR_WHITE)
            self.screen.blit(text, (10, SCREEN_HEIGHT - 140 + i * 18))
        
        # カメラ情報
        if self.show_camera_info:
            camera_info = [
                f"FPS: {self.fps:.1f}",
                f"Frame: {self.frame_count}",
                f"Follow Speed: {self.map_system.camera.follow_speed:.1f}"
            ]
            
            for i, info in enumerate(camera_info):
                text = self.small_font.render(info, True, COLOR_GREEN)
                self.screen.blit(text, (SCREEN_WIDTH - 200, 10 + i * 20))
    
    def run(self):
        """メインループ"""
        print("マップシステムデモ開始")
        print("操作方法:")
        print("  WASD / 矢印キー: プレイヤー移動")
        print("  Shift: 走行")
        print("  M: マップ切り替え")
        print("  C: カメラ中央揃え")
        print("  R: リセット")
        print("  F1: デバッグ情報切り替え")
        print("  F2: 衝突判定表示切り替え")
        print("  F3: カメラ情報切り替え")
        
        last_time = pygame.time.get_ticks() / 1000.0
        
        while self.running:
            # デルタタイム計算
            current_time = pygame.time.get_ticks() / 1000.0
            dt = current_time - last_time
            last_time = current_time
            
            # イベント処理
            self.handle_events()
            
            # 更新
            self.update(dt)
            
            # 描画
            self.render()
            
            # FPS制御
            self.clock.tick(TARGET_FPS)
        
        print("マップシステムデモ終了")
    
    def cleanup(self):
        """クリーンアップ"""
        pygame.quit()


def main():
    """メイン関数"""
    try:
        demo = MapDemo()
        demo.initialize()
        demo.run()
    except KeyboardInterrupt:
        print("\nデモ中断")
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'demo' in locals():
            demo.cleanup()


if __name__ == "__main__":
    main()
