#!/usr/bin/env python3
"""
TimerSystem get_time_string() と is_warning_time() メソッドテスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.timer_system import TimerSystem

def test_timer_methods():
    """get_time_string()とis_warning_time()メソッドのテスト"""
    print("⏰ TimerSystemメソッドテスト開始")
    print("=" * 50)
    
    # タイマーシステム作成（3分 = 180秒）
    timer = TimerSystem(180.0)
    
    # 様々な残り時間でテスト
    test_times = [180.0, 120.5, 90.0, 60.3, 45.0, 30.0, 25.7, 10.0, 5.2, 0.0]
    
    print("残り時間    時間表示  警告状態")
    print("-" * 35)
    
    for remaining in test_times:
        timer.remaining_time = remaining
        time_string = timer.get_time_string()
        is_warning = timer.is_warning_time()
        warning_text = "⚠️ 警告" if is_warning else "   通常"
        
        print(f"{remaining:6.1f}秒 → {time_string}   {warning_text}")
    
    print("\n✅ TimerSystemメソッドテスト完了")

def main():
    """メイン関数"""
    try:
        test_timer_methods()
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
