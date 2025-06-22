#!/usr/bin/env python3
"""
総合デモ（256x256ハイブリッド対応）
全機能を統合したデモアプリケーション
"""

import sys
import pygame
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.systems.sprite_manager import SpriteManager, SpriteSize
from src.systems.minigame_manager import MinigameManager, MinigameType
from src.core.minigame import GameConfig, Difficulty

class DemoMode:
    """デモモード定義"""
    SPRITE_VIEWER = "sprite_viewer"
    MAP_DEMO = "map_demo"
    MINIGAME_DEMO = "minigame_demo"
    INVENTORY_DEMO = "inventory_demo"

def main():
    print("🎮 総合デモ（256x256ハイブリッド対応）起動中...")
    
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    pygame.display.set_caption("総合デモ - 256x256ハイブリッド対応")
    clock = pygame.time.Clock()
    
    # システム初期化
    sprite_manager = SpriteManager()
    minigame_manager = MinigameManager(screen)
    
    # フォント
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)
    
    # 色定義
    colors = {
        'background': (240, 248, 255),
        'text': (50, 50, 50),
        'highlight': (33, 150, 243),
        'panel': (255, 255, 255, 200)
    }
    
    # デモモード
    current_mode = None
    demo_modes = [
        (DemoMode.SPRITE_VIEWER, "🎨 スプライト表示", "256x256画像のハイブリッド表示"),
        (DemoMode.MAP_DEMO, "🗺️ マップデモ", "タイルベースマップ表示"),
        (DemoMode.MINIGAME_DEMO, "🎮 ミニゲーム", "アクション・記憶ゲーム"),
        (DemoMode.INVENTORY_DEMO, "📦 インベントリ", "アイテム管理システム")
    ]
    
    # スプライト表示用設定
    current_size = SpriteSize.MEDIUM
    size_cycle = [SpriteSize.MEDIUM, SpriteSize.LARGE, SpriteSize.ORIGINAL]
    
    print("✅ 総合デモ初期化完了")
    print("🎯 利用可能なデモ:")
    for mode_id, name, desc in demo_modes:
        print(f"  {name}: {desc}")
    
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if current_mode:
                        current_mode = None  # メインメニューに戻る
                        minigame_manager.stop_current_game()
                    else:
                        running = False
                elif event.key == pygame.K_1:
                    current_mode = DemoMode.SPRITE_VIEWER
                elif event.key == pygame.K_2:
                    current_mode = DemoMode.MAP_DEMO
                elif event.key == pygame.K_3:
                    current_mode = DemoMode.MINIGAME_DEMO
                elif event.key == pygame.K_4:
                    current_mode = DemoMode.INVENTORY_DEMO
                elif event.key == pygame.K_TAB and current_mode == DemoMode.SPRITE_VIEWER:
                    # スプライトサイズ切り替え
                    current_index = size_cycle.index(current_size)
                    current_size = size_cycle[(current_index + 1) % len(size_cycle)]
                    print(f"🔄 スプライトサイズ: {current_size.value}")
            
            # ミニゲームのイベント処理
            if current_mode == DemoMode.MINIGAME_DEMO:
                minigame_manager.handle_event(event)
        
        # 背景
        screen.fill(colors['background'])
        
        if current_mode is None:
            # メインメニュー表示
            draw_main_menu(screen, demo_modes, colors, font_large, font_medium, font_small)
        
        elif current_mode == DemoMode.SPRITE_VIEWER:
            # スプライト表示デモ
            draw_sprite_viewer(screen, sprite_manager, current_size, size_cycle, colors, font_medium, font_small)
        
        elif current_mode == DemoMode.MAP_DEMO:
            # マップデモ（簡易版）
            draw_map_demo(screen, sprite_manager, colors, font_medium, font_small)
        
        elif current_mode == DemoMode.MINIGAME_DEMO:
            # ミニゲームデモ
            draw_minigame_demo(screen, minigame_manager, colors, font_medium, font_small)
        
        elif current_mode == DemoMode.INVENTORY_DEMO:
            # インベントリデモ（プレースホルダー）
            draw_inventory_demo(screen, colors, font_medium, font_small)
        
        pygame.display.flip()
        clock.tick(60)
        
        # ミニゲーム更新
        if current_mode == DemoMode.MINIGAME_DEMO:
            minigame_manager.update(1/60)
    
    print("🎉 総合デモ終了")
    pygame.quit()

