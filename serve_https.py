#!/usr/bin/env python3
"""
HTTPS対応Web版テスト用サーバー
Pygbag Web版のCORS問題を解決するためのHTTPSサーバー
"""

import http.server
import ssl
import socketserver
import webbrowser
import os
import tempfile
import subprocess
from pathlib import Path

def create_self_signed_cert(cert_dir):
    """自己署名証明書を作成"""
    cert_file = cert_dir / "server.crt"
    key_file = cert_dir / "server.key"
    
    if cert_file.exists() and key_file.exists():
        print("✅ 既存の証明書を使用")
        return str(cert_file), str(key_file)
    
    print("🔐 自己署名証明書を作成中...")
    
    # OpenSSLコマンドで証明書作成
    cmd = [
        "openssl", "req", "-x509", "-newkey", "rsa:4096", 
        "-keyout", str(key_file), "-out", str(cert_file),
        "-days", "30", "-nodes", "-subj", 
        "/C=JP/ST=Tokyo/L=Tokyo/O=Test/CN=localhost"
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        print("✅ 自己署名証明書作成完了")
        return str(cert_file), str(key_file)
    except subprocess.CalledProcessError as e:
        print(f"❌ OpenSSL証明書作成失敗: {e}")
        return None, None
    except FileNotFoundError:
        print("❌ OpenSSLが見つかりません")
        print("Homebrewでインストール: brew install openssl")
        return None, None

def serve_https(port=8443, directory="build/web"):
    """HTTPSでWeb版を配信"""
    # ディレクトリ存在チェック
    dist_path = Path(directory)
    if not dist_path.exists():
        print(f"❌ ディレクトリが見つかりません: {directory}")
        return
    
    # index.html存在チェック
    index_path = dist_path / "index.html"
    if not index_path.exists():
        print(f"❌ index.htmlが見つかりません: {index_path}")
        return
    
    # 証明書ディレクトリ
    cert_dir = Path.home() / ".mystery-pet-rescue" / "certs"
    cert_dir.mkdir(parents=True, exist_ok=True)
    
    # 自己署名証明書作成
    cert_file, key_file = create_self_signed_cert(cert_dir)
    if not cert_file or not key_file:
        print("❌ HTTPS証明書の準備に失敗しました")
        print("🔄 代替案: GitHub Pagesに直接デプロイしましょう")
        return False
    
    print("🌐 HTTPS Web版テストサーバー起動")
    print("=" * 50)
    print(f"📁 配信ディレクトリ: {dist_path.absolute()}")
    print(f"🔒 HTTPS URL: https://localhost:{port}")
    print("⚠️  自己署名証明書のため、ブラウザで警告が表示されます")
    print("   → 「詳細設定」→「localhost に進む (安全ではありません)」を選択")
    print("🛑 終了するには Ctrl+C を押してください")
    print("=" * 50)
    
    # 元のディレクトリを保存
    original_dir = os.getcwd()
    
    try:
        # ディレクトリ変更
        os.chdir(dist_path)
        
        # CORS対応のカスタムハンドラー
        class CORSHTTPSRequestHandler(http.server.SimpleHTTPRequestHandler):
            def end_headers(self):
                # Pygbag用の特別なヘッダー
                self.send_header('Cross-Origin-Embedder-Policy', 'require-corp')
                self.send_header('Cross-Origin-Opener-Policy', 'same-origin')
                self.send_header('Cross-Origin-Resource-Policy', 'cross-origin')
                
                # 追加のCORSヘッダー
                self.send_header('Access-Control-Allow-Origin', '*')
                self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
                self.send_header('Access-Control-Allow-Headers', '*')
                
                # キャッシュ制御
                self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
                self.send_header('Pragma', 'no-cache')
                self.send_header('Expires', '0')
                
                super().end_headers()
            
            def log_message(self, format, *args):
                # 重要でないログを抑制
                if not any(x in args[0] for x in ['.wasm', '.js', '.data', 'favicon']):
                    super().log_message(format, *args)
        
        # HTTPSサーバー設定
        with socketserver.TCPServer(("", port), CORSHTTPSRequestHandler) as httpd:
            # SSL設定
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert_file, key_file)
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
            
            print(f"✅ HTTPSサーバー起動完了: https://localhost:{port}")
            
            # ブラウザを自動で開く
            try:
                webbrowser.open(f"https://localhost:{port}")
                print("🌐 ブラウザを開きました")
            except Exception as e:
                print(f"⚠️ ブラウザの自動起動に失敗: {e}")
                print(f"手動でブラウザを開いて https://localhost:{port} にアクセスしてください")
            
            print("\n🎮 Web版ゲームの使用方法:")
            print("  1. ブラウザで証明書警告を承認してください")
            print("  2. ゲームが読み込まれるまでお待ちください")
            print("  3. 読み込み完了後、通常通りゲームをプレイできます")
            print("\n🔧 トラブルシューティング:")
            print("  - 証明書エラー: 「詳細設定」から「続行」を選択")
            print("  - 読み込みエラー: ページを再読み込み (F5)")
            print("  - CORS エラー: HTTPSが必要です")
            
            # サーバー実行
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n🛑 HTTPSサーバーを停止しました")
        return True
    except OSError as e:
        if e.errno == 48:  # Address already in use
            print(f"❌ ポート {port} は既に使用されています")
            print(f"別のポートを試してください: python serve_https.py --port {port + 1}")
        else:
            print(f"❌ HTTPSサーバー起動エラー: {e}")
        return False
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        return False
    finally:
        # 元のディレクトリに戻る
        os.chdir(original_dir)

def deploy_to_github_pages():
    """GitHub Pagesにデプロイ"""
    print("🚀 GitHub Pages デプロイ準備")
    
    # Web版ファイルをdocsディレクトリにコピー
    web_files = Path("build/web")
    docs_dir = Path("docs")
    
    if not web_files.exists():
        print("❌ Web版ファイルが見つかりません")
        return False
    
    # docs ディレクトリの準備
    docs_dir.mkdir(exist_ok=True)
    
    print("📁 ファイルをdocsディレクトリにコピー中...")
    
    # ファイルをコピー
    import shutil
    for file in web_files.glob("*"):
        if file.is_file():
            dest = docs_dir / file.name
            shutil.copy2(file, dest)
            print(f"✅ {file.name} → docs/{file.name}")
    
    print("🎉 GitHub Pages用ファイル準備完了!")
    print("📝 次のステップ:")
    print("  1. git add docs/")
    print("  2. git commit -m 'Add web version to GitHub Pages'")
    print("  3. git push")
    print("  4. GitHub設定でPages機能を有効化")
    
    return True

def main():
    """メイン関数"""
    import argparse
    
    parser = argparse.ArgumentParser(description="HTTPS対応Web版サーバー")
    parser.add_argument("--port", "-p", type=int, default=8443, help="ポート番号 (デフォルト: 8443)")
    parser.add_argument("--directory", "-d", default="build/web", help="配信ディレクトリ (デフォルト: build/web)")
    parser.add_argument("--deploy", action="store_true", help="GitHub Pagesにデプロイ")
    
    args = parser.parse_args()
    
    if args.deploy:
        deploy_to_github_pages()
    else:
        success = serve_https(args.port, args.directory)
        if not success:
            print("\n🔄 HTTPSサーバーが起動できませんでした")
            print("💡 代替案: GitHub Pagesに直接デプロイしましょう")
            deploy_to_github_pages()

if __name__ == "__main__":
    main()