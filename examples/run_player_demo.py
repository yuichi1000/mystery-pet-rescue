#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
プレイヤーキャラクターデモ実行スクリプト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.demos.player_demo import PlayerDemo

def main():
    """プレイヤーデモを実行"""
    try:
        demo = PlayerDemo()
        demo.initialize()
        demo.run()
    except KeyboardInterrupt:
        print("\nデモ中断")
    except Exception as e:
        print(f"エラー: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'demo' in locals():
            demo.cleanup()

if __name__ == "__main__":
    main()
