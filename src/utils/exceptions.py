"""
ゲーム専用例外クラス
エラーハンドリングの統一化
"""

class GameError(Exception):
    """ゲーム関連の基底例外クラス"""
    def __init__(self, message: str, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code or "GAME_ERROR"

class AssetLoadError(GameError):
    """アセット読み込みエラー"""
    def __init__(self, asset_path: str, message: str = None):
        self.asset_path = asset_path
        msg = message or f"アセット読み込み失敗: {asset_path}"
        super().__init__(msg, "ASSET_LOAD_ERROR")

class SaveLoadError(GameError):
    """セーブ/ロードエラー"""
    def __init__(self, operation: str, message: str = None):
        self.operation = operation
        msg = message or f"{operation}操作に失敗しました"
        super().__init__(msg, "SAVE_LOAD_ERROR")

class ConfigError(GameError):
    """設定エラー"""
    def __init__(self, config_key: str, message: str = None):
        self.config_key = config_key
        msg = message or f"設定エラー: {config_key}"
        super().__init__(msg, "CONFIG_ERROR")

class UIError(GameError):
    """UI関連エラー"""
    def __init__(self, ui_component: str, message: str = None):
        self.ui_component = ui_component
        msg = message or f"UI エラー: {ui_component}"
        super().__init__(msg, "UI_ERROR")

class GameStateError(GameError):
    """ゲーム状態エラー"""
    def __init__(self, state: str, message: str = None):
        self.state = state
        msg = message or f"無効なゲーム状態: {state}"
        super().__init__(msg, "GAME_STATE_ERROR")

class NetworkError(GameError):
    """ネットワークエラー（将来の拡張用）"""
    def __init__(self, message: str = None):
        msg = message or "ネットワーク接続エラー"
        super().__init__(msg, "NETWORK_ERROR")

class ValidationError(GameError):
    """データ検証エラー"""
    def __init__(self, field: str, value, message: str = None):
        self.field = field
        self.value = value
        msg = message or f"データ検証エラー: {field} = {value}"
        super().__init__(msg, "VALIDATION_ERROR")
