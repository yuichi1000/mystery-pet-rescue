#!/usr/bin/env python3
"""
ミステリー・ペット・レスキュー Web版エントリーポイント
Pygbag用の非同期ゲームループ実装
"""

import asyncio
import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# Web環境での環境変数設定
os.environ['SDL_IME_SHOW_UI'] = '0'
os.environ['WEB_VERSION'] = '1'  # Web版フラグ

import pygame
from src.core.game_main import GameMain

class WebGameMain(GameMain):
    """Web版ゲームメイン（非同期対応）"""
    
    def __init__(self):
        super().__init__()
        self.running = True
        self.clock = pygame.time.Clock()
    
    async def run_async(self):
        """非同期ゲームループ"""
        print("🌐 Web版ゲーム開始")
        
        try:
            # ゲーム初期化
            if not self.initialize():
                print("❌ ゲーム初期化失敗")
                return
            
            print("✅ Web版ゲーム初期化完了")
            
            # メインループ
            while self.running:
                # 1フレーム処理
                if not await self.update_frame():
                    break
                
                # ブラウザに制御を返す
                await asyncio.sleep(0)
        
        except Exception as e:
            print(f"❌ Web版ゲームエラー: {e}")
            import traceback
            traceback.print_exc()
        
        finally:
            self.cleanup()
    
    async def update_frame(self) -> bool:
        """1フレームの更新処理"""
        try:
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                
                # ゲームフローにイベントを渡す
                if self.game_flow:
                    result = self.game_flow.handle_event(event)
                    if result == "quit":
                        return False
            
            # 時間経過計算
            time_delta = self.clock.tick(60) / 1000.0
            
            # ゲーム更新
            if self.game_flow:
                result = self.game_flow.update(time_delta)
                if result == "quit":
                    return False
            
            # 画面クリア
            self.screen.fill((40, 40, 40))
            
            # ゲーム描画
            if self.game_flow:
                self.game_flow.draw(self.screen)
            
            # 画面更新
            pygame.display.flip()
            
            return True
            
        except Exception as e:
            print(f"❌ フレーム更新エラー: {e}")
            return False
    
    def cleanup(self):
        """クリーンアップ処理"""
        print("🧹 Web版ゲーム終了処理")
        if hasattr(self, 'game_flow') and self.game_flow:
            self.game_flow.cleanup()
        pygame.quit()

async def main():
    """メイン関数（非同期）"""
    print("🌐 ミステリー・ペット・レスキュー Web版")
    print("=" * 50)
    print("🐾 迷子のペットを探して救出するアドベンチャーゲーム")
    print("🎯 目標: すべてのペットを見つけて飼い主の元に返そう")
    print("🌐 Web版: ブラウザで楽しめます")
    print("=" * 50)
    
    # Web版ゲーム実行
    game = WebGameMain()
    await game.run_async()

if __name__ == "__main__":
    # 非同期実行
    asyncio.run(main())
