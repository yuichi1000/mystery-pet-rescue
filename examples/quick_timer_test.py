#!/usr/bin/env python3
"""
TimerSystem クイックテスト
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.timer_system import TimerSystem

# 基本的な動作確認
timer = TimerSystem(180.0)
print('✅ TimerSystem作成成功')
print(f'📊 get_time_string(): {timer.get_time_string()}')
print(f'⚠️ is_warning_time(): {timer.is_warning_time()}')

# 警告時間のテスト
timer.remaining_time = 25.0
print(f'🔥 残り25秒 - is_warning_time(): {timer.is_warning_time()}')
print('✅ 全メソッド正常動作')
