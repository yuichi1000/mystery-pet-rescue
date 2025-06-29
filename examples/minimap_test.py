#!/usr/bin/env python3
"""
ミニマップ改善テスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from src.ui.game_ui import GameUI
from src.systems.map_system import MapSystem
from src.entities.pet import Pet, PetData, PetType

def test_minimap():
    """ミニマップの改善テスト"""
    print("🗺️ ミニマップ改善テスト開始")
    print("=" * 50)
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("ミニマップテスト")
    
    try:
        # マップシステム初期化
        map_system = MapSystem()
        
        # GameUI初期化
        game_ui = GameUI(screen)
        game_ui.map_system = map_system  # マップシステムを設定
        game_ui._setup_ui_layout()  # UIレイアウト初期化
        
        # テスト用ペット作成
        pets = []
        pet_data = [
            ("dog", PetType.DOG, 300, 200),
            ("cat", PetType.CAT, 500, 300),
            ("rabbit", PetType.RABBIT, 700, 400),
            ("bird", PetType.BIRD, 400, 150)
        ]
        
        for name, pet_type, x, y in pet_data:
            data = PetData(
                pet_id=f"{name}_001",
                name=name,
                pet_type=pet_type,
                personality="test",
                rarity="common",
                description=f"テスト用{name}"
            )
            pet = Pet(data, x=x, y=y)
            pets.append(pet)
        
        print(f"📊 ミニマップサイズ: {game_ui.minimap_size}x{game_ui.minimap_size}")
        print(f"📐 ミニマップ位置: {game_ui.minimap_rect}")
        print(f"🐾 テストペット数: {len(pets)}匹")
        
        # プレイヤー位置
        player_pos = (100, 100)
        
        # 描画テスト
        clock = pygame.time.Clock()
        running = True
        frame_count = 0
        
        while running and frame_count < 300:  # 5秒間テスト
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            
            # 背景クリア
            screen.fill((40, 40, 40))
            
            # ミニマップ描画
            game_ui._draw_minimap(pets, player_pos, map_system)
            
            # 情報表示
            font = pygame.font.Font(None, 24)
            info_texts = [
                f"ミニマップサイズ: {game_ui.minimap_size}x{game_ui.minimap_size}",
                f"プレイヤー位置: ({player_pos[0]}, {player_pos[1]})",
                f"ペット数: {len(pets)}匹",
                "ESCで終了"
            ]
            
            for i, text in enumerate(info_texts):
                surface = font.render(text, True, (255, 255, 255))
                screen.blit(surface, (20, 20 + i * 30))
            
            pygame.display.flip()
            clock.tick(60)
            frame_count += 1
            
            # ESCキーで終了
            keys = pygame.key.get_pressed()
            if keys[pygame.K_ESCAPE]:
                break
        
        print("✅ ミニマップテスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

def main():
    """メイン関数"""
    test_minimap()

if __name__ == "__main__":
    main()
