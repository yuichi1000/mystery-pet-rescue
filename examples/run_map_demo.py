#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
タイルベース2Dマップシステムデモ実行スクリプト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.demos.map_demo import MapDemo

def main():
    """マップデモを実行"""
    try:
        demo = MapDemo()
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
