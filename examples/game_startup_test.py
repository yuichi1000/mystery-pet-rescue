#!/usr/bin/env python3
"""
ゲーム起動とペット配置テスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import pygame
from src.scenes.game import GameScene

def test_game_startup():
    """ゲーム起動とペット配置のテスト"""
    print("🎮 ゲーム起動とペット配置テスト開始")
    print("=" * 50)
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    
    try:
        # ゲームシーン作成
        print("🎯 ゲームシーン作成中...")
        game_scene = GameScene(screen)
        
        # シーンに入る（ペット配置が実行される）
        print("🚀 ゲームシーン開始...")
        game_scene.enter()
        
        # ペット配置結果を確認
        print(f"\n🐾 ペット配置結果:")
        print(f"  配置されたペット数: {len(game_scene.pets)}匹")
        
        for i, pet in enumerate(game_scene.pets):
            print(f"  {i+1}. {pet.data.name} ({pet.data.pet_type.value}): ({pet.x:.1f}, {pet.y:.1f})")
        
        # プレイヤー位置も確認
        print(f"\n👤 プレイヤー位置: ({game_scene.player.x:.1f}, {game_scene.player.y:.1f})")
        
        # 距離チェック
        print(f"\n📏 プレイヤーからの距離:")
        for i, pet in enumerate(game_scene.pets):
            distance = ((pet.x - game_scene.player.x) ** 2 + (pet.y - game_scene.player.y) ** 2) ** 0.5
            print(f"  {pet.data.name}: {distance:.1f}ピクセル")
        
        print(f"\n✅ ゲーム起動テスト完了")
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        pygame.quit()

def main():
    """メイン関数"""
    test_game_startup()

if __name__ == "__main__":
    main()
