# ミステリー・ペット・レスキュー 🐾

## ゲーム概要
迷子になったペットたちを探し出し、飼い主の元に返すアドベンチャーゲームです。

### 主な特徴
- **探索**: 住宅街を歩き回り、隠れているペットを発見
- **コレクション**: 様々な種類のペットを図鑑に記録
- **ミニゲーム**: ペットとの信頼関係を築くためのゲーム
- **多言語対応**: 日本語・英語に対応

### ゲームの流れ
1. 住宅街を探索してペットを発見
2. ミニゲームでペットとの信頼関係を構築
3. 飼い主を見つけて無事に返す
4. ペット図鑑にコレクション

## 動作環境
- Python 3.8以上
- Pygame 2.0以上
- 画面解像度: 1280x720以上推奨

## インストール・実行方法

### 1. 依存関係のインストール
```bash
pip install -r requirements.txt
```

### 2. デモ実行コマンド

#### 基本確認
```bash
python test_pygame.py
```

#### シンプル版
```bash
python main.py
```

#### 移動デモ
```bash
python run_window_demo.py
```

#### 完全デモ
```bash
python run_demo_game.py
```

## 操作方法
- **SPACE**: ゲーム開始 / シーン切り替え
- **ESC**: ゲーム終了
- **マウス**: 将来的にサポート予定

## 開発者向け

### プロジェクト構造
```
mystery-pet-rescue/
├── main.py              # メインゲームファイル
├── requirements.txt     # 依存関係
├── test_pygame.py      # 動作確認テスト
├── config/             # 設定ファイル
├── src/                # ソースコード
├── assets/             # ゲームアセット
├── data/               # ゲームデータ
├── saves/              # セーブデータ
└── tests/              # テストファイル
```

### 開発環境セットアップ
```bash
# 開発用依存関係のインストール
pip install -r requirements.txt

# テスト実行
python -m pytest tests/

# コード品質チェック
flake8 src/
black src/
```

詳細な開発情報は `DEVELOPMENT_GUIDE.md` を参照してください。

## ライセンス
MIT License
