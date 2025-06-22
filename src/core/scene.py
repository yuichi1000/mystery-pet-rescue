"""
シーン基底クラス
ゲームの各画面（シーン）の基本構造を定義
"""

import pygame
from abc import ABC, abstractmethod
from typing import Optional

class Scene(ABC):
    """シーン基底クラス"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
    
    @abstractmethod
    def enter(self) -> None:
        """シーンに入る時の処理"""
        pass
    
    @abstractmethod
    def exit(self) -> None:
        """シーンから出る時の処理"""
        pass
    
    @abstractmethod
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """
        イベント処理
        
        Returns:
            Optional[str]: 次のシーン名（シーン変更がない場合はNone）
        """
        pass
    
    @abstractmethod
    def update(self, time_delta: float) -> Optional[str]:
        """
        更新処理
        
        Args:
            time_delta: 前フレームからの経過時間（秒）
            
        Returns:
            Optional[str]: 次のシーン名（シーン変更がない場合はNone）
        """
        pass
    
    @abstractmethod
    def draw(self, surface: pygame.Surface) -> None:
        """
        描画処理
        
        Args:
            surface: 描画対象のサーフェス
        """
        pass
