#!/usr/bin/env python3
"""
ペット図鑑システムのデモ
実際にUIを起動して操作可能
"""

import sys
import os
import pygame
import pygame_gui
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ui.pet_collection_ui import PetCollectionUI
from src.systems.pet_collection import PetCollection

def main():
    """ペット図鑑デモのメイン関数"""
    print("🐾 ペット図鑑システム起動中...")
    
    # Pygameの初期化
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("ミステリー・ペット・レスキュー - ペット図鑑")
    clock = pygame.time.Clock()
    
    # UIマネージャーの初期化
    ui_manager = pygame_gui.UIManager((1280, 720))
    
    try:
        # ペット図鑑システムの初期化
        pet_collection = PetCollection()
        pet_ui = PetCollectionUI(screen, ui_manager)
        
        # テスト用にいくつかのペットを救助済みにする
        pet_collection.rescue_pet("dog_001", "住宅街の公園", 120)  # チョコ
        pet_collection.rescue_pet("cat_001", "路地裏", 180)       # ミケ
        pet_collection.rescue_pet("rabbit_001", "茂みの中", 240)  # ふわり
        
        print("✅ ペット図鑑システム初期化完了")
        print("\n🎮 操作方法:")
        print("  - マウス: UI操作")
        print("  - ESC: 終了")
        print("  - 検索ボックス: ペット名で検索")
        print("  - フィルター: 救助状態やレア度で絞り込み")
        print("  - ペットをクリック: 詳細表示")
        
        # UIを表示
        pet_ui.show()
        
        # 統計情報を表示
        stats = pet_collection.get_collection_stats()
        print(f"\n📊 現在の図鑑状況:")
        print(f"  完成率: {stats['completion_rate']:.1f}%")
        print(f"  救助済み: {stats['rescued_pets']}/{stats['total_pets']}匹")
        
        running = True
        
        while running:
            time_delta = clock.tick(60) / 1000.0
            
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                
                # UIイベント処理
                ui_manager.process_events(event)
                result = pet_ui.handle_event(event)
                
                # ペット詳細表示の結果をチェック
                if result:
                    print(f"🐾 ペット選択: {result}")
            
            # 更新
            ui_manager.update(time_delta)
            pet_ui.update(time_delta)
            
            # 描画
            screen.fill((240, 248, 255))  # アリスブルー背景
            
            # タイトル表示
            font = pygame.font.Font(None, 48)
            title_text = font.render("ペット図鑑", True, (50, 50, 50))
            title_rect = title_text.get_rect(center=(640, 50))
            screen.blit(title_text, title_rect)
            
            # UI描画
            ui_manager.draw_ui(screen)
            pet_ui.draw(screen)
            
            pygame.display.flip()
        
        print("\n🎉 ペット図鑑システム終了")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
