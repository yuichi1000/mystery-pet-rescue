"""
エラーハンドリングシステム
統一されたエラー処理とログ記録
"""

import logging
import traceback
import sys
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime

from src.utils.exceptions import GameError

class ErrorHandler:
    """エラーハンドリングクラス"""
    
    def __init__(self, log_file: str = "logs/game_errors.log"):
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(exist_ok=True)
        
        # ロガー設定
        self.logger = logging.getLogger("GameErrorHandler")
        self.logger.setLevel(logging.DEBUG)
        
        # ファイルハンドラー
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.ERROR)
        
        # コンソールハンドラー
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.WARNING)
        
        # フォーマッター
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # ハンドラー追加
        if not self.logger.handlers:
            self.logger.addHandler(file_handler)
            self.logger.addHandler(console_handler)
        
        # エラー統計
        self.error_stats = {
            'total_errors': 0,
            'error_types': {},
            'last_error_time': None
        }
    
    def handle_error(self, error: Exception, context: str = None, 
                    critical: bool = False) -> bool:
        """
        エラーを処理
        
        Args:
            error: 発生したエラー
            context: エラーが発生したコンテキスト
            critical: クリティカルエラーかどうか
            
        Returns:
            bool: 処理継続可能かどうか
        """
        # エラー情報の収集
        error_info = self._collect_error_info(error, context)
        
        # ログ記録
        self._log_error(error_info, critical)
        
        # 統計更新
        self._update_stats(error_info)
        
        # ユーザー通知
        self._notify_user(error_info, critical)
        
        # 処理継続可能性の判定
        return not critical and self._is_recoverable(error)
    
    def _collect_error_info(self, error: Exception, context: str = None) -> Dict[str, Any]:
        """エラー情報を収集"""
        return {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or 'Unknown',
            'traceback': traceback.format_exc(),
            'error_code': getattr(error, 'error_code', None)
        }
    
    def _log_error(self, error_info: Dict[str, Any], critical: bool):
        """エラーをログに記録"""
        log_message = (
            f"[{error_info['context']}] "
            f"{error_info['error_type']}: {error_info['error_message']}"
        )
        
        if critical:
            self.logger.critical(log_message)
            self.logger.critical(f"Traceback:\n{error_info['traceback']}")
        else:
            self.logger.error(log_message)
            self.logger.debug(f"Traceback:\n{error_info['traceback']}")
    
    def _update_stats(self, error_info: Dict[str, Any]):
        """エラー統計を更新"""
        self.error_stats['total_errors'] += 1
        self.error_stats['last_error_time'] = error_info['timestamp']
        
        error_type = error_info['error_type']
        if error_type not in self.error_stats['error_types']:
            self.error_stats['error_types'][error_type] = 0
        self.error_stats['error_types'][error_type] += 1
    
    def _notify_user(self, error_info: Dict[str, Any], critical: bool):
        """ユーザーにエラーを通知"""
        if critical:
            print(f"❌ 重大なエラーが発生しました: {error_info['error_message']}")
        else:
            print(f"⚠️ エラーが発生しましたが、処理を続行します: {error_info['error_message']}")
    
    def _is_recoverable(self, error: Exception) -> bool:
        """エラーが回復可能かどうか判定"""
        # 回復不可能なエラータイプ
        unrecoverable_types = (
            MemoryError,
            SystemExit,
            KeyboardInterrupt,
            SystemError
        )
        
        if isinstance(error, unrecoverable_types):
            return False
        
        # GameErrorは基本的に回復可能
        if isinstance(error, GameError):
            return True
        
        # その他のエラーは種類によって判定
        recoverable_types = (
            FileNotFoundError,
            ValueError,
            TypeError,
            AttributeError,
            KeyError,
            IndexError
        )
        
        return isinstance(error, recoverable_types)
    
    def get_error_stats(self) -> Dict[str, Any]:
        """エラー統計を取得"""
        return self.error_stats.copy()
    
    def clear_stats(self):
        """エラー統計をクリア"""
        self.error_stats = {
            'total_errors': 0,
            'error_types': {},
            'last_error_time': None
        }

# グローバルエラーハンドラー
_global_error_handler = None

def get_error_handler() -> ErrorHandler:
    """グローバルエラーハンドラーを取得"""
    global _global_error_handler
    if _global_error_handler is None:
        _global_error_handler = ErrorHandler()
    return _global_error_handler

def handle_error(error: Exception, context: str = None, critical: bool = False) -> bool:
    """エラーを処理（便利関数）"""
    return get_error_handler().handle_error(error, context, critical)

def safe_execute(func, *args, context: str = None, default=None, **kwargs):
    """
    安全に関数を実行
    
    Args:
        func: 実行する関数
        *args: 関数の引数
        context: エラーコンテキスト
        default: エラー時のデフォルト値
        **kwargs: 関数のキーワード引数
        
    Returns:
        関数の戻り値またはデフォルト値
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        handle_error(e, context or f"safe_execute({func.__name__})")
        return default
