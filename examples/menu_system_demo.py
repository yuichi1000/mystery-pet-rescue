#!/usr/bin/env python3
"""
メニューシステムデモ
階層的なメニュー管理とスムーズな画面遷移のデモンストレーション
"""

import sys
import pygame
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.menu_system import MenuSystem, MenuState
from src.ui.settings_menu import SettingsMenu
from src.ui.pet_collection_menu import PetCollectionMenu
from src.ui.save_load_menu import SaveLoadMenu

class MenuDemo:
    """メニューデモクラス"""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("メニューシステムデモ - 階層的メニュー管理")
        self.clock = pygame.time.Clock()
        
        # メニューシステム
        self.menu_system = MenuSystem(self.screen)
        
        # サブメニュー
        self.settings_menu = None
        self.pet_collection_menu = None
        self.save_load_menu = None
        
        # ゲーム状態
        self.running = True
        self.in_game = False
        
        print("🎮 メニューシステムデモ起動完了")
        print("🎯 利用可能な機能:")
        print("  - 階層的メニュー管理")
        print("  - スムーズな画面遷移")
        print("  - 設定メニュー（音量・キー設定）")
        print("  - ペット図鑑")
        print("  - セーブ/ロードシステム")
        print("  - ポーズメニュー")
    
    def run(self):
        """メインループ"""
        while self.running:
            time_delta = self.clock.tick(60) / 1000.0
            events = pygame.event.get()
            
            # 終了チェック
            for event in events:
                if event.type == pygame.QUIT:
                    self.running = False
            
            # 更新
            self.update(time_delta, events)
            
            # 描画
            self.draw()
            
            pygame.display.flip()
        
        # クリーンアップ
        self.cleanup()
    
    def update(self, time_delta: float, events: list):
        """更新処理"""
        current_state = self.menu_system.current_state
        
        if current_state == MenuState.GAME:
            self._update_game(time_delta, events)
        
        elif current_state == MenuState.SETTINGS:
            self._update_settings(events)
        
        elif current_state == MenuState.PET_COLLECTION:
            self._update_pet_collection(events)
        
        elif current_state == MenuState.SAVE_LOAD:
            self._update_save_load(events)
        
        elif current_state == MenuState.QUIT:
            self.running = False
        
        else:
            # メインメニューシステムの更新
            result = self.menu_system.update(time_delta, events)
            if result == MenuState.QUIT:
                self.running = False
    
    def _update_game(self, time_delta: float, events: list):
        """ゲーム中の更新"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_TAB:
                    # ポーズメニューを開く
                    self.menu_system.push_state(MenuState.PAUSE)
                    self.menu_system.start_transition(MenuState.PAUSE)
                    return
        
        # 簡単なゲームシミュレーション
        # 実際のゲームロジックをここに実装
    
    def _update_settings(self, events: list):
        """設定メニューの更新"""
        if not self.settings_menu:
            self.settings_menu = SettingsMenu(self.screen, self.menu_system.get_settings())
        
        updated_settings = self.settings_menu.update(events)
        
        # 設定の更新をメニューシステムに反映
        for key, value in updated_settings.items():
            self.menu_system.update_setting(key, value)
        
        # 戻るキーの処理
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.settings_menu = None
                    self.menu_system.pop_state()
                    return
    
    def _update_pet_collection(self, events: list):
        """ペット図鑑の更新"""
        if not self.pet_collection_menu:
            self.pet_collection_menu = PetCollectionMenu(self.screen)
            # サンプルペットを発見済みにする
            self.pet_collection_menu.discover_pet("cat_001", "住宅街")
            self.pet_collection_menu.discover_pet("dog_001", "公園")
        
        result = self.pet_collection_menu.update(events)
        if result == "back":
            self.pet_collection_menu = None
            self.menu_system.pop_state()
    
    def _update_save_load(self, events: list):
        """セーブ/ロードの更新"""
        if not self.save_load_menu:
            self.save_load_menu = SaveLoadMenu(self.screen)
        
        result = self.save_load_menu.update(events)
        if result == "back":
            self.save_load_menu = None
            self.menu_system.pop_state()
        elif result == "save_complete":
            print("💾 セーブ完了")
        elif result == "load_complete":
            print("📂 ロード完了")
            # ゲーム状態をロードしたデータに更新
            self.menu_system.current_state = MenuState.GAME
    
    def draw(self):
        """描画処理"""
        current_state = self.menu_system.current_state
        
        if current_state == MenuState.GAME:
            self._draw_game()
        
        elif current_state == MenuState.SETTINGS:
            if self.settings_menu:
                self.settings_menu.draw()
        
        elif current_state == MenuState.PET_COLLECTION:
            if self.pet_collection_menu:
                self.pet_collection_menu.draw()
        
        elif current_state == MenuState.SAVE_LOAD:
            if self.save_load_menu:
                self.save_load_menu.draw()
        
        else:
            # メインメニューシステムの描画
            self.menu_system.draw()
    
    def _draw_game(self):
        """ゲーム画面の描画"""
        # 簡単なゲーム画面のシミュレーション
        self.screen.fill((50, 100, 50))  # 緑の背景
        
        # ゲームタイトル
        font_manager = self.menu_system.font_manager
        title_surface = font_manager.render_text("ゲーム中", 48, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(self.screen.get_width() // 2, 200))
        self.screen.blit(title_surface, title_rect)
        
        # 操作説明
        help_text = "ESC または TAB でポーズメニュー"
        help_surface = font_manager.render_text(help_text, 24, (255, 255, 255))
        help_rect = help_surface.get_rect(center=(self.screen.get_width() // 2, 300))
        self.screen.blit(help_surface, help_rect)
        
        # ゲーム情報
        info_texts = [
            "現在の場所: 住宅街",
            "発見したペット: 2匹",
            "プレイ時間: 01:23:45",
            "進行度: 45%"
        ]
        
        for i, text in enumerate(info_texts):
            info_surface = font_manager.render_text(text, 18, (255, 255, 255))
            self.screen.blit(info_surface, (100, 400 + i * 30))
    
    def cleanup(self):
        """クリーンアップ"""
        self.menu_system.cleanup()
        pygame.quit()
        print("🧹 メニューシステムデモ終了")

def main():
    """メイン関数"""
    print("🎮 メニューシステムデモ起動中...")
    
    try:
        demo = MenuDemo()
        demo.run()
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
