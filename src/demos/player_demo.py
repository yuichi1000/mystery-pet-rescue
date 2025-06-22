#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
プレイヤーキャラクターデモ
新しいプレイヤークラスの機能をテストするデモ
"""

import pygame
import sys
import math
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.entities.player import Player, AnimationState, Direction
from config.constants import *

class PlayerDemo:
    """プレイヤーデモクラス"""
    
    def __init__(self):
        self.screen = None
        self.clock = None
        self.running = False
        self.font = None
        self.small_font = None
        
        # プレイヤー
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        
        # デバッグ表示
        self.show_debug = True
        self.show_stats = True
        
        # 背景グリッド
        self.show_grid = True
        
        # カメラ（将来用）
        self.camera_x = 0
        self.camera_y = 0
        
        # フレーム情報
        self.frame_count = 0
        self.fps = 0
    
    def initialize(self):
        """デモを初期化"""
        pygame.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Player Character Demo")
        
        self.clock = pygame.time.Clock()
        
        pygame.font.init()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        self.running = True
        print("プレイヤーデモ初期化完了")
    
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
                    self.show_stats = not self.show_stats
                elif event.key == pygame.K_F3:
                    self.show_grid = not self.show_grid
                elif event.key == pygame.K_r:
                    self.reset_demo()
                elif event.key == pygame.K_1:
                    self.player.set_speed(100)  # 遅い
                elif event.key == pygame.K_2:
                    self.player.set_speed(200)  # 普通
                elif event.key == pygame.K_3:
                    self.player.set_speed(400)  # 速い
    
    def update(self, dt: float):
        """デモ更新"""
        self.frame_count += 1
        self.fps = self.clock.get_fps()
        
        # プレイヤー更新（Noneを渡すことで直接pygame.key.get_pressed()を使用）
        self.player.update(dt, None)
    
    def render(self):
        """画面描画"""
        # 背景
        self.screen.fill((40, 60, 40))  # 暗い緑
        
        # グリッド描画
        if self.show_grid:
            self.render_grid()
        
        # プレイヤー描画
        self.player.render(self.screen)
        
        # デバッグ情報
        if self.show_debug:
            self.player.render_debug(self.screen)
        
        # UI描画
        self.render_ui()
        
        # 統計情報
        if self.show_stats:
            self.render_stats()
        
        pygame.display.flip()
    
    def render_grid(self):
        """グリッドを描画"""
        grid_size = 50
        grid_color = (60, 80, 60)
        
        # 縦線
        for x in range(0, SCREEN_WIDTH, grid_size):
            pygame.draw.line(self.screen, grid_color, (x, 0), (x, SCREEN_HEIGHT))
        
        # 横線
        for y in range(0, SCREEN_HEIGHT, grid_size):
            pygame.draw.line(self.screen, grid_color, (0, y), (SCREEN_WIDTH, y))
    
    def render_ui(self):
        """UI描画"""
        # タイトル
        title_text = self.font.render("Player Character Demo", True, COLOR_WHITE)
        self.screen.blit(title_text, (10, 10))
        
        # 操作説明
        instructions = [
            "WASD / Arrow Keys: Move (8-direction)",
            "Shift: Run (consumes stamina)",
            "ESC: Quit",
            "F1: Toggle Debug  F2: Toggle Stats  F3: Toggle Grid",
            "R: Reset  1/2/3: Speed (Slow/Normal/Fast)"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, COLOR_WHITE)
            self.screen.blit(text, (10, SCREEN_HEIGHT - 120 + i * 20))
        
        # 現在の状態表示
        state_info = [
            f"Animation: {self.player.animation_state.value}",
            f"Direction: {self.player.direction.value}",
            f"Speed: {self.player.current_speed:.0f}",
            f"Moving: {self.player.is_moving}"
        ]
        
        for i, info in enumerate(state_info):
            color = COLOR_YELLOW if self.player.is_moving else COLOR_WHITE
            text = self.small_font.render(info, True, color)
            self.screen.blit(text, (SCREEN_WIDTH - 200, 50 + i * 25))
    
    def render_stats(self):
        """統計情報を描画"""
        stats = self.player.get_stats()
        
        # ステータスバー
        bar_width = 150
        bar_height = 15
        bar_x = SCREEN_WIDTH - 200
        bar_y = 200
        
        # 体力バー
        self.render_bar("Health", stats["health"], 100, 
                       bar_x, bar_y, bar_width, bar_height, COLOR_RED)
        
        # エネルギーバー
        self.render_bar("Energy", stats["energy"], 100, 
                       bar_x, bar_y + 40, bar_width, bar_height, COLOR_BLUE)
        
        # スタミナバー
        self.render_bar("Stamina", stats["stamina"], 100, 
                       bar_x, bar_y + 80, bar_width, bar_height, COLOR_GREEN)
        
        # 統計情報
        stat_info = [
            f"Position: ({stats['position'][0]:.0f}, {stats['position'][1]:.0f})",
            f"Distance: {stats['distance_walked']:.1f}",
            f"Play Time: {stats['play_time']:.1f}s",
            f"Pets Rescued: {stats['pets_rescued']}",
            f"FPS: {self.fps:.1f}"
        ]
        
        for i, info in enumerate(stat_info):
            text = self.small_font.render(info, True, COLOR_WHITE)
            self.screen.blit(text, (bar_x, bar_y + 120 + i * 20))
    
    def render_bar(self, label: str, current: float, maximum: float, 
                   x: int, y: int, width: int, height: int, color: tuple):
        """ステータスバーを描画"""
        # ラベル
        label_text = self.small_font.render(label, True, COLOR_WHITE)
        self.screen.blit(label_text, (x, y - 20))
        
        # 背景
        bg_rect = pygame.Rect(x, y, width, height)
        pygame.draw.rect(self.screen, COLOR_GRAY, bg_rect)
        
        # バー
        if maximum > 0:
            bar_width = int(width * (current / maximum))
            bar_rect = pygame.Rect(x, y, bar_width, height)
            pygame.draw.rect(self.screen, color, bar_rect)
        
        # 枠線
        pygame.draw.rect(self.screen, COLOR_WHITE, bg_rect, 1)
        
        # 数値表示
        value_text = self.small_font.render(f"{current:.0f}/{maximum:.0f}", True, COLOR_WHITE)
        text_rect = value_text.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(value_text, text_rect)
    
    def reset_demo(self):
        """デモをリセット"""
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.frame_count = 0
        print("デモをリセットしました")
    
    def run(self):
        """メインループ"""
        print("プレイヤーデモ開始")
        print("操作方法:")
        print("  WASD / 矢印キー: 8方向移動")
        print("  Shift: 走行（スタミナ消費）")
        print("  F1: デバッグ表示切り替え")
        print("  F2: 統計表示切り替え")
        print("  F3: グリッド表示切り替え")
        print("  R: リセット")
        print("  1/2/3: 速度変更")
        
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
        
        print("プレイヤーデモ終了")
    
    def cleanup(self):
        """クリーンアップ"""
        pygame.quit()
    
    # 入力ハンドラーのインターフェース互換性のため
    @property
    def keys_pressed(self):
        """現在押されているキーのセットを返す"""
        keys = pygame.key.get_pressed()
        pressed_keys = set()
        
        for i, pressed in enumerate(keys):
            if pressed:
                pressed_keys.add(i)
        
        return pressed_keys


def main():
    """メイン関数"""
    try:
        demo = PlayerDemo()
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
