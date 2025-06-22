#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ミステリー・ペット・レスキュー
メインゲームファイル

迷子になったペットたちを探し出し、飼い主の元に返すアドベンチャーゲーム
"""

import sys
import os
import pygame
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# ゲーム設定
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
FPS = 60
GAME_TITLE = "ミステリー・ペット・レスキュー"

# 色定義
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_BLUE = (100, 150, 255)


class GameState:
    """ゲーム状態管理クラス"""
    
    def __init__(self):
        self.current_scene = "title"
        self.running = True
        self.clock = pygame.time.Clock()
        self.screen = None
        self.font = None
        self.fullscreen = False
        self.show_debug = False
        self.frame_count = 0
    
    def initialize(self):
        """ゲームを初期化"""
        pygame.init()
        
        # 画面設定
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(GAME_TITLE)
        
        # フォント初期化
        pygame.font.init()
        self.font = pygame.font.Font(None, 72)
        
        print(f"ゲーム初期化完了: {SCREEN_WIDTH}x{SCREEN_HEIGHT}")
    
    def handle_events(self):
        """イベント処理"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # スペースキーでシーン切り替え（デモ用）
                    if self.current_scene == "title":
                        self.current_scene = "game"
                    else:
                        self.current_scene = "title"
                elif event.key == pygame.K_F1:
                    # F1キーでデバッグ情報表示切り替え
                    self.show_debug = not getattr(self, 'show_debug', False)
                elif event.key == pygame.K_F11:
                    # F11キーでフルスクリーン切り替え
                    self.toggle_fullscreen()
    
    def update(self):
        """ゲーム状態更新"""
        # フレームカウント更新
        self.frame_count += 1
        
        # 将来的にはここで各シーンの更新処理を呼び出す
        pass
    
    def render(self):
        """画面描画"""
        self.screen.fill(COLOR_BLACK)
        
        if self.current_scene == "title":
            self.render_title_scene()
        elif self.current_scene == "game":
            self.render_game_scene()
        
        # デバッグ情報表示
        if self.show_debug:
            self.render_debug_info()
        
        pygame.display.flip()
    
    def render_title_scene(self):
        """タイトルシーン描画"""
        # タイトル
        title_text = self.font.render(GAME_TITLE, True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(title_text, title_rect)
        
        # 操作説明
        font_small = pygame.font.Font(None, 36)
        instruction_text = font_small.render("SPACE: ゲーム開始  ESC: 終了  F1: デバッグ  F11: フルスクリーン", True, COLOR_BLUE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(instruction_text, instruction_rect)
    
    def render_game_scene(self):
        """ゲームシーン描画（仮実装）"""
        # 背景色を変更
        self.screen.fill((50, 100, 50))  # 緑っぽい背景
        
        # ゲーム画面表示
        game_text = self.font.render("ゲーム画面", True, COLOR_WHITE)
        game_rect = game_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(game_text, game_rect)
        
        # 操作説明
        font_small = pygame.font.Font(None, 36)
        instruction_text = font_small.render("SPACE: タイトルに戻る  ESC: 終了  F1: デバッグ  F11: フルスクリーン", True, COLOR_WHITE)
        instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(instruction_text, instruction_rect)
    
    def run(self):
        """メインゲームループ"""
        print("ゲーム開始")
        
        while self.running:
            # イベント処理
            self.handle_events()
            
            # 更新処理
            self.update()
            
            # 描画処理
            self.render()
            
            # FPS制御
            self.clock.tick(FPS)
        
        print("ゲーム終了")
    
    def cleanup(self):
        """クリーンアップ処理"""
        pygame.quit()
    
    def toggle_fullscreen(self):
        """フルスクリーン切り替え"""
        self.fullscreen = not self.fullscreen
        if self.fullscreen:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    def render_debug_info(self):
        """デバッグ情報を描画"""
        font_small = pygame.font.Font(None, 24)
        debug_info = [
            f"FPS: {self.clock.get_fps():.1f}",
            f"Frame: {self.frame_count}",
            f"Scene: {self.current_scene}",
            f"Fullscreen: {self.fullscreen}",
            f"Resolution: {SCREEN_WIDTH}x{SCREEN_HEIGHT}"
        ]
        
        # デバッグ情報背景
        debug_bg = pygame.Rect(10, 10, 200, len(debug_info) * 25 + 10)
        pygame.draw.rect(self.screen, (0, 0, 0, 180), debug_bg)
        pygame.draw.rect(self.screen, COLOR_WHITE, debug_bg, 1)
        
        # デバッグテキスト
        for i, info in enumerate(debug_info):
            text = font_small.render(info, True, COLOR_WHITE)
            self.screen.blit(text, (15, 20 + i * 25))


def main():
    """メイン関数"""
    try:
        # ゲーム状態を作成
        game = GameState()
        
        # 初期化
        game.initialize()
        
        # ゲームループ実行
        game.run()
        
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
