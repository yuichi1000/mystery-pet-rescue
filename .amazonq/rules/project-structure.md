# プロジェクト構造ガイドライン

## ファイル配置の原則

### プロジェクトルートに配置すべきファイル
- `main.py` - メインエントリーポイントのみ
- `requirements.txt` - 依存関係
- `setup.py` - パッケージ設定（オプション）
- `.env.example` - 環境変数サンプル
- 設定ファイル（`.gitignore`, `pytest.ini` など）
- ドキュメント（`README.md`, `LICENSE` など）

### src/ 内に配置すべきファイル
- **すべてのゲームロジック**
- `game_window.py` → `src/core/window.py` または `src/ui/window.py`
- ゲームコンポーネント
- ユーティリティ関数
- システムモジュール

### デモ・サンプルファイルの配置

**重要**: すべてのファイルは適切なディレクトリに配置してください：

1. **デモ・サンプルファイル**
   - `examples/` ディレクトリに配置
   - 例: `examples/demo_game.py`, `examples/player_demo.py`
   - `run_*.py` 形式のファイルもすべて `examples/` に配置

2. **テストファイル**
   - `tests/` ディレクトリに配置
   - 単体テスト: `tests/unit/test_*.py`
   - 統合テスト: `tests/integration/test_*.py`
   - `test_*.py` 形式のファイルもすべて `tests/` に配置

3. **ルートディレクトリには配置しない**
   - `main.py` 以外の実行ファイルはルートに置かない
   - デモやテストファイルは必ず適切なディレクトリに配置

### tests/ 内に配置すべきファイル
- 単体テスト（`test_*.py`）
- 統合テスト
- E2Eテスト

## main.py の配置について

### プロジェクトルートに配置する理由

1. **Pythonのベストプラクティス**
   - 多くのPythonプロジェクトでは `main.py` をルートに配置
   - 実行が簡単: `python main.py`
   - パッケージ構造が明確になる

2. **インポートパスの簡潔性**
```python
# main.py（プロジェクトルート）
from src.core.game import Game
from src.scenes.menu import MenuScene
from src.utils.config import Config

# もし src/main.py だった場合の問題
# 相対インポートが複雑になる
from .core.game import Game  # または
from core.game import Game   # 実行方法により変わる
```

3. **実行方法の統一**
```bash
# 推奨: プロジェクトルートから実行
python main.py

# 開発時のデバッグ実行
python -m debugpy --listen 5678 main.py

# パッケージとして実行
python -m mystery_pet_rescue
```

## 推奨ディレクトリ構造

```
mystery-pet-rescue/
├── main.py                  # エントリーポイント
├── requirements.txt         # 依存関係
├── requirements-dev.txt     # 開発用依存関係
├── .env.example            # 環境変数の例
├── .gitignore              # Git除外設定
├── README.md               # プロジェクト説明
├── DEVELOPMENT_GUIDE.md    # 開発ガイド
├── pytest.ini              # pytest設定
├── setup.py                # パッケージ設定（オプション）
│
├── src/                    # ソースコード
│   ├── __init__.py        # パッケージ初期化
│   ├── core/              # コアシステム
│   ├── entities/          # ゲームエンティティ
│   ├── systems/           # ゲームシステム
│   ├── scenes/            # ゲームシーン
│   ├── ui/                # UIコンポーネント
│   └── utils/             # ユーティリティ
│
├── examples/               # デモ・サンプルコード
│   ├── __init__.py
│   ├── demo_game.py       # ゲームデモ
│   ├── player_demo.py     # プレイヤー移動デモ
│   ├── window_demo.py     # ウィンドウデモ
│   └── pygame_test.py     # Pygame動作確認
│
├── tests/                  # テストコード
│   ├── __init__.py
│   ├── conftest.py        # pytest共通設定
│   ├── unit/              # 単体テスト
│   ├── integration/       # 統合テスト
│   └── e2e/               # E2Eテスト
│
├── assets/                 # ゲームアセット
│   ├── images/            # 画像ファイル
│   ├── sounds/            # 効果音
│   ├── music/             # BGM
│   ├── fonts/             # フォント
│   └── locales/           # 翻訳ファイル
│
├── data/                   # ゲームデータ
│   ├── levels/            # レベルデータ
│   ├── dialogues/         # 会話データ
│   └── puzzles/           # パズルデータ
│
├── config/                 # 設定ファイル
│   ├── game_config.json   # ゲーム設定
│   ├── audio_config.json  # 音声設定
│   └── graphics_config.json # グラフィック設定
│
├── docs/                   # ドキュメント
│   ├── api/               # API仕様
│   ├── design/            # 設計書
│   └── assets/            # ドキュメント用画像
│
├── scripts/                # ユーティリティスクリプト
│   ├── build.py           # ビルドスクリプト
│   ├── generate_assets.py # アセット生成
│   └── check_translations.py # 翻訳チェック
│
├── cache/                  # キャッシュ（.gitignore対象）
│   └── audio/             # 生成音楽キャッシュ
│
└── .amazonq/               # Amazon Q設定
    ├── mcp.json           # MCP設定
    └── rules/             # プロジェクトルール
```

## main.py の実装例

```python
#!/usr/bin/env python3
"""
ミステリー・ペット・レスキュー
エントリーポイント
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent))

# 環境変数の読み込み
from dotenv import load_dotenv
load_dotenv()

# ゲームのインポートと起動
from src.core.game import Game
from src.utils.config import Config
from src.utils.logger import setup_logger

def main():
    """メイン関数"""
    # ロガーの設定
    logger = setup_logger()
    logger.info("ゲーム起動中...")
    
    try:
        # 設定の読み込み
        config = Config.load()
        
        # ゲームインスタンスの作成と実行
        game = Game(config)
        game.run()
        
    except KeyboardInterrupt:
        logger.info("ユーザーによる中断")
        sys.exit(0)
    except Exception as e:
        logger.error(f"予期しないエラー: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("ゲーム終了")

if __name__ == "__main__":
    main()
```

## パッケージ化する場合

もしPyPIなどに公開する場合は、`setup.py` を作成：

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="mystery-pet-rescue",
    version="1.0.0",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'mystery-pet-rescue=main:main',
        ],
    },
    # 他の設定...
)
```

この場合でも、`main.py` はプロジェクトルートに置くのが一般的です。