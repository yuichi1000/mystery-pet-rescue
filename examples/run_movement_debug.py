#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
移動デバッグテスト実行スクリプト
"""

import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from examples.tests.movement_debug import main

if __name__ == "__main__":
    main()
