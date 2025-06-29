#!/usr/bin/env python3
"""
ペットランダム配置システムテスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
import random
from src.systems.map_system import MapSystem
from src.entities.pet import PetType

def test_random_placement():
    """ランダム配置システムのテスト"""
    print("🎲 ペットランダム配置システムテスト開始")
    print("=" * 50)
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    
    # マップシステム初期化
    map_system = MapSystem()
    
    # マップサイズを取得
    if map_system.current_map:
        map_width = map_system.current_map.width * map_system.tile_size
        map_height = map_system.current_map.height * map_system.tile_size
    else:
        # デフォルトマップサイズ
        map_width = 1600  # 25 * 64
        map_height = 1280  # 20 * 64
    
    print(f"📏 マップサイズ: {map_width} x {map_height}")
    print(f"📐 タイルサイズ: {map_system.tile_size}")
    
    # ランダム位置生成テスト
    print("\n🎯 ランダム位置生成テスト:")
    print("-" * 30)
    
    valid_positions = []
    invalid_positions = []
    
    for i in range(20):
        # ランダム位置を生成
        margin = 100
        x = random.uniform(margin, map_width - margin)
        y = random.uniform(margin, map_height - margin)
        
        # 通過可能かチェック
        is_walkable = map_system.is_walkable(x, y)
        
        if is_walkable:
            valid_positions.append((x, y))
            status = "✅ 有効"
        else:
            invalid_positions.append((x, y))
            status = "❌ 無効"
        
        tile_type = map_system.get_tile_at_position(x, y)
        tile_name = tile_type.value if tile_type else "unknown"
        print(f"位置 {i+1:2d}: ({x:6.1f}, {y:6.1f}) - {tile_name:12s} - {status}")
    
    print(f"\n📊 結果:")
    print(f"  ✅ 有効な位置: {len(valid_positions)}個")
    print(f"  ❌ 無効な位置: {len(invalid_positions)}個")
    print(f"  📈 成功率: {len(valid_positions)/20*100:.1f}%")
    
    # 実際のペット配置シミュレーション
    print(f"\n🐾 ペット配置シミュレーション:")
    print("-" * 30)
    
    pet_types = [PetType.DOG, PetType.CAT, PetType.RABBIT, PetType.BIRD]
    placed_pets = []
    
    for i, pet_type in enumerate(pet_types):
        # 適切な位置を探す
        position = find_random_walkable_position(map_system, map_width, map_height)
        if position:
            x, y = position
            placed_pets.append((pet_type, x, y))
            print(f"  🐾 {pet_type.value:8s}: ({x:6.1f}, {y:6.1f}) ✅")
        else:
            print(f"  🐾 {pet_type.value:8s}: 配置失敗 ❌")
    
    print(f"\n✅ 配置成功: {len(placed_pets)}/4匹")
    
    pygame.quit()
    print("\n✅ ランダム配置テスト完了")

def find_random_walkable_position(map_system, map_width, map_height, max_attempts=100):
    """通過可能なランダム位置を見つける"""
    margin = 100
    
    for attempt in range(max_attempts):
        x = random.uniform(margin, map_width - margin)
        y = random.uniform(margin, map_height - margin)
        
        if map_system.is_walkable(x, y):
            return (x, y)
    
    return None

def main():
    """メイン関数"""
    try:
        test_random_placement()
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
