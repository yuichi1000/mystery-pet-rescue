#!/usr/bin/env python3
"""
ミステリー・ペット・レスキュー
メインエントリーポイント (Web/デスクトップ統合版)
"""

import asyncio
import sys
import os
from pathlib import Path

# 環境設定
os.environ['SDL_IME_SHOW_UI'] = '0'
sys.path.insert(0, str(Path(__file__).parent))

# Web環境チェック
def is_web_environment():
    return (
        hasattr(sys, 'platform') and 'emscripten' in sys.platform or
        os.environ.get('WEB_VERSION') == '1' or
        'pygbag' in sys.modules
    )

import pygame

# Web環境での日本語フォント対応
if is_web_environment():
    print("🌐 Web環境での日本語フォント初期化")
    # フォントファイルを事前読み込み
    import base64
    try:
        # Pygbagのファイルシステムにフォントを登録
        font_path = "assets/fonts/NotoSansJP-VariableFont_wght.ttf"
        if os.path.exists(font_path):
            print(f"✅ 日本語フォントファイル発見: {font_path}")
            # PygameにカスタムフォントとしてNoto Sans JPを登録
            try:
                test_font = pygame.font.Font(font_path, 24)
                print("✅ 日本語フォント読み込みテスト成功")
            except Exception as e:
                print(f"⚠️ フォント読み込みテスト失敗: {e}")
    except Exception as e:
        print(f"⚠️ Web環境フォント初期化エラー: {e}")

class Game:
    def __init__(self):
        pygame.init()
        
        # Web環境では軽量初期化
        if is_web_environment():
            os.environ['WEB_VERSION'] = '1'
            try:
                pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
            except:
                pass
        else:
            pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Mystery Pet Rescue")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.fps = 30 if is_web_environment() else 60
        
        # ゲームフロー初期化
        self.game_flow = None
        self.initialize_game()
    
    def initialize_game(self):
        try:
            from src.core.game_flow import GameFlowManager
            self.game_flow = GameFlowManager(self.screen)
            print("✅ ゲーム初期化完了")
            return True
        except Exception as e:
            print(f"❌ ゲーム初期化エラー: {e}")
            return False
    
    async def run_async(self):
        """非同期ゲームループ（Web版）"""
        print("🌐 Web版ゲーム開始")
        
        if not self.game_flow:
            await self.show_error()
            return
        
        while self.running:
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    try:
                        result = self.game_flow.handle_event(event)
                        if result == "quit":
                            self.running = False
                    except:
                        pass
            
            # 更新
            time_delta = self.clock.tick(self.fps) / 1000.0
            try:
                result = self.game_flow.update(time_delta)
                if result == "quit":
                    self.running = False
            except:
                pass
            
            # 描画
            self.screen.fill((40, 40, 40))
            try:
                self.game_flow.draw(self.screen)
            except:
                pass
            
            pygame.display.flip()
            await asyncio.sleep(0)
    
    def run_sync(self):
        """同期ゲームループ（デスクトップ版）"""
        print("🖥️ デスクトップ版ゲーム開始")
        
        if not self.game_flow:
            return
        
        while self.running:
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    try:
                        result = self.game_flow.handle_event(event)
                        if result == "quit":
                            self.running = False
                    except:
                        pass
            
            # 更新
            time_delta = self.clock.tick(self.fps) / 1000.0
            try:
                result = self.game_flow.update(time_delta)
                if result == "quit":
                    self.running = False
            except:
                pass
            
            # 描画
            self.screen.fill((40, 40, 40))
            try:
                self.game_flow.draw(self.screen)
            except:
                pass
            
            pygame.display.flip()
    
    async def show_error(self):
        """エラー表示"""
        font = pygame.font.Font(None, 48)
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.screen.fill((20, 30, 50))
            
            text = font.render("Mystery Pet Rescue", True, (255, 255, 255))
            text_rect = text.get_rect(center=(640, 300))
            self.screen.blit(text, text_rect)
            
            text = font.render("Loading Error - Web Version", True, (200, 200, 200))
            text_rect = text.get_rect(center=(640, 360))
            self.screen.blit(text, text_rect)
            
            pygame.display.flip()
            self.clock.tick(30)
            await asyncio.sleep(0)

async def main():
    print("🎮 ミステリー・ペット・レスキュー")
    print("=" * 50)
    
    try:
        game = Game()
        
        if is_web_environment():
            print("🌐 Web版で実行")
            await game.run_async()
        else:
            print("🖥️ デスクトップ版で実行")
            game.run_sync()
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if is_web_environment():
        asyncio.run(main())
    else:
        # デスクトップ版では従来のGameMainを使用
        try:
            from src.core.game_main import GameMain
            game = GameMain()
            game.run()
        except:
            asyncio.run(main())
