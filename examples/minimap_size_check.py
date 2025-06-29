#!/usr/bin/env python3
"""
ミニマップサイズ確認テスト
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from src.ui.game_ui import GameUI

def check_minimap_size():
    """ミニマップサイズの確認"""
    print("🗺️ ミニマップサイズ確認テスト")
    print("=" * 40)
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    
    # GameUI作成
    game_ui = GameUI(screen)
    
    print(f"📊 ミニマップサイズ: {game_ui.minimap_size}x{game_ui.minimap_size}")
    print(f"📐 ミニマップ位置: {game_ui.minimap_rect}")
    print(f"🎯 UI スケール: {game_ui.ui_scale:.2f}")
    print(f"📱 画面サイズ: {screen.get_width()}x{screen.get_height()}")
    
    # 元のサイズと比較
    original_size = int(200 * game_ui.ui_scale)
    current_size = game_ui.minimap_size
    reduction_ratio = current_size / original_size
    
    print(f"\n📈 サイズ比較:")
    print(f"  元のサイズ: {original_size}x{original_size}")
    print(f"  現在のサイズ: {current_size}x{current_size}")
    print(f"  縮小率: {reduction_ratio:.2f} ({reduction_ratio*100:.0f}%)")
    
    if abs(reduction_ratio - 0.25) < 0.01:
        print("✅ 4分の1サイズに正しく縮小されています")
    else:
        print("❌ サイズが期待値と異なります")
    
    pygame.quit()
    print("\n✅ サイズ確認完了")

if __name__ == "__main__":
    check_minimap_size()
