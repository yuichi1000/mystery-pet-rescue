#!/usr/bin/env python3
"""
Web版テスト用簡易サーバー
ローカルでWeb版をテストするためのHTTPサーバー
"""

import http.server
import socketserver
import webbrowser
import os
from pathlib import Path

def serve_web(port=8000, directory="dist"):
    """Web版を配信"""
    # ディレクトリ存在チェック
    dist_path = Path(directory)
    if not dist_path.exists():
        print(f"❌ ディレクトリが見つかりません: {directory}")
        print("先にbuild_web.pyを実行してWeb版をビルドしてください")
        return
    
    # index.html存在チェック
    index_path = dist_path / "index.html"
    if not index_path.exists():
        print(f"❌ index.htmlが見つかりません: {index_path}")
        print("Web版のビルドが完了していない可能性があります")
        return
    
    print("🌐 Web版テストサーバー起動")
    print("=" * 40)
    print(f"📁 配信ディレクトリ: {dist_path.absolute()}")
    print(f"🌐 URL: http://localhost:{port}")
    print("🛑 終了するには Ctrl+C を押してください")
    print("=" * 40)
    
    # ディレクトリ変更
    os.chdir(dist_path)
    
    # HTTPサーバー設定
    handler = http.server.SimpleHTTPRequestHandler
    
    # CORS対応のカスタムハンドラー
    class CORSHTTPRequestHandler(handler):
        def end_headers(self):
            self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
            self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
            super().end_headers()
    
    try:
        with socketserver.TCPServer(("", port), CORSHTTPRequestHandler) as httpd:
            print(f"✅ サーバー起動完了: http://localhost:{port}")
            
            # ブラウザを自動で開く
            try:
                webbrowser.open(f"http://localhost:{port}")
                print("🌐 ブラウザを開きました")
            except Exception as e:
                print(f"⚠️ ブラウザの自動起動に失敗: {e}")
                print(f"手動でブラウザを開いて http://localhost:{port} にアクセスしてください")
            
            # サーバー実行
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 サーバーを停止しました")
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ ポート {port} は既に使用されています")
            print(f"別のポートを試してください: python serve_web.py --port {port + 1}")
        else:
            print(f"❌ サーバー起動エラー: {e}")

def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Web版テスト用サーバー")
    parser.add_argument("--port", "-p", type=int, default=8000, help="ポート番号 (デフォルト: 8000)")
    parser.add_argument("--directory", "-d", default="dist", help="配信ディレクトリ (デフォルト: dist)")
    
    args = parser.parse_args()
    
    serve_web(args.port, args.directory)

if __name__ == "__main__":
    main()
