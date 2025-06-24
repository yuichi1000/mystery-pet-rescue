#!/usr/bin/env python3
"""
ゲーム用音声生成スクリプト
Beatoven.ai APIを使用してBGMと効果音を生成
"""

import sys
import argparse
import logging
from pathlib import Path

# プロジェクトルートをパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.utils.audio_generator import get_audio_generator

# ログ設定
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def generate_all_audio():
    """全ての音声を生成"""
    print("🎵 ゲーム用音声生成を開始します...")
    
    generator = get_audio_generator()
    
    if generator.is_using_mock():
        print("🔧 モックAPIを使用します（テスト用無音ファイルを生成）")
    else:
        print("🌐 実際のBeatoven.ai APIを使用します")
    
    # 全音声生成
    results = generator.generate_game_audio_set()
    
    # 結果表示
    print("\n📊 生成結果:")
    success_count = 0
    for name, success in results.items():
        status = "✅" if success else "❌"
        print(f"   {status} {name}")
        if success:
            success_count += 1
    
    print(f"\n🎯 成功: {success_count}/{len(results)}")
    
    # キャッシュ情報
    cache_info = generator.get_cache_info()
    if cache_info['cache_count'] > 0:
        print(f"💾 キャッシュ: {cache_info['cache_count']}ファイル, {cache_info['total_size_mb']:.1f}MB")
    
    return success_count == len(results)

def generate_single_bgm(scene_type: str, mood: str, duration: int = 60):
    """単一のBGMを生成"""
    print(f"🎵 BGM生成: {scene_type} ({mood}, {duration}秒)")
    
    generator = get_audio_generator()
    audio_data = generator.generate_bgm(scene_type, mood, duration)
    
    if audio_data:
        filename = f"{scene_type}_{mood}_bgm.mp3"
        output_path = Path("assets/music") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(audio_data)
        
        print(f"✅ 保存完了: {output_path}")
        return True
    else:
        print("❌ 生成失敗")
        return False

def generate_single_sfx(effect_type: str, intensity: str = "medium", duration: float = 2.0):
    """単一の効果音を生成"""
    print(f"🔊 効果音生成: {effect_type} ({intensity}, {duration}秒)")
    
    generator = get_audio_generator()
    audio_data = generator.generate_sfx(effect_type, intensity, duration)
    
    if audio_data:
        filename = f"{effect_type}.wav"
        output_path = Path("assets/sounds") / filename
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'wb') as f:
            f.write(audio_data)
        
        print(f"✅ 保存完了: {output_path}")
        return True
    else:
        print("❌ 生成失敗")
        return False

def clear_cache():
    """キャッシュをクリア"""
    print("🗑️ キャッシュをクリアします...")
    generator = get_audio_generator()
    generator.clear_cache()
    print("✅ キャッシュクリア完了")

def show_cache_info():
    """キャッシュ情報を表示"""
    generator = get_audio_generator()
    cache_info = generator.get_cache_info()
    
    print("💾 キャッシュ情報:")
    print(f"   ファイル数: {cache_info['cache_count']}")
    print(f"   合計サイズ: {cache_info['total_size_mb']:.1f}MB")
    print(f"   ディレクトリ: {cache_info['cache_dir']}")
    
    if generator.is_using_mock():
        print("   ⚠️ モックAPIを使用中")

def show_setup_guide():
    """セットアップガイドを表示"""
    print("🔧 Beatoven.ai API セットアップガイド")
    print()
    print("1. Beatoven.ai にアカウント登録")
    print("   https://beatoven.ai/")
    print()
    print("2. APIキーを取得")
    print("   ダッシュボード → API Settings → Generate API Key")
    print()
    print("3. .env ファイルを作成")
    print("   プロジェクトルートに .env ファイルを作成し、以下を追加:")
    print("   BEATOVEN_API_KEY=your_api_key_here")
    print("   USE_MOCK_API=False")
    print()
    print("4. 音声生成を実行")
    print("   python scripts/generate_audio.py all")
    print()
    print("💡 テスト用にモックAPIを使用する場合:")
    print("   USE_MOCK_API=True に設定してください")

def main():
    parser = argparse.ArgumentParser(description="ゲーム用音声生成ツール")
    subparsers = parser.add_subparsers(dest='command', help='利用可能なコマンド')
    
    # 全生成コマンド
    subparsers.add_parser('all', help='全ての音声を生成')
    
    # BGM生成コマンド
    bgm_parser = subparsers.add_parser('bgm', help='BGMを生成')
    bgm_parser.add_argument('scene_type', help='シーンタイプ (menu, residential, forest, puzzle, victory, game_over)')
    bgm_parser.add_argument('mood', help='ムード (calm, peaceful, mysterious, focused, triumphant, dramatic)')
    bgm_parser.add_argument('--duration', type=int, default=60, help='長さ（秒）')
    
    # 効果音生成コマンド
    sfx_parser = subparsers.add_parser('sfx', help='効果音を生成')
    sfx_parser.add_argument('effect_type', help='効果音タイプ (pet_found, pet_rescued, button_click, footstep, notification, error, puzzle_solve)')
    sfx_parser.add_argument('--intensity', default='medium', choices=['soft', 'medium', 'strong'], help='強度')
    sfx_parser.add_argument('--duration', type=float, default=2.0, help='長さ（秒）')
    
    # キャッシュ管理コマンド
    subparsers.add_parser('clear-cache', help='キャッシュをクリア')
    subparsers.add_parser('cache-info', help='キャッシュ情報を表示')
    
    # セットアップガイド
    subparsers.add_parser('setup', help='セットアップガイドを表示')
    
    args = parser.parse_args()
    
    if args.command == 'all':
        success = generate_all_audio()
        sys.exit(0 if success else 1)
    
    elif args.command == 'bgm':
        success = generate_single_bgm(args.scene_type, args.mood, args.duration)
        sys.exit(0 if success else 1)
    
    elif args.command == 'sfx':
        success = generate_single_sfx(args.effect_type, args.intensity, args.duration)
        sys.exit(0 if success else 1)
    
    elif args.command == 'clear-cache':
        clear_cache()
    
    elif args.command == 'cache-info':
        show_cache_info()
    
    elif args.command == 'setup':
        show_setup_guide()
    
    else:
        parser.print_help()
        print()
        print("💡 初回セットアップの場合:")
        print("   python scripts/generate_audio.py setup")

if __name__ == "__main__":
    main()
