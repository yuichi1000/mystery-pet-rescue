#!/usr/bin/env python3
"""
Web版ビルドスクリプト
Pygbagを使用してブラウザ版を生成
"""

import subprocess
import sys
import os
from pathlib import Path

def check_pygbag():
    """Pygbagがインストールされているかチェック"""
    try:
        result = subprocess.run([sys.executable, '-m', 'pygbag', '--version'], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"✅ Pygbag インストール済み")
            return True
        else:
            # バージョンコマンドが失敗してもpygbagがインストールされている可能性
            try:
                import pygbag
                print(f"✅ Pygbag モジュール確認済み")
                return True
            except ImportError:
                return False
    except (FileNotFoundError, subprocess.TimeoutExpired):
        try:
            import pygbag
            print(f"✅ Pygbag モジュール確認済み")
            return True
        except ImportError:
            print("❌ Pygbagがインストールされていません")
            print("インストール方法: pip install pygbag")
            return False

def build_web():
    """Web版をビルド"""
    print("🌐 Web版ビルド開始")
    print("=" * 50)
    
    # Pygbagチェック
    if not check_pygbag():
        return False
    
    # 現在のディレクトリ確認
    current_dir = Path.cwd()
    main_path = current_dir / "main.py"
    
    if not main_path.exists():
        print(f"❌ main.py が見つかりません: {main_path}")
        return False
    
    print(f"📁 ビルド対象: {main_path}")
    
    # 基本的なpygbagコマンド（最小限のオプション）
    build_cmd = [
        sys.executable, '-m', 'pygbag',
        '--width', '1280',
        '--height', '720',
        '--archive',
        'main.py'
    ]
    
    print("🔨 ビルドコマンド実行中...")
    print(f"コマンド: {' '.join(build_cmd)}")
    
    try:
        # ビルド実行
        result = subprocess.run(build_cmd, cwd=current_dir, 
                              capture_output=False, text=True)
        
        if result.returncode == 0:
            print("✅ Web版ビルド完了")
            
            # 出力ディレクトリ確認
            dist_dir = current_dir / "dist"
            if dist_dir.exists():
                print(f"📁 出力ディレクトリ: {dist_dir}")
                
                # 生成されたファイル一覧
                files = list(dist_dir.glob("*"))
                if files:
                    print("📄 生成されたファイル:")
                    for file in files[:10]:  # 最初の10ファイルのみ表示
                        print(f"  - {file.name}")
                    if len(files) > 10:
                        print(f"  ... 他 {len(files) - 10} ファイル")
                
                # index.html確認
                index_path = dist_dir / "index.html"
                if index_path.exists():
                    print("✅ index.html 生成確認")
                    print("🌐 ブラウザでindex.htmlを開いてテストしてください")
                else:
                    print("⚠️ index.htmlが見つかりません")
            else:
                print("⚠️ distディレクトリが見つかりません")
            
            return True
        else:
            print(f"❌ ビルドエラー (終了コード: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ ビルド中にエラーが発生: {e}")
        return False

def build_web_alternative():
    """代替ビルド方法（より基本的なコマンド）"""
    print("🔄 代替ビルド方法を試行中...")
    
    # より基本的なコマンド
    build_cmd = [
        sys.executable, '-m', 'pygbag',
        'main.py'
    ]
    
    print(f"コマンド: {' '.join(build_cmd)}")
    
    try:
        result = subprocess.run(build_cmd, cwd=Path.cwd())
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 代替ビルドもエラー: {e}")
        return False

def install_pygbag():
    """Pygbagをインストール"""
    print("📦 Pygbagをインストール中...")
    try:
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pygbag'], check=True)
        print("✅ Pygbagインストール完了")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Pygbagインストール失敗: {e}")
        return False

def main():
    """メイン関数"""
    print("🎮 ミステリー・ペット・レスキュー Web版ビルダー")
    print("=" * 60)
    
    # 現在のディレクトリ確認
    current_dir = Path.cwd()
    print(f"📁 作業ディレクトリ: {current_dir}")
    
    # main.pyの存在確認
    main_path = current_dir / "main.py"
    if not main_path.exists():
        print("❌ main.py が見つかりません")
        return
    
    # Pygbagチェック・インストール
    if not check_pygbag():
        print("🔧 Pygbagをインストールしますか？ (y/n): ", end="")
        try:
            response = input().lower()
            if response in ['y', 'yes']:
                if not install_pygbag():
                    return
            else:
                print("❌ Pygbagが必要です")
                return
        except (EOFError, KeyboardInterrupt):
            print("\n❌ 中断されました")
            return
    
    # ビルド実行
    success = build_web()
    
    # 基本ビルドが失敗した場合は代替方法を試行
    if not success:
        print("\n🔄 基本ビルドが失敗しました。代替方法を試行します...")
        success = build_web_alternative()
    
    if success:
        print("\n🎉 Web版ビルド成功！")
        print("🌐 次のステップ:")
        print("  1. python serve_web.py でテストサーバーを起動")
        print("  2. ブラウザで http://localhost:8000 を開く")
        print("  3. ゲームをテストしてください")
    else:
        print("\n❌ Web版ビルド失敗")
        print("🔧 トラブルシューティング:")
        print("  1. pygbag --help で利用可能なオプションを確認")
        print("  2. main.py の構文エラーがないか確認")
        print("  3. 必要な依存関係がインストールされているか確認")

if __name__ == "__main__":
    main()
