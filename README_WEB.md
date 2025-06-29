# ミステリー・ペット・レスキュー Web版

ブラウザで遊べるWeb版の作成・実行方法

## 🌐 Web版の特徴

- **ブラウザで実行**: インストール不要でブラウザから直接プレイ
- **軽量化**: Web環境に最適化されたパフォーマンス
- **クロスプラットフォーム**: Windows、Mac、Linux、モバイルで動作
- **非同期処理**: スムーズなゲーム体験

## 📋 必要な環境

- **Python**: 3.8以上
- **Pygbag**: Web版ビルドツール
- **モダンブラウザ**: Chrome、Firefox、Safari、Edge

## 🚀 Web版の作成手順

### 1. Pygbagのインストール

```bash
pip install pygbag
```

### 2. Web版のビルド

```bash
# 自動ビルドスクリプト使用（推奨）
python build_web.py

# または手動でPygbag実行
python -m pygbag --width 1280 --height 720 --archive main_web.py
```

### 3. Web版のテスト

```bash
# テスト用サーバー起動
python serve_web.py

# ブラウザで http://localhost:8000 を開く
```

## 📁 ファイル構成

### Web版専用ファイル
- `main_web.py` - Web版エントリーポイント
- `build_web.py` - ビルドスクリプト
- `serve_web.py` - テスト用サーバー
- `pygbag.toml` - Pygbag設定
- `requirements_web.txt` - Web版依存関係

### 修正されたファイル
- `src/core/game_main.py` - 非同期対応
- `src/utils/web_utils.py` - Web環境対応
- `src/utils/font_manager.py` - Web用フォント
- `src/systems/audio_system.py` - Web用音声

### 生成されるファイル
- `build/web/index.html` - Web版メインファイル
- `build/web/mystery-pet-rescue.apk` - ゲームデータ
- `build/web/favicon.png` - アイコン

## 🎮 Web版の操作方法

デスクトップ版と同じ操作方法：
- **WASD/矢印キー**: プレイヤー移動
- **E**: ペット救出
- **ESC**: メニューに戻る
- **P**: ゲーム一時停止

## 🔧 Web版の制限事項

### 機能制限
- **API呼び出し**: 外部API（Beatoven.ai）は使用不可
- **ファイル保存**: ローカルファイルへの保存制限
- **フルスクリーン**: ブラウザ制限により無効

### パフォーマンス制限
- **音質**: 軽量化のため音質を調整
- **フレームレート**: ブラウザ性能に依存
- **メモリ使用量**: ブラウザのメモリ制限

## 🌐 デプロイ方法

### GitHub Pagesでの公開

1. **ビルド後のファイルをコピー**
```bash
# build/web/ の内容をdocs/に配置
cp -r build/web/* docs/
```

2. **GitHub Pages有効化**
- リポジトリ設定 → Pages → Source: docs folder

### 他のホスティングサービス

- **Netlify**: build/webディレクトリをドラッグ&ドロップ
- **Vercel**: GitHubリポジトリを連携
- **Firebase Hosting**: firebase deployコマンド

## 🐛 トラブルシューティング

### よくある問題

**1. ビルドエラー**
```bash
# Pygbagの再インストール
pip uninstall pygbag
pip install pygbag

# 依存関係の確認
pip install -r requirements_web.txt
```

**2. 音声が再生されない**
- ブラウザの自動再生ポリシーが原因
- ユーザー操作後に音声が有効になります

**3. フォントが表示されない**
- Web版ではシステムフォントを使用
- 日本語表示に問題がある場合はブラウザ設定を確認

**4. 読み込みが遅い**
- アセットファイルのサイズを確認
- ネットワーク接続を確認

**5. "Cross-Origin" エラー**
- serve_web.pyを使用してローカルサーバーから実行
- ファイルを直接開かず、HTTPサーバー経由でアクセス

### デバッグ方法

**ブラウザ開発者ツール**
```javascript
// コンソールでエラー確認
console.log("ゲーム状態確認");

// パフォーマンス監視
performance.mark("game-start");
```

## 📊 パフォーマンス最適化

### 推奨設定
- **画面解像度**: 1280x720（デフォルト）
- **フレームレート**: 60fps
- **音声品質**: 22kHz（Web最適化）

### 最適化のヒント
- 大きな画像ファイルは事前に圧縮
- 不要なアセットは除外
- ブラウザキャッシュを活用

## 🎯 ビルド成功の確認

ビルドが成功すると以下のファイルが生成されます：

```
build/web/
├── index.html              # メインHTMLファイル
├── mystery-pet-rescue.apk  # ゲームデータ（約10MB）
└── favicon.png             # アイコン
```

## 🚀 クイックスタート

```bash
# 1. Pygbagインストール
pip install pygbag

# 2. ビルド実行
python build_web.py

# 3. サーバー起動
python serve_web.py

# 4. ブラウザで http://localhost:8000 を開く
```

---

Web版で楽しいペット救出ゲームをお楽しみください！🐾🌐
