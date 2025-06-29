"""
メインゲームクラス（フロー管理版）
GameFlowManagerを使用したゲーム実行（パフォーマンス最適化版）
"""

import pygame
import sys
from src.core.game_flow import GameFlowManager
from src.utils.performance_optimizer import get_performance_optimizer
from src.utils.language_manager import get_language_manager, get_text

class GameMain:
    """メインゲームクラス"""
    
    def __init__(self):
        print("🎮 GameMain 初期化開始")
        
        try:
            # Web環境チェック
            self.is_web = self._check_web_environment()
            
            # Pygame初期化
            print("🔧 Pygame 初期化中...")
            pygame.init()
            
            # Web環境では軽量な音声初期化
            if self.is_web:
                print("🌐 Web環境用音声初期化")
                try:
                    pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
                except Exception as e:
                    print(f"⚠️ Web音声初期化失敗: {e}")
            else:
                print("🖥️ デスクトップ環境用音声初期化")
                pygame.mixer.init()
            
            # 日本語入力（IME）を無効化
            try:
                # テキスト入力を停止してIMEを無効化
                pygame.key.stop_text_input()
                
                # 追加の無効化設定
                import os
                os.environ['SDL_IME_SHOW_UI'] = '0'  # IME UIを非表示
                
                print("✅ 日本語入力（IME）を無効化しました")
            except Exception as e:
                print(f"⚠️ IME無効化に失敗: {e}")
            
            # 画面設定
            self.screen_width = 1280
            self.screen_height = 720
            
            # Web環境では異なる画面設定
            if self.is_web:
                print("🌐 Web環境用画面設定")
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
            else:
                print("🖥️ デスクトップ環境用画面設定")
                self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.RESIZABLE)
            
            # 言語管理システム
            print("🌐 言語管理システム初期化中...")
            try:
                from src.utils.language_manager import get_language_manager
                self.language_manager = get_language_manager()
                self.update_window_title()
                print("✅ 言語管理システム初期化完了")
            except Exception as e:
                print(f"⚠️ 言語管理システム初期化エラー: {e}")
                self.language_manager = None
            
            # パフォーマンス最適化
            print("⚡ パフォーマンス最適化システム初期化中...")
            try:
                from src.utils.performance_optimizer import get_performance_optimizer
                self.optimizer = get_performance_optimizer()
                print("✅ パフォーマンス最適化システム初期化完了")
            except Exception as e:
                print(f"⚠️ パフォーマンス最適化システム初期化エラー: {e}")
                self.optimizer = None
            
            # ゲームフロー管理
            print("🎮 ゲームフロー管理初期化中...")
            try:
                from src.core.game_flow import GameFlowManager
                self.flow_manager = GameFlowManager(self.screen)
                print("✅ ゲームフロー管理初期化完了")
            except Exception as e:
                print(f"❌ ゲームフロー管理初期化エラー: {e}")
                raise
            
            # 初期ウィンドウタイトル設定
            self.update_window_title()
            
            # ゲーム設定
            self.clock = pygame.time.Clock()
            self.target_fps = 60 if not self.is_web else 30  # Web版はFPSを下げる
            
            print("✅ GameMain 初期化完了")
            
        except Exception as e:
            print(f"❌ GameMain 初期化エラー: {e}")
            import traceback
            traceback.print_exc()
            raise
    
    def _check_web_environment(self) -> bool:
        """Web環境かチェック"""
        try:
            from src.utils.web_utils import is_web_environment
            return is_web_environment()
        except ImportError:
            import os
            return os.environ.get('WEB_VERSION') == '1'
        
        # ゲーム設定
        self.clock = pygame.time.Clock()
        self.target_fps = 60
    
    def update_window_title(self):
        """ウィンドウタイトルを現在の言語に応じて更新"""
        title = get_text("game_title")
        pygame.display.set_caption(title)
        print(f"🪟 ウィンドウタイトル更新: '{title}'")
    
    def initialize(self) -> bool:
        """ゲーム初期化（Web版対応）"""
        try:
            print("🎮 ゲーム初期化中...")
            
            # ゲームフロー初期化
            if hasattr(self, 'flow_manager'):
                self.game_flow = self.flow_manager
            else:
                from src.core.game_flow import GameFlowManager
                self.game_flow = GameFlowManager(self.screen)
            
            print("✅ ゲーム初期化完了")
            return True
            
        except Exception as e:
            print(f"❌ ゲーム初期化エラー: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self):
        """従来のメインゲームループ（デスクトップ版）"""
        print("🖥️ デスクトップ版ゲーム開始")
        
        # 初期化
        if not self.initialize():
            return
        
        while self.game_flow.is_running():
            # パフォーマンス最適化：フレーム開始
            self.optimizer.begin_frame()
            
            # フレーム時間計算
            time_delta = self.clock.tick(self.target_fps) / 1000.0
            
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("🔴 QUIT イベント受信")
                    self.game_flow.running = False
                    break
                elif event.type == pygame.VIDEORESIZE:
                    self._handle_resize(event)
                else:
                    result = self.game_flow.handle_event(event)
                    if result == "quit":
                        print("🔴 ゲーム終了シグナル受信")
                        self.game_flow.running = False
                        break
            
            # 終了処理が要求されている場合はループを抜ける
            if not self.game_flow.is_running():
                break
            
            # 更新処理（最適化付き）
            self.optimizer.begin_update()
            result = self.game_flow.update(time_delta)
            if result == "quit":
                print("🔴 更新処理で終了シグナル受信")
                self.game_flow.running = False
                self.optimizer.end_update()
                break
            self.optimizer.end_update()
            
            # フレームスキップ判定
            should_skip = self.optimizer.end_frame()
            if should_skip:
                continue  # 描画をスキップ
            
            # 描画処理（最適化付き）
            self.optimizer.begin_draw()
            self.screen.fill((0, 0, 0))  # 背景クリア
            self.game_flow.draw(self.screen)
            self.optimizer.end_draw()
            
            # 画面更新
            pygame.display.flip()
        
        # パフォーマンスレポート表示
        print(self.optimizer.get_performance_report())
        
        print("🔴 ゲーム終了処理開始")
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
        print("🧹 クリーンアップ開始...")
        
        try:
            # ゲームフローの音声システムを停止
            if hasattr(self, 'flow_manager') and self.flow_manager:
                if hasattr(self.flow_manager, 'audio_system'):
                    print("🔇 音声システム停止中...")
                    self.flow_manager.audio_system.stop_bgm()
                    self.flow_manager.audio_system.stop_all_sfx()
        except Exception as e:
            print(f"⚠️ 音声停止エラー: {e}")
        
        try:
            # Pygameを終了
            print("🎮 Pygame終了中...")
            pygame.mixer.quit()
            pygame.quit()
            print("✅ Pygame終了完了")
        except Exception as e:
            print(f"⚠️ Pygame終了エラー: {e}")
        
        print("🔴 アプリケーション終了")
        sys.exit(0)

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
