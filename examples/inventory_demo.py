#!/usr/bin/env python3
"""
インベントリシステムのデモ
アイテム管理、UI、ドラッグ&ドロップ、組み合わせ機能のテスト
"""

import sys
import os
import pygame
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.scenes.inventory_scene import InventoryScene

def main():
    """インベントリデモのメイン関数"""
    print("🎒 インベントリシステムデモ起動中...")
    
    # Pygameの初期化
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("ミステリー・ペット・レスキュー - インベントリシステム")
    clock = pygame.time.Clock()
    
    try:
        # インベントリシーンの初期化
        inventory_scene = InventoryScene(screen)
        inventory_scene.enter()
        
        print("✅ インベントリシステム初期化完了")
        print("\n🎮 操作方法:")
        print("  - 左クリック: アイテム選択")
        print("  - Ctrl+左クリック: 複数選択")
        print("  - ドラッグ&ドロップ: アイテム移動")
        print("  - 使用ボタン: 選択したアイテムを使用")
        print("  - 組み合わせボタン: 選択したアイテムを組み合わせ")
        print("  - マウスホバー: アイテム詳細表示")
        print("  - ESC: 終了")
        
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
                
                # シーンのイベント処理
                result = inventory_scene.handle_event(event)
                if result == "menu":
                    running = False
            
            # 更新
            inventory_scene.update(time_delta)
            
            # 描画
            inventory_scene.draw(screen)
            pygame.display.flip()
        
        print("\n🎉 インベントリシステムデモ終了")
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()
