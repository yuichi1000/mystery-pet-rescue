#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pygame基本ゲームウィンドウ
1280x720解像度、60FPS、キーボード入力対応
"""

import pygame
import sys
from typing import Set

# ゲーム設定
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "Mystery Pet Rescue - Game Window"

# 色定義
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_GRAY = (128, 128, 128)


class GameWindow:
    """基本ゲームウィンドウクラス"""
    
    def __init__(self):
        """ゲームウィンドウを初期化"""
        self.screen = None
        self.clock = None
        self.running = False
        self.font = None
        self.small_font = None
        
        # キー入力状態管理
        self.keys_pressed: Set[int] = set()
        self.keys_just_pressed: Set[int] = set()
        self.keys_just_released: Set[int] = set()
        
        # ゲーム状態
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT // 2
        self.player_speed = 5
        
        # デバッグ情報
        self.show_debug = True
        self.frame_count = 0
        
    def initialize(self):
        """Pygameを初期化"""
        try:
            pygame.init()
            
            # 画面設定
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            pygame.display.set_caption(GAME_TITLE)
            
            # クロック設定
            self.clock = pygame.time.Clock()
            
            # フォント設定
            pygame.font.init()
            self.font = pygame.font.Font(None, 48)
            self.small_font = pygame.font.Font(None, 24)
            
            self.running = True
            print(f"ゲームウィンドウ初期化完了: {SCREEN_WIDTH}x{SCREEN_HEIGHT} @ {FPS}FPS")
            
        except pygame.error as e:
            print(f"Pygame初期化エラー: {e}")
            sys.exit(1)
    
    def handle_events(self):
        """イベント処理"""
        # 前フレームのキー状態をクリア
        self.keys_just_pressed.clear()
        self.keys_just_released.clear()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                # ESCキーで終了
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                # キー押下状態を記録
                if event.key not in self.keys_pressed:
                    self.keys_just_pressed.add(event.key)
                self.keys_pressed.add(event.key)
                
                # デバッグ表示切り替え
                if event.key == pygame.K_F1:
                    self.show_debug = not self.show_debug
                
            elif event.type == pygame.KEYUP:
                # キー離上状態を記録
                if event.key in self.keys_pressed:
                    self.keys_just_released.add(event.key)
                    self.keys_pressed.remove(event.key)
    
    def update(self):
        """ゲーム状態更新"""
        # プレイヤー移動処理
        if pygame.K_LEFT in self.keys_pressed or pygame.K_a in self.keys_pressed:
            self.player_x -= self.player_speed
        if pygame.K_RIGHT in self.keys_pressed or pygame.K_d in self.keys_pressed:
            self.player_x += self.player_speed
        if pygame.K_UP in self.keys_pressed or pygame.K_w in self.keys_pressed:
            self.player_y -= self.player_speed
        if pygame.K_DOWN in self.keys_pressed or pygame.K_s in self.keys_pressed:
            self.player_y += self.player_speed
        
        # 画面境界チェック
        self.player_x = max(25, min(SCREEN_WIDTH - 25, self.player_x))
        self.player_y = max(25, min(SCREEN_HEIGHT - 25, self.player_y))
        
        # フレームカウント更新
        self.frame_count += 1
    
    def render(self):
        """画面描画"""
        # 背景をクリア
        self.screen.fill(COLOR_BLACK)
        
        # プレイヤーを描画（青い四角）
        player_rect = pygame.Rect(self.player_x - 25, self.player_y - 25, 50, 50)
        pygame.draw.rect(self.screen, COLOR_BLUE, player_rect)
        pygame.draw.rect(self.screen, COLOR_WHITE, player_rect, 2)
        
        # タイトル表示
        title_text = self.font.render("Pygame Game Window", True, COLOR_WHITE)
        self.screen.blit(title_text, (50, 50))
        
        # 操作説明
        instructions = [
            "WASD / Arrow Keys: Move",
            "ESC: Quit",
            "F1: Toggle Debug Info"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, COLOR_YELLOW)
            self.screen.blit(text, (50, 120 + i * 25))
        
        # デバッグ情報表示
        if self.show_debug:
            self.render_debug_info()
        
        # 画面更新
        pygame.display.flip()
    
    def render_debug_info(self):
        """デバッグ情報を描画"""
        debug_info = [
            f"FPS: {self.clock.get_fps():.1f}",
            f"Frame: {self.frame_count}",
            f"Player: ({self.player_x}, {self.player_y})",
            f"Keys Pressed: {len(self.keys_pressed)}",
            f"Screen: {SCREEN_WIDTH}x{SCREEN_HEIGHT}"
        ]
        
        # デバッグ情報背景
        debug_bg = pygame.Rect(SCREEN_WIDTH - 250, 10, 240, len(debug_info) * 25 + 10)
        pygame.draw.rect(self.screen, (0, 0, 0, 128), debug_bg)
        pygame.draw.rect(self.screen, COLOR_WHITE, debug_bg, 1)
        
        # デバッグテキスト
        for i, info in enumerate(debug_info):
            text = self.small_font.render(info, True, COLOR_GREEN)
            self.screen.blit(text, (SCREEN_WIDTH - 240, 20 + i * 25))
        
        # 現在押されているキーを表示
        if self.keys_pressed:
            key_names = [pygame.key.name(key) for key in self.keys_pressed]
            key_text = f"Active Keys: {', '.join(key_names[:5])}"  # 最大5個まで表示
            text = self.small_font.render(key_text, True, COLOR_YELLOW)
            self.screen.blit(text, (50, SCREEN_HEIGHT - 50))
    
    def run(self):
        """メインゲームループ"""
        print("ゲーム開始")
        print("操作方法:")
        print("  WASD / 矢印キー: 移動")
        print("  ESC: 終了")
        print("  F1: デバッグ情報表示切り替え")
        
        while self.running:
            # イベント処理
            self.handle_events()
            
            # ゲーム状態更新
            self.update()
            
            # 画面描画
            self.render()
            
            # FPS制御
            self.clock.tick(FPS)
        
        print("ゲーム終了")
    
    def cleanup(self):
        """クリーンアップ処理"""
        pygame.quit()
        print("Pygame終了処理完了")


def main():
    """メイン関数"""
    try:
        # ゲームウィンドウを作成
        game = GameWindow()
        
        # 初期化
        game.initialize()
        
        # ゲームループ実行
        game.run()
        
    except KeyboardInterrupt:
        print("\nキーボード割り込みでゲーム終了")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # クリーンアップ
        if 'game' in locals():
            game.cleanup()


if __name__ == "__main__":
    main()
