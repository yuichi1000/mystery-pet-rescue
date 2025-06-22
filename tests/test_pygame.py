#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pygame動作確認テスト

このスクリプトでPygameが正常にインストールされているかテストします。
"""

import sys

def test_pygame_installation():
    """Pygameのインストール状況をテスト"""
    print("Pygame動作確認テスト")
    print("=" * 40)
    
    try:
        import pygame
        print(f"✓ Pygame インストール済み (バージョン: {pygame.version.ver})")
        
        # Pygame初期化テスト
        pygame.init()
        print("✓ Pygame 初期化成功")
        
        # 画面作成テスト
        screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Pygame テスト")
        print("✓ 画面作成成功 (800x600)")
        
        # フォント初期化テスト
        pygame.font.init()
        font = pygame.font.Font(None, 36)
        print("✓ フォント初期化成功")
        
        # 簡単な描画テスト
        screen.fill((0, 0, 0))
        text = font.render("Pygame Test OK!", True, (255, 255, 255))
        screen.blit(text, (300, 280))
        pygame.display.flip()
        print("✓ 描画テスト成功")
        
        print("\n3秒後に自動終了します...")
        pygame.time.wait(3000)
        
        pygame.quit()
        print("✓ Pygame 終了処理成功")
        
        print("\n" + "=" * 40)
        print("✅ 全てのテストが成功しました！")
        print("main.pyを実行してゲームを開始できます。")
        
        return True
        
    except ImportError:
        print("❌ Pygame がインストールされていません")
        print("以下のコマンドでインストールしてください:")
        print("pip install pygame>=2.0.0")
        return False
        
    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        return False


if __name__ == "__main__":
    success = test_pygame_installation()
    sys.exit(0 if success else 1)
