#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ミステリー・ペット・レスキュー デモゲーム
完全なキーボード入力とゲームループのデモンストレーション
"""

import pygame
import sys
import math
from typing import Set, Tuple

# ゲーム設定
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "Mystery Pet Rescue - Demo"

# 色定義
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_PURPLE = (255, 0, 255)
COLOR_CYAN = (0, 255, 255)
COLOR_GRAY = (128, 128, 128)
COLOR_DARK_GREEN = (0, 128, 0)


class Player:
    """プレイヤークラス"""
    
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.speed = 300  # ピクセル/秒
        self.size = 30
        self.color = COLOR_BLUE
        self.trail = []  # 軌跡用
        
    def update(self, dt: float, keys_pressed: Set[int]):
        """プレイヤー更新"""
        # 移動処理
        dx = dy = 0
        if pygame.K_LEFT in keys_pressed or pygame.K_a in keys_pressed:
            dx -= 1
        if pygame.K_RIGHT in keys_pressed or pygame.K_d in keys_pressed:
            dx += 1
        if pygame.K_UP in keys_pressed or pygame.K_w in keys_pressed:
            dy -= 1
        if pygame.K_DOWN in keys_pressed or pygame.K_s in keys_pressed:
            dy += 1
        
        # 斜め移動の正規化
        if dx != 0 and dy != 0:
            dx *= 0.707  # 1/√2
            dy *= 0.707
        
        # 位置更新
        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt
        
        # 画面境界チェック
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))
        
        # 軌跡更新
        self.trail.append((int(self.x), int(self.y)))
        if len(self.trail) > 50:
            self.trail.pop(0)
    
    def render(self, screen: pygame.Surface):
        """プレイヤー描画"""
        # 軌跡描画
        for i, pos in enumerate(self.trail):
            alpha = int(255 * (i / len(self.trail)))
            color = (*COLOR_CYAN, alpha)
            pygame.draw.circle(screen, COLOR_CYAN, pos, max(1, self.size // 4 * (i / len(self.trail))))
        
        # プレイヤー本体
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, COLOR_WHITE, (int(self.x), int(self.y)), self.size, 3)


class Pet:
    """ペットクラス（デモ用）"""
    
    def __init__(self, x: int, y: int, pet_type: str):
        self.x = x
        self.y = y
        self.pet_type = pet_type
        self.size = 20
        self.color = self._get_color()
        self.angle = 0
        self.speed = 50
        self.found = False
        
    def _get_color(self) -> Tuple[int, int, int]:
        """ペットタイプに応じた色を取得"""
        colors = {
            "dog": COLOR_YELLOW,
            "cat": (255, 165, 0),  # オレンジ
            "rabbit": COLOR_WHITE,
            "bird": COLOR_GREEN
        }
        return colors.get(self.pet_type, COLOR_GRAY)
    
    def update(self, dt: float, player_pos: Tuple[float, float]):
        """ペット更新"""
        # プレイヤーとの距離計算
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        distance = math.sqrt(dx * dx + dy * dy)
        
        # プレイヤーが近くにいる場合
        if distance < 100 and not self.found:
            self.found = True
        
        # 簡単なAI移動
        if not self.found:
            self.angle += dt * 2
            self.x += math.cos(self.angle) * self.speed * dt
            self.y += math.sin(self.angle) * self.speed * dt
            
            # 画面境界で反転
            if self.x <= self.size or self.x >= SCREEN_WIDTH - self.size:
                self.angle = math.pi - self.angle
            if self.y <= self.size or self.y >= SCREEN_HEIGHT - self.size:
                self.angle = -self.angle
    
    def render(self, screen: pygame.Surface):
        """ペット描画"""
        color = COLOR_GREEN if self.found else self.color
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)
        pygame.draw.circle(screen, COLOR_BLACK, (int(self.x), int(self.y)), self.size, 2)
        
        # 発見済みマーク
        if self.found:
            pygame.draw.circle(screen, COLOR_WHITE, (int(self.x), int(self.y)), self.size // 2)


class DemoGame:
    """デモゲームクラス"""
    
    def __init__(self):
        self.screen = None
        self.clock = None
        self.running = False
        self.font = None
        self.small_font = None
        
        # キー入力状態
        self.keys_pressed: Set[int] = set()
        self.keys_just_pressed: Set[int] = set()
        
        # ゲームオブジェクト
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.pets = [
            Pet(200, 200, "dog"),
            Pet(800, 300, "cat"),
            Pet(400, 500, "rabbit"),
            Pet(1000, 200, "bird")
        ]
        
        # ゲーム状態
        self.show_debug = True
        self.frame_count = 0
        self.game_time = 0
        self.fullscreen = False
        
    def initialize(self):
        """ゲーム初期化"""
        pygame.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        
        self.clock = pygame.time.Clock()
        
        pygame.font.init()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 24)
        
        self.running = True
        print(f"デモゲーム初期化完了: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    
    def handle_events(self):
        """イベント処理"""
        self.keys_just_pressed.clear()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_F1:
                    self.show_debug = not self.show_debug
                elif event.key == pygame.K_F11:
                    self.toggle_fullscreen()
                elif event.key == pygame.K_r:
                    self.reset_game()
                
                if event.key not in self.keys_pressed:
                    self.keys_just_pressed.add(event.key)
                self.keys_pressed.add(event.key)
                
            elif event.type == pygame.KEYUP:
                if event.key in self.keys_pressed:
                    self.keys_pressed.remove(event.key)
    
    def update(self, dt: float):
        """ゲーム更新"""
        self.frame_count += 1
        self.game_time += dt
        
        # プレイヤー更新
        self.player.update(dt, self.keys_pressed)
        
        # ペット更新
        for pet in self.pets:
            pet.update(dt, (self.player.x, self.player.y))
    
    def render(self):
        """画面描画"""
        # 背景
        self.screen.fill(COLOR_DARK_GREEN)
        
        # グリッド描画（デバッグ用）
        if self.show_debug:
            for x in range(0, SCREEN_WIDTH, 100):
                pygame.draw.line(self.screen, COLOR_GRAY, (x, 0), (x, SCREEN_HEIGHT))
            for y in range(0, SCREEN_HEIGHT, 100):
                pygame.draw.line(self.screen, COLOR_GRAY, (0, y), (SCREEN_WIDTH, y))
        
        # ペット描画
        for pet in self.pets:
            pet.render(self.screen)
        
        # プレイヤー描画
        self.player.render(self.screen)
        
        # UI描画
        self.render_ui()
        
        # デバッグ情報
        if self.show_debug:
            self.render_debug_info()
        
        pygame.display.flip()
    
    def render_ui(self):
        """UI描画"""
        # タイトル
        title_text = self.font.render("Mystery Pet Rescue - Demo", True, COLOR_WHITE)
        self.screen.blit(title_text, (20, 20))
        
        # 発見したペット数
        found_pets = sum(1 for pet in self.pets if pet.found)
        status_text = self.small_font.render(f"Pets Found: {found_pets}/{len(self.pets)}", True, COLOR_YELLOW)
        self.screen.blit(status_text, (20, 70))
        
        # 操作説明
        instructions = [
            "WASD / Arrow Keys: Move",
            "ESC: Quit  F1: Debug  F11: Fullscreen  R: Reset"
        ]
        
        for i, instruction in enumerate(instructions):
            text = self.small_font.render(instruction, True, COLOR_WHITE)
            self.screen.blit(text, (20, SCREEN_HEIGHT - 60 + i * 25))
    
    def render_debug_info(self):
        """デバッグ情報描画"""
        debug_info = [
            f"FPS: {self.clock.get_fps():.1f}",
            f"Frame: {self.frame_count}",
            f"Time: {self.game_time:.1f}s",
            f"Player: ({self.player.x:.0f}, {self.player.y:.0f})",
            f"Keys: {len(self.keys_pressed)}",
            f"Fullscreen: {self.fullscreen}"
        ]
        
        # 背景
        bg_rect = pygame.Rect(SCREEN_WIDTH - 220, 10, 210, len(debug_info) * 25 + 10)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), bg_rect)
        pygame.draw.rect(self.screen, COLOR_WHITE, bg_rect, 1)
        
        # テキスト
        for i, info in enumerate(debug_info):
            text = self.small_font.render(info, True, COLOR_GREEN)
            self.screen.blit(text, (SCREEN_WIDTH - 210, 20 + i * 25))
    
    def toggle_fullscreen(self):
        """フルスクリーン切り替え"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def reset_game(self):
        """ゲームリセット"""
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.pets = [
            Pet(200, 200, "dog"),
            Pet(800, 300, "cat"),
            Pet(400, 500, "rabbit"),
            Pet(1000, 200, "bird")
        ]
        self.game_time = 0
        self.frame_count = 0
    
    def run(self):
        """メインゲームループ"""
        print("デモゲーム開始")
        print("ペットに近づいて発見しよう！")
        
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
            self.clock.tick(FPS)
        
        print("デモゲーム終了")
    
    def cleanup(self):
        """クリーンアップ"""
        pygame.quit()


def main():
    """メイン関数"""
    try:
        game = DemoGame()
        game.initialize()
        game.run()
    except KeyboardInterrupt:
        print("\nゲーム中断")
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'game' in locals():
            game.cleanup()


if __name__ == "__main__":
    main()
