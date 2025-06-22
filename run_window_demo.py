#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基本ウィンドウデモ実行スクリプト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.core.window import GameWindow

def main():
    """基本ウィンドウデモを実行"""
    try:
        game = GameWindow()
        game.initialize()
        game.run()
    except KeyboardInterrupt:
        print("\nゲーム中断")
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'game' in locals():
            game.cleanup()

if __name__ == "__main__":
    main()
