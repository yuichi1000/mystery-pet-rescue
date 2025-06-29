"""
Web環境対応ユーティリティ
Pygbag・ブラウザ環境での動作をサポート
"""

import os
import sys
from pathlib import Path
from typing import Optional, Dict, Any

def is_web_environment() -> bool:
    """Web環境（Pygbag）で実行されているかチェック"""
    return (
        os.environ.get('WEB_VERSION') == '1' or
        hasattr(sys, 'platform') and 'emscripten' in sys.platform or
        'pygbag' in sys.modules
    )

def get_web_safe_path(path: str) -> str:
    """Web環境で安全なパスを取得"""
    if is_web_environment():
        # Web環境では相対パスを使用
        return path.replace('\\', '/')
    else:
        # デスクトップ環境では通常のパス
        return str(Path(path))

def get_default_config() -> Dict[str, Any]:
    """Web環境用のデフォルト設定"""
    return {
        # 音楽・音声設定
        'BEATOVEN_API_KEY': None,  # Web版では無効
        'BEATOVEN_API_URL': None,
        'USE_MOCK_API': True,  # モック音声を使用
        
        # ゲーム設定
        'DEBUG_MODE': False,
        'AUDIO_CACHE_ENABLED': False,  # Web版ではキャッシュ無効
        'AUDIO_CACHE_DIR': None,
        
        # パフォーマンス設定
        'TARGET_FPS': 60,
        'ENABLE_VSYNC': True,
        'ENABLE_OPTIMIZATION': True,
        
        # Web固有設定
        'WEB_VERSION': True,
        'ENABLE_FULLSCREEN': False,  # Web版ではフルスクリーン無効
        'ENABLE_RESIZE': True,
    }

def load_web_config() -> Dict[str, Any]:
    """Web環境用の設定を読み込み"""
    config = get_default_config()
    
    if is_web_environment():
        print("🌐 Web環境を検出、Web用設定を適用")
        
        # Web環境固有の設定
        config.update({
            'USE_SYSTEM_FONTS': True,  # システムフォントを優先
            'PRELOAD_ASSETS': True,    # アセットを事前読み込み
            'ASYNC_LOADING': True,     # 非同期読み込み
        })
    else:
        print("🖥️ デスクトップ環境を検出")
        
        # デスクトップ環境では.envファイルを読み込み
        try:
            from dotenv import load_dotenv
            load_dotenv()
            
            # 環境変数から設定を更新
            for key in config:
                env_value = os.environ.get(key)
                if env_value is not None:
                    # 型変換
                    if isinstance(config[key], bool):
                        config[key] = env_value.lower() in ('true', '1', 'yes')
                    elif isinstance(config[key], int):
                        try:
                            config[key] = int(env_value)
                        except ValueError:
                            pass
                    else:
                        config[key] = env_value
        except ImportError:
            print("⚠️ python-dotenvが見つかりません、デフォルト設定を使用")
    
    return config

def get_web_safe_font_path() -> Optional[str]:
    """Web環境で安全なフォントパスを取得"""
    if is_web_environment():
        # Web環境では限定的なフォントのみ使用
        web_fonts = [
            "assets/fonts/NotoSansJP-Regular.ttf",
            "assets/fonts/arial.ttf",
            None  # システムデフォルト
        ]
        
        for font_path in web_fonts:
            if font_path is None:
                return None
            
            if Path(font_path).exists():
                return get_web_safe_path(font_path)
        
        return None
    else:
        # デスクトップ環境では通常のフォント検索
        return None

def log_web_info():
    """Web環境の情報をログ出力"""
    if is_web_environment():
        print("🌐 Web環境情報:")
        print(f"  プラットフォーム: {sys.platform}")
        print(f"  Python バージョン: {sys.version}")
        print(f"  モジュール: {list(sys.modules.keys())[:10]}...")
        
        # ブラウザ情報（可能な場合）
        try:
            import platform
            print(f"  システム: {platform.system()}")
        except:
            pass
    else:
        print("🖥️ デスクトップ環境で実行中")

# Web環境初期化
if is_web_environment():
    print("🌐 Web環境対応モジュール読み込み完了")
    log_web_info()
