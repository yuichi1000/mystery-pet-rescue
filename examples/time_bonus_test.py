#!/usr/bin/env python3
"""
タイムボーナス計算テスト
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.timer_system import TimerSystem

def test_time_bonus():
    """タイムボーナス計算のテスト"""
    print("⏰ タイムボーナス計算テスト開始")
    print("=" * 50)
    
    # タイマーシステム作成（3分 = 180秒）
    timer = TimerSystem(180.0)
    
    # 様々な残り時間でボーナス計算テスト
    test_times = [180.0, 150.0, 120.0, 90.0, 60.0, 30.0, 15.0, 5.0, 0.0]
    
    print("残り時間    タイムボーナス")
    print("-" * 30)
    
    for remaining in test_times:
        timer.remaining_time = remaining
        bonus = timer.calculate_time_bonus()
        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        
        print(f"{remaining:6.1f}秒 ({minutes:02d}:{seconds:02d}) → {bonus:4d}点")
    
    print(f"\n📊 ボーナス計算式:")
    print(f"  残り秒数 × 10点")
    print(f"  例: 120秒残り → 120 × 10 = 1200点")
    
    # 実際のゲーム終了シナリオテスト
    print(f"\n🎮 ゲーム終了シナリオ:")
    scenarios = [
        ("完璧クリア", 180.0),
        ("余裕でクリア", 120.0),
        ("普通にクリア", 60.0),
        ("ギリギリクリア", 10.0),
        ("タイムアップ", 0.0)
    ]
    
    for scenario_name, time_left in scenarios:
        timer.remaining_time = time_left
        bonus = timer.calculate_time_bonus()
        base_score = 4000  # 4匹救出 × 1000点
        total_score = base_score + bonus
        
        print(f"  {scenario_name:12s}: {bonus:4d}点ボーナス → 総合{total_score:5d}点")
    
    print("\n✅ タイムボーナステスト完了")

def main():
    """メイン関数"""
    try:
        test_time_bonus()
        
    except Exception as e:
        print(f"❌ テストエラー: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
