#!/usr/bin/env python3
"""
ミステリー・ペット・レスキュー
メインエントリーポイント
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# 環境変数の読み込み（オプショナル）
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("ℹ️ python-dotenvが見つかりません（オプショナル）")

# メインゲームのインポートと起動
from src.core.game_main import GameMain

def main():
    """メイン関数"""
    print("🎮 ミステリー・ペット・レスキュー")
    print("=" * 50)
    print("🐾 迷子のペットを探して救出するアドベンチャーゲーム")
    print("🎯 目標: すべてのペットを見つけて飼い主の元に返そう")
    print("=" * 50)
    print()
    
    try:
        # ゲーム起動
        game = GameMain()
        game.run()
        
    except KeyboardInterrupt:
        print("\n⚠️ ユーザーによる中断")
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback
        traceback.print_exc()
    finally:
        print("👋 ゲームを終了します")

if __name__ == "__main__":
    main()
