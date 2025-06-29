#!/usr/bin/env python3
"""
3分制限タイマーシステムテスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

import time
from src.systems.timer_system import TimerSystem

def test_timer_system():
    """3分制限タイマーシステムのテスト"""
    print("⏰ 3分制限タイマーシステムテスト開始")
    print("=" * 50)
    
    # ヒントコールバック
    def on_hint(message, level):
        print(f"💡 ヒント{level}: {message}")
    
    # 警告コールバック
    def on_warning():
        print("⚠️ 時間警告: 残り30秒以下")
    
    # タイムアップコールバック
    def on_time_up():
        print("⏰ タイムアップ！")
    
    # タイマーシステム作成（3分 = 180秒）
    timer = TimerSystem(180.0)
    timer.set_hint_callback(on_hint)
    timer.set_time_warning_callback(on_warning)
    timer.set_time_up_callback(on_time_up)
    
    print(f"制限時間: {timer.time_limit}秒（{timer.time_limit/60:.1f}分）")
    print(f"残り時間: {timer.remaining_time}秒")
    
    # タイマー開始
    timer.start()
    print("🚀 タイマー開始")
    
    # 高速テスト（実際の時間の10倍速）
    test_duration = 20  # 20秒でテスト完了
    start_time = time.time()
    
    while time.time() - start_time < test_duration:
        # 10倍速でシミュレート
        elapsed = (time.time() - start_time) * 10
        
        # タイマー更新（手動で経過時間を設定）
        timer.start_time = time.time() - elapsed
        timer.update()
        
        # 状態表示
        remaining = timer.remaining_time
        if remaining > 0:
            print(f"⏱️ 残り時間: {remaining:.1f}秒 ({remaining/60:.2f}分)")
        else:
            print("⏰ 時間切れ")
            break
        
        time.sleep(0.5)  # 0.5秒待機
    
    print("\n✅ タイマーテスト完了")

def main():
    """メイン関数"""
    try:
        test_timer_system()
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
