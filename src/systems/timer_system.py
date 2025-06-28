"""
時間制限システム
5分のタイマーとヒントシステムを管理
"""

import time
from typing import Optional, Callable
from enum import Enum

class TimerState(Enum):
    """タイマーの状態"""
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"

class TimerSystem:
    """時間制限システム"""
    
    def __init__(self, time_limit: float = 300.0):  # 5分 = 300秒
        self.time_limit = time_limit
        self.remaining_time = time_limit
        self.start_time: Optional[float] = None
        self.pause_time: Optional[float] = None
        self.state = TimerState.PAUSED
        
        # ヒントフラグ
        self.hint_2min_shown = False
        self.hint_3min_shown = False
        self.hint_4min_shown = False
        
        # コールバック関数
        self.on_hint_callback: Optional[Callable[[str, int], None]] = None
        self.on_time_warning_callback: Optional[Callable[[], None]] = None
        self.on_time_up_callback: Optional[Callable[[], None]] = None
    
    def start(self):
        """タイマー開始"""
        if self.state == TimerState.PAUSED:
            current_time = time.time()
            if self.start_time is None:
                self.start_time = current_time
            elif self.pause_time is not None:
                # 一時停止からの再開
                pause_duration = current_time - self.pause_time
                self.start_time += pause_duration
                self.pause_time = None
            
            self.state = TimerState.RUNNING
    
    def pause(self):
        """タイマー一時停止"""
        if self.state == TimerState.RUNNING:
            self.pause_time = time.time()
            self.state = TimerState.PAUSED
    
    def reset(self):
        """タイマーリセット"""
        self.remaining_time = self.time_limit
        self.start_time = None
        self.pause_time = None
        self.state = TimerState.PAUSED
        
        # ヒントフラグリセット
        self.hint_2min_shown = False
        self.hint_3min_shown = False
        self.hint_4min_shown = False
    
    def update(self):
        """タイマー更新"""
        if self.state != TimerState.RUNNING or self.start_time is None:
            return
        
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        self.remaining_time = max(0, self.time_limit - elapsed_time)
        
        # ヒントシステム
        self._check_hints(elapsed_time)
        
        # 時間警告（30秒以下）
        if self.remaining_time <= 30 and self.remaining_time > 0:
            if self.on_time_warning_callback:
                self.on_time_warning_callback()
        
        # 時間切れ
        if self.remaining_time <= 0:
            self.state = TimerState.FINISHED
            if self.on_time_up_callback:
                self.on_time_up_callback()
    
    def _check_hints(self, elapsed_time: float):
        """ヒント表示チェック"""
        if elapsed_time >= 120 and not self.hint_2min_shown:  # 2分
            self.hint_2min_shown = True
            if self.on_hint_callback:
                self.on_hint_callback("ペットの鳴き声が聞こえます", 2)
        
        elif elapsed_time >= 180 and not self.hint_3min_shown:  # 3分
            self.hint_3min_shown = True
            if self.on_hint_callback:
                self.on_hint_callback("足跡を発見しました", 3)
        
        elif elapsed_time >= 240 and not self.hint_4min_shown:  # 4分
            self.hint_4min_shown = True
            if self.on_hint_callback:
                self.on_hint_callback("ペットが近くにいます", 4)
    
    def get_time_string(self) -> str:
        """時間をMM:SS形式で取得"""
        minutes = int(self.remaining_time // 60)
        seconds = int(self.remaining_time % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def get_progress_ratio(self) -> float:
        """進行率を0.0-1.0で取得"""
        return (self.time_limit - self.remaining_time) / self.time_limit
    
    def is_warning_time(self) -> bool:
        """警告時間（30秒以下）かどうか"""
        return self.remaining_time <= 30 and self.remaining_time > 0
    
    def is_finished(self) -> bool:
        """時間切れかどうか"""
        return self.state == TimerState.FINISHED
    
    def is_running(self) -> bool:
        """実行中かどうか"""
        return self.state == TimerState.RUNNING
    
    def set_hint_callback(self, callback: Callable[[str, int], None]):
        """ヒントコールバック設定"""
        self.on_hint_callback = callback
    
    def set_time_warning_callback(self, callback: Callable[[], None]):
        """時間警告コールバック設定"""
        self.on_time_warning_callback = callback
    
    def set_time_up_callback(self, callback: Callable[[], None]):
        """時間切れコールバック設定"""
        self.on_time_up_callback = callback
    
    def calculate_time_bonus(self) -> int:
        """タイムボーナス計算"""
        return int(self.remaining_time * 10)  # 残り秒数 × 10