def draw_main_menu(screen, demo_modes, colors, font_large, font_medium, font_small):
    """メインメニュー描画"""
    # タイトル
    title_text = font_large.render("総合デモ - 256x256ハイブリッド対応", True, colors['text'])
    title_rect = title_text.get_rect(center=(screen.get_width() // 2, 100))
    screen.blit(title_text, title_rect)
    
    # デモ選択
    y_offset = 200
    for i, (mode_id, name, desc) in enumerate(demo_modes):
        # ボタン背景
        button_rect = pygame.Rect(screen.get_width() // 2 - 300, y_offset - 10, 600, 80)
        button_surface = pygame.Surface((button_rect.width, button_rect.height), pygame.SRCALPHA)
        button_surface.fill(colors['panel'])
        screen.blit(button_surface, button_rect)
        pygame.draw.rect(screen, colors['highlight'], button_rect, 3)
        
        # ボタンテキスト
        key_text = font_medium.render(f"{i+1}. {name}", True, colors['text'])
        desc_text = font_small.render(desc, True, colors['text'])
        
        screen.blit(key_text, (button_rect.x + 20, button_rect.y + 15))
        screen.blit(desc_text, (button_rect.x + 20, button_rect.y + 45))
        
        y_offset += 100
    
    # 操作説明
    help_texts = [
        "1-4: デモ選択",
        "ESC: 終了"
    ]
    
    y_pos = screen.get_height() - 80
    for text in help_texts:
        help_surface = font_small.render(text, True, colors['text'])
        screen.blit(help_surface, (50, y_pos))
        y_pos += 25

def draw_sprite_viewer(screen, sprite_manager, current_size, size_cycle, colors, font_medium, font_small):
    """スプライト表示デモ"""
    # タイトル
    title_text = font_medium.render("🎨 スプライト表示（256x256ハイブリッド）", True, colors['text'])
    screen.blit(title_text, (20, 20))
    
    # 現在のサイズ表示
    size_info = f"現在のサイズ: {current_size.value} ({sprite_manager.size_mapping[current_size][0]}x{sprite_manager.size_mapping[current_size][1]})"
    size_text = font_small.render(size_info, True, colors['text'])
    screen.blit(size_text, (20, 60))
    
    # タイルスプライト読み込み・表示
    sprite_manager.load_tile_sprites()
    
    tile_types = ["grass", "ground", "stone_wall", "water", "tree", "rock", "concrete"]
    x_pos = 50
    y_pos = 120
    
    for tile_type in tile_types:
        tile_sprite = sprite_manager.get_tile_sprite(tile_type, current_size)
        if tile_sprite:
            # 背景
            bg_rect = pygame.Rect(x_pos - 10, y_pos - 10, 
                                tile_sprite.get_width() + 20, 
                                tile_sprite.get_height() + 50)
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill(colors['panel'])
            screen.blit(bg_surface, bg_rect)
            
            # スプライト
            screen.blit(tile_sprite, (x_pos, y_pos))
            
            # 名前
            name_text = font_small.render(tile_type, True, colors['text'])
            name_rect = name_text.get_rect(center=(x_pos + tile_sprite.get_width()//2, 
                                                 y_pos + tile_sprite.get_height() + 20))
            screen.blit(name_text, name_rect)
            
            x_pos += tile_sprite.get_width() + 30
            if x_pos > screen.get_width() - 200:
                x_pos = 50
                y_pos += tile_sprite.get_height() + 80
    
    # 操作説明
    help_texts = [
        "TAB: サイズ切り替え",
        "ESC: メニューに戻る"
    ]
    
    y_pos = screen.get_height() - 60
    for text in help_texts:
        help_surface = font_small.render(text, True, colors['text'])
        screen.blit(help_surface, (20, y_pos))
        y_pos += 25

def draw_map_demo(screen, sprite_manager, colors, font_medium, font_small):
    """マップデモ（簡易版）"""
    title_text = font_medium.render("🗺️ マップデモ", True, colors['text'])
    screen.blit(title_text, (20, 20))
    
    info_text = font_small.render("詳細なマップデモは game_map_demo.py を実行してください", True, colors['text'])
    screen.blit(info_text, (20, 60))
    
    # 簡単なマップ表示
    sprite_manager.load_tile_sprites()
    
    simple_map = [
        ["grass", "grass", "tree", "grass"],
        ["ground", "stone_wall", "water", "water"],
        ["concrete", "rock", "grass", "grass"]
    ]
    
    x_start = 100
    y_start = 120
    
    for row_idx, row in enumerate(simple_map):
        for col_idx, tile_type in enumerate(row):
            tile_sprite = sprite_manager.get_tile_sprite(tile_type, SpriteSize.MEDIUM)
            if tile_sprite:
                x = x_start + col_idx * (tile_sprite.get_width() + 5)
                y = y_start + row_idx * (tile_sprite.get_height() + 5)
                screen.blit(tile_sprite, (x, y))
    
    help_text = font_small.render("ESC: メニューに戻る", True, colors['text'])
    screen.blit(help_text, (20, screen.get_height() - 40))

def draw_minigame_demo(screen, minigame_manager, colors, font_medium, font_small):
    """ミニゲームデモ"""
    if minigame_manager.current_game:
        # ミニゲーム実行中
        minigame_manager.draw(screen)
    else:
        # ミニゲーム選択画面
        title_text = font_medium.render("🎮 ミニゲーム選択", True, colors['text'])
        screen.blit(title_text, (20, 20))
        
        games = [
            ("1: アクションゲーム", "障害物を避けてペットに近づく"),
            ("2: 記憶ゲーム", "ペットカードの神経衰弱")
        ]
        
        y_pos = 80
        for game_name, game_desc in games:
            name_text = font_small.render(game_name, True, colors['text'])
            desc_text = font_small.render(game_desc, True, colors['text'])
            screen.blit(name_text, (50, y_pos))
            screen.blit(desc_text, (50, y_pos + 25))
            y_pos += 60
        
        help_texts = [
            "1/2: ゲーム選択",
            "ESC: メニューに戻る"
        ]
        
        y_pos = screen.get_height() - 80
        for text in help_texts:
            help_surface = font_small.render(text, True, colors['text'])
            screen.blit(help_surface, (20, y_pos))
            y_pos += 25

def draw_inventory_demo(screen, colors, font_medium, font_small):
    """インベントリデモ（プレースホルダー）"""
    title_text = font_medium.render("📦 インベントリデモ", True, colors['text'])
    screen.blit(title_text, (20, 20))
    
    info_text = font_small.render("詳細なインベントリデモは inventory_demo.py を実行してください", True, colors['text'])
    screen.blit(info_text, (20, 60))
    
    help_text = font_small.render("ESC: メニューに戻る", True, colors['text'])
    screen.blit(help_text, (20, screen.get_height() - 40))

if __name__ == "__main__":
    main()
