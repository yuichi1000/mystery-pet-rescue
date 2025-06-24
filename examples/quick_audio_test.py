#!/usr/bin/env python3
"""
音響システムの簡単なテスト
"""

import pygame
import sys
import time
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.audio_system import get_audio_system

def quick_audio_test():
    """音響システムの簡単なテスト"""
    print("🎵 音響システム簡単テスト開始")
    
    # Pygame初期化
    pygame.init()
    
    # 音響システム取得
    audio_system = get_audio_system()
    
    print(f"利用可能なBGM: {audio_system.get_bgm_list()}")
    print(f"利用可能な効果音: {audio_system.get_sfx_list()}")
    
    # pet_found効果音があるかチェック
    if 'pet_found' in audio_system.get_sfx_list():
        print("✅ pet_found.wav が正常に読み込まれました")
        
        # 効果音再生テスト
        print("🔊 pet_found効果音を再生...")
        success = audio_system.play_sfx('pet_found')
        
        if success:
            print("✅ 効果音再生成功")
            time.sleep(2)  # 再生時間を待つ
        else:
            print("❌ 効果音再生失敗")
    else:
        print("❌ pet_found.wav が見つかりません")
    
    # クリーンアップ
    audio_system.cleanup()
    pygame.quit()
    print("🎵 テスト完了")

if __name__ == "__main__":
    quick_audio_test()
