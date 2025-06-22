# ファイル配置ルール

## 絶対的なルール

### プロジェクトルートに配置できるファイル
以下のファイル**のみ**をプロジェクトルートに配置できます：
- `main.py` - メインエントリーポイント
- `requirements.txt` - 依存関係
- `requirements-dev.txt` - 開発用依存関係  
- `setup.py` - パッケージ設定
- `pyproject.toml` - プロジェクト設定
- `.env` / `.env.example` - 環境変数
- `.gitignore` - Git設定
- `README.md` - プロジェクト説明
- `DEVELOPMENT_GUIDE.md` - 開発ガイド
- `CLAUDE.md` - Claude Code設定
- `LICENSE` - ライセンス
- `pytest.ini` - pytest設定
- `MANIFEST.in` - パッケージマニフェスト

**上記以外のPythonファイル(.py)をルートに配置することは禁止です。**

### ファイルタイプ別の配置場所

| ファイルタイプ | 配置場所 | 例 |
|--------------|---------|-----|
| ゲームロジック | `src/` | `src/core/game.py` |
| エンティティ | `src/entities/` | `src/entities/player.py` |
| UI コンポーネント | `src/ui/` | `src/ui/menu.py` |
| デモ・サンプル | `examples/` | `examples/demo_game.py` |
| 単体テスト | `tests/unit/` | `tests/unit/test_player.py` |
| 統合テスト | `tests/integration/` | `tests/integration/test_game.py` |
| E2Eテスト | `tests/e2e/` | `tests/e2e/test_gameplay.py` |

### 禁止事項

❌ **以下は禁止です**：
- `run_demo.py` をルートに配置 → `examples/demo.py` に配置
- `test_pygame.py` をルートに配置 → `tests/unit/test_pygame.py` に配置
- `game_window.py` をルートに配置 → `src/core/window.py` に配置
- `simple_test.py` をルートに配置 → `tests/` または `examples/` に配置

### 実行方法の例

```bash
# 正しい実行方法
python main.py
python examples/demo_game.py
python examples/player_demo.py
python -m pytest tests/

# 間違った構成（ルートにデモファイルがある場合）
# python run_demo.py  ← これは禁止
```

## Amazon Q への明確な指示

1. 新しいファイルを作成する際は、必ず上記の配置ルールに従う
2. `run_*.py` や `test_*.py` という名前でも、ルートには配置しない
3. デモを作成する場合は `examples/` ディレクトリを作成して配置
4. テストを作成する場合は `tests/` ディレクトリ内の適切な場所に配置

**例外なくこのルールに従ってください。**