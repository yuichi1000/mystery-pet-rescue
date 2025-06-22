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
    
    def update(self):
        """ゲーム状態更新"""
        # 将来的にはここで各シーンの更新処理を呼び出す
        pass
    
    def render(self):
        """画面描画"""
        self.screen.fill(COLOR_BLACK)
        
        if self.current_scene == "title":
            self.render_title_scene()
        elif self.current_scene == "game":
            self.render_game_scene()
        
        pygame.display.flip()
    
    def render_title_scene(self):
        """タイトルシーン描画"""
        # タイトル
        title_text = self.font.render(GAME_TITLE, True, COLOR_WHITE)
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(title_text, title_rect)
        
        # 操作説明
        font_small = pygame.font.Font(None, 36)
        instruction_text = font_small.render("SPACE: ゲーム開始  ESC: 終了", True, COLOR_BLUE)
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
        instruction_text = font_small.render("SPACE: タイトルに戻る  ESC: 終了", True, COLOR_WHITE)
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
