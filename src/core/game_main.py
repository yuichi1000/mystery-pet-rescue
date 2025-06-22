"""
メインゲームクラス（フロー管理版）
GameFlowManagerを使用したゲーム実行
"""

import pygame
import sys
from src.core.game_flow import GameFlowManager

class GameMain:
    """メインゲームクラス"""
    
    def __init__(self):
        # Pygame初期化
        pygame.init()
        pygame.mixer.init()
        
        # 画面設定
        self.screen_width = 1280
        self.screen_height = 720
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        pygame.display.set_caption("ミステリー・ペット・レスキュー")
        
        # ゲームフロー管理
        self.flow_manager = GameFlowManager(self.screen)
        
        # ゲーム設定
        self.clock = pygame.time.Clock()
        self.target_fps = 60
    
    def run(self):
        """メインゲームループ"""
        print("ゲーム開始")
        
        while self.flow_manager.is_running():
            # フレーム時間計算
            time_delta = self.clock.tick(self.target_fps) / 1000.0
            
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.flow_manager.running = False
                elif event.type == pygame.VIDEORESIZE:
                    self._handle_resize(event)
                else:
                    self.flow_manager.handle_event(event)
            
            # 更新処理
            self.flow_manager.update(time_delta)
            
            # 描画処理
            self.screen.fill((0, 0, 0))  # 背景クリア
            self.flow_manager.draw(self.screen)
            
            # 画面更新
            pygame.display.flip()
        
        print("ゲーム終了")
        self._cleanup()
    
    def _handle_resize(self, event):
        """画面リサイズ処理"""
        self.screen_width = event.w
        self.screen_height = event.h
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
        
        # フローマネージャーに新しい画面サイズを通知
        self.flow_manager.screen = self.screen
        
        # 現在のシーンに新しい画面サイズを設定
        if self.flow_manager.current_scene:
            self.flow_manager.current_scene.screen = self.screen
    
    def _cleanup(self):
        """クリーンアップ処理"""
        pygame.quit()
        sys.exit()

def main():
    """メイン関数"""
    try:
        game = GameMain()
        game.run()
    except KeyboardInterrupt:
        print("\nゲームが中断されました")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main()
