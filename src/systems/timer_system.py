"""
時間制限システム
3分のタイマーシステムを管理
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
    
    def __init__(self, time_limit: float = 180.0):  # 3分 = 180秒
        self.time_limit = time_limit
        self.remaining_time = time_limit
        self.start_time: Optional[float] = None
        self.pause_time: Optional[float] = None
        self.state = TimerState.PAUSED
        
        # コールバック関数
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
    
    def update(self):
        """タイマー更新"""
        if self.state != TimerState.RUNNING or self.start_time is None:
            return
        
        current_time = time.time()
        elapsed_time = current_time - self.start_time
        self.remaining_time = max(0, self.time_limit - elapsed_time)
        
        # 時間警告（30秒以下）
        if self.remaining_time <= 30 and self.remaining_time > 0:
            if self.on_time_warning_callback:
                self.on_time_warning_callback()
        
        # 時間切れ
        if self.remaining_time <= 0:
            self.state = TimerState.FINISHED
            if self.on_time_up_callback:
                self.on_time_up_callback()
    
    def set_time_warning_callback(self, callback: Callable[[], None]):
        """時間警告コールバック設定"""
        self.on_time_warning_callback = callback
    
    def set_time_up_callback(self, callback: Callable[[], None]):
        """タイムアップコールバック設定"""
        self.on_time_up_callback = callback
    
    def is_running(self) -> bool:
        """タイマーが動作中かチェック"""
        return self.state == TimerState.RUNNING
    
    def is_finished(self) -> bool:
        """タイマーが終了したかチェック"""
        return self.state == TimerState.FINISHED
    
    def get_remaining_time(self) -> float:
        """残り時間を取得"""
        return self.remaining_time
    
    def get_remaining_minutes(self) -> int:
        """残り時間（分）を取得"""
        return int(self.remaining_time // 60)
    
    def get_remaining_seconds(self) -> int:
        """残り時間（秒）を取得"""
        return int(self.remaining_time % 60)
    
    def get_time_string(self) -> str:
        """残り時間を文字列形式で取得 (MM:SS)"""
        minutes = self.get_remaining_minutes()
        seconds = self.get_remaining_seconds()
        return f"{minutes:02d}:{seconds:02d}"
    
    def is_warning_time(self) -> bool:
        """警告時間（残り30秒以下）かどうかチェック"""
        return self.remaining_time <= 30 and self.remaining_time > 0
    
    def calculate_time_bonus(self) -> int:
        """残り時間に基づくタイムボーナスを計算"""
        if self.remaining_time <= 0:
            return 0
        # 残り秒数 × 10点のボーナス
        return int(self.remaining_time * 10)
