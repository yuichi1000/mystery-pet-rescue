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
        result = subprocess.run(['pygbag', '--version'], capture_output=True, text=True)
        print(f"✅ Pygbag バージョン: {result.stdout.strip()}")
        return True
    except FileNotFoundError:
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
    
    # ビルドコマンド
    build_cmd = [
        'pygbag',
        '--width', '1280',
        '--height', '720',
        '--name', 'Mystery Pet Rescue',
        '--icon', 'assets/icons/game_icon.png',
        '--template', 'custom',
        '--archive',
        'main_web.py'
    ]
    
    print("🔨 ビルドコマンド実行中...")
    print(f"コマンド: {' '.join(build_cmd)}")
    
    try:
        # ビルド実行
        result = subprocess.run(build_cmd, cwd=Path.cwd())
        
        if result.returncode == 0:
            print("✅ Web版ビルド完了")
            print("📁 出力ディレクトリ: dist/")
            print("🌐 ブラウザでindex.htmlを開いてテストしてください")
            return True
        else:
            print(f"❌ ビルドエラー (終了コード: {result.returncode})")
            return False
            
    except Exception as e:
        print(f"❌ ビルド中にエラーが発生: {e}")
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
    
    # main_web.pyの存在確認
    main_web_path = current_dir / "main_web.py"
    if not main_web_path.exists():
        print("❌ main_web.py が見つかりません")
        return
    
    # Pygbagチェック・インストール
    if not check_pygbag():
        print("🔧 Pygbagをインストールしますか？ (y/n): ", end="")
        response = input().lower()
        if response in ['y', 'yes']:
            if not install_pygbag():
                return
        else:
            print("❌ Pygbagが必要です")
            return
    
    # ビルド実行
    if build_web():
        print("\n🎉 Web版ビルド成功！")
        print("🌐 ブラウザでゲームを楽しんでください")
    else:
        print("\n❌ Web版ビルド失敗")

if __name__ == "__main__":
    main()
