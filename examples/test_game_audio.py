#!/usr/bin/env python3
"""
ゲーム内音響システムのテスト
"""

import pygame
import sys
import time
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.audio_system import get_audio_system

def test_game_audio_integration():
    """ゲーム内音響統合テスト"""
    print("🎮 ゲーム内音響統合テスト開始")
    
    # Pygame初期化
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("ゲーム音響テスト")
    clock = pygame.time.Clock()
    
    # 音響システム取得
    audio_system = get_audio_system()
    
    print("🎵 ゲームシナリオテスト:")
    print("1. ゲーム開始...")
    
    # シナリオ1: ペット発見
    print("2. ペットを発見！")
    audio_system.play_sfx('pet_found')
    time.sleep(2)
    
    print("3. ペットと相互作用...")
    time.sleep(1)
    
    # シナリオ2: ペット救出（まだファイルがないのでエラーになるが、システムは動作）
    print("4. ペット救出を試行...")
    success = audio_system.play_sfx('pet_rescued')
    if success:
        print("✅ ペット救出音再生成功")
    else:
        print("⚠️ ペット救出音ファイルなし（予想通り）")
    
    print("5. テスト完了")
    
    # クリーンアップ
    audio_system.cleanup()
    pygame.quit()
    print("🎮 ゲーム内音響統合テスト完了")

if __name__ == "__main__":
    test_game_audio_integration()
