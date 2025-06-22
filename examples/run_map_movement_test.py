#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
マップ移動テスト実行スクリプト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# examples/tests/map_movement_test.py を実行
import subprocess

def main():
    """マップ移動テストを実行"""
    test_file = project_root / "examples" / "tests" / "map_movement_test.py"
    try:
        subprocess.run([sys.executable, str(test_file)], check=True)
    except subprocess.CalledProcessError as e:
        print(f"テスト実行エラー: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nテスト中断")

if __name__ == "__main__":
    main()
