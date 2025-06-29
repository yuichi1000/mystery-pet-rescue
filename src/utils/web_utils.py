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
    web_indicators = [
        os.environ.get('WEB_VERSION') == '1',
        hasattr(sys, 'platform') and 'emscripten' in sys.platform,
        'pygbag' in sys.modules,
        'pyodide' in sys.modules,
        hasattr(sys, '_emscripten_info')
    ]
    
    is_web = any(web_indicators)
    if is_web:
        print("🌐 Web環境を検出")
    else:
        print("🖥️ デスクトップ環境を検出")
    
    return is_web

def get_web_safe_path(path: str) -> str:
    """Web環境で安全なパスを取得"""
    if is_web_environment():
        # Web環境では相対パスを使用
        safe_path = path.replace('\\', '/')
        print(f"🌐 Web安全パス: {path} → {safe_path}")
        return safe_path
    else:
        # デスクトップ環境では通常のパス
        return str(Path(path))

def get_default_config() -> Dict[str, Any]:
    """Web環境用のデフォルト設定"""
    config = {
        # 音楽・音声設定
        'BEATOVEN_API_KEY': None,  # Web版では無効
        'BEATOVEN_API_URL': None,
        'USE_MOCK_API': True,  # モック音声を使用
        
        # ゲーム設定
        'DEBUG_MODE': True,  # Web版ではデバッグ有効
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
    
    print(f"🔧 デフォルト設定読み込み: {len(config)}項目")
    return config

def load_web_config() -> Dict[str, Any]:
    """Web環境用の設定を読み込み"""
    config = get_default_config()
    
    if is_web_environment():
        print("🌐 Web環境設定を適用")
        
        # Web環境固有の設定
        config.update({
            'USE_SYSTEM_FONTS': True,  # システムフォントを優先
            'PRELOAD_ASSETS': True,    # アセットを事前読み込み
            'ASYNC_LOADING': True,     # 非同期読み込み
            'REDUCED_QUALITY': True,   # 品質を下げてパフォーマンス向上
        })
    else:
        print("🖥️ デスクトップ環境設定を適用")
        
        # デスクトップ環境では.envファイルを読み込み
        try:
            from dotenv import load_dotenv
            load_dotenv()
            print("✅ .env ファイル読み込み完了")
            
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
        print("🌐 Web環境フォント検索")
        # Web環境では限定的なフォントのみ使用
        web_fonts = [
            "assets/fonts/NotoSansJP-VariableFont_wght.ttf",  # 実際のファイル名
            "assets/fonts/NotoSansJP-Regular.ttf",
            "assets/fonts/arial.ttf",
            None  # システムデフォルト
        ]
        
        for font_path in web_fonts:
            if font_path is None:
                print("🌐 システムデフォルトフォント使用")
                return None
            
            if Path(font_path).exists():
                safe_path = get_web_safe_path(font_path)
                print(f"✅ Web用フォント発見: {safe_path}")
                return safe_path
        
        print("⚠️ Web用フォントが見つかりません")
        return None
    else:
        # デスクトップ環境では通常のフォント検索
        print("🖥️ デスクトップ環境フォント検索")
        return None

def check_web_assets() -> Dict[str, bool]:
    """Web環境でのアセット存在確認"""
    assets_status = {}
    
    # 重要なアセットディレクトリ
    asset_dirs = [
        "assets/images",
        "assets/sounds", 
        "assets/music",
        "data",
        "config",
        "locales"
    ]
    
    print("🔍 アセット存在確認:")
    for asset_dir in asset_dirs:
        exists = Path(asset_dir).exists()
        assets_status[asset_dir] = exists
        status = "✅" if exists else "❌"
        print(f"  {status} {asset_dir}")
    
    return assets_status

def log_web_info():
    """Web環境の情報をログ出力"""
    print("🌐 環境情報:")
    print(f"  プラットフォーム: {sys.platform}")
    print(f"  Python バージョン: {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    print(f"  作業ディレクトリ: {os.getcwd()}")
    
    if is_web_environment():
        print("🌐 Web環境詳細:")
        
        # Web環境の詳細情報
        web_info = []
        if os.environ.get('WEB_VERSION'):
            web_info.append("WEB_VERSION フラグ")
        if hasattr(sys, 'platform') and 'emscripten' in sys.platform:
            web_info.append("Emscripten プラットフォーム")
        if 'pygbag' in sys.modules:
            web_info.append("Pygbag モジュール")
        if 'pyodide' in sys.modules:
            web_info.append("Pyodide モジュール")
        
        print(f"  検出された指標: {', '.join(web_info)}")
        
        # モジュール情報
        web_modules = [mod for mod in sys.modules.keys() if any(x in mod.lower() for x in ['web', 'emscripten', 'pygbag', 'pyodide'])]
        if web_modules:
            print(f"  Web関連モジュール: {web_modules[:5]}")
    else:
        print("🖥️ デスクトップ環境で実行中")
    
    # アセット確認
    check_web_assets()

def safe_import(module_name: str, fallback=None):
    """安全なモジュールインポート"""
    try:
        module = __import__(module_name)
        print(f"✅ {module_name} インポート成功")
        return module
    except ImportError as e:
        print(f"⚠️ {module_name} インポート失敗: {e}")
        if fallback is not None:
            print(f"🔄 フォールバック使用: {fallback}")
            return fallback
        return None

# Web環境初期化
if is_web_environment():
    print("🌐 Web環境対応モジュール読み込み完了")
    log_web_info()
else:
    print("🖥️ デスクトップ環境で実行中")
