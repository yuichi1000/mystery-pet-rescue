"""
メニューシステム
階層的なメニュー管理とスムーズな画面遷移
"""

import pygame
from typing import Dict, List, Optional, Callable, Any
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

from src.utils.font_manager import get_font_manager
from src.utils.asset_manager import get_asset_manager
from src.systems.save_load_system import SaveLoadSystem

class MenuState(Enum):
    """メニュー状態"""
    TITLE = "title"
    PAUSE = "pause"
    SAVE_LOAD = "save_load"
    GAME = "game"
    QUIT = "quit"

class TransitionType(Enum):
    """画面遷移タイプ"""
    NONE = "none"
    FADE = "fade"
    SLIDE_LEFT = "slide_left"
    SLIDE_RIGHT = "slide_right"
    SLIDE_UP = "slide_up"
    SLIDE_DOWN = "slide_down"

@dataclass
class MenuButton:
    """メニューボタン"""
    text: str
    action: Callable
    rect: pygame.Rect = None
    enabled: bool = True
    visible: bool = True
    color: tuple = (70, 130, 180)
    hover_color: tuple = (100, 149, 237)
    text_color: tuple = (255, 255, 255)
    font_size: int = 20

@dataclass
class MenuTransition:
    """画面遷移データ"""
    transition_type: TransitionType
    duration: float
    current_time: float = 0.0
    from_state: MenuState = None
    to_state: MenuState = None
    progress: float = 0.0

class MenuSystem:
    """メニューシステム管理クラス"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # フォントマネージャー
        self.font_manager = get_font_manager()
        
        # アセットマネージャー
        self.asset_manager = get_asset_manager()
        
        # セーブ/ロードシステム
        self.save_load_system = SaveLoadSystem()
        
        # 状態管理
        self.current_state = MenuState.TITLE
        self.previous_state = None
        self.state_stack: List[MenuState] = []
        
        # 画面遷移
        self.transition: Optional[MenuTransition] = None
        self.transition_surface = pygame.Surface((self.screen_width, self.screen_height))
        
        # メニューデータ
        self.menus: Dict[MenuState, List[MenuButton]] = {}
        self.backgrounds: Dict[MenuState, pygame.Surface] = {}
        
        # 設定データ
        self.settings = self._load_settings()
        
        # 入力管理
        self.selected_button = 0
        self.mouse_pos = (0, 0)
        self.keys_pressed = set()
        
        # 初期化
        self._setup_menus()
        self._setup_backgrounds()
        
        print("✅ メニューシステム初期化完了")
    
    def _load_settings(self) -> Dict[str, Any]:
        """設定を読み込み"""
        settings_file = "config/game_settings.json"
        default_settings = {
            "master_volume": 0.8,
            "music_volume": 0.7,
            "sfx_volume": 0.8,
            "fullscreen": False,
            "key_bindings": {
                "up": pygame.K_UP,
                "down": pygame.K_DOWN,
                "left": pygame.K_LEFT,
                "right": pygame.K_RIGHT,
                "action": pygame.K_SPACE,
                "cancel": pygame.K_ESCAPE,
                "menu": pygame.K_TAB
            }
        }
        
        try:
            if Path(settings_file).exists():
                with open(settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
                # デフォルト設定とマージ
                for key, value in default_settings.items():
                    if key not in settings:
                        settings[key] = value
                return settings
        except Exception as e:
            print(f"⚠️ 設定読み込みエラー: {e}")
        
        return default_settings
    
    def _save_settings(self):
        """設定を保存"""
        settings_file = "config/game_settings.json"
        try:
            Path(settings_file).parent.mkdir(parents=True, exist_ok=True)
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, ensure_ascii=False, indent=2)
            print("💾 設定保存完了")
        except Exception as e:
            print(f"❌ 設定保存エラー: {e}")
    
    def _setup_menus(self):
        """メニューを設定"""
        # タイトルメニュー
        self.menus[MenuState.TITLE] = [
            MenuButton("ゲーム開始", self._start_game, font_size=24),
            MenuButton("ペット図鑑", self._open_pet_collection, font_size=20),
            MenuButton("セーブ/ロード", self._open_save_load, font_size=20),
            MenuButton("設定", self._open_settings, font_size=20),
            MenuButton("ゲーム終了", self._quit_game, font_size=20)
        ]
        
        # 設定メニュー
        self.menus[MenuState.SETTINGS] = [
            MenuButton("音量設定", self._open_audio_settings, font_size=18),
            MenuButton("キー設定", self._open_key_config, font_size=18),
            MenuButton("画面設定", self._open_display_settings, font_size=18),
            MenuButton("戻る", self._go_back, font_size=18)
        ]
        
        # ポーズメニュー
        self.menus[MenuState.PAUSE] = [
            MenuButton("ゲーム再開", self._resume_game, font_size=20),
            MenuButton("設定", self._open_settings, font_size=18),
            MenuButton("セーブ", self._quick_save, font_size=18),
            MenuButton("タイトルに戻る", self._return_to_title, font_size=18)
        ]
        
        # ペット図鑑メニュー
        self.menus[MenuState.PET_COLLECTION] = [
            MenuButton("図鑑を見る", self._view_collection, font_size=18),
            MenuButton("統計", self._view_stats, font_size=18),
            MenuButton("戻る", self._go_back, font_size=18)
        ]
        
        # セーブ/ロードメニュー
        self.menus[MenuState.SAVE_LOAD] = [
            MenuButton("セーブ", self._save_game, font_size=18),
            MenuButton("ロード", self._load_game, font_size=18),
            MenuButton("戻る", self._go_back, font_size=18)
        ]
        
        # ボタン位置を計算
        self._calculate_button_positions()
    
    def _calculate_button_positions(self):
        """ボタン位置を計算"""
        for state, buttons in self.menus.items():
            if not buttons:
                continue
            
            # メニューの中央配置
            total_height = len(buttons) * 60 + (len(buttons) - 1) * 20
            start_y = (self.screen_height - total_height) // 2
            
            for i, button in enumerate(buttons):
                button_width = 300
                button_height = 50
                button_x = (self.screen_width - button_width) // 2
                button_y = start_y + i * 70
                
                button.rect = pygame.Rect(button_x, button_y, button_width, button_height)
    
    def _setup_backgrounds(self):
        """背景を設定"""
        # 各メニューの背景色
        background_colors = {
            MenuState.SETTINGS: (47, 79, 79),    # ダークスレートグレー
            MenuState.PAUSE: (0, 0, 0, 180),     # 半透明黒
            MenuState.PET_COLLECTION: (34, 139, 34),  # フォレストグリーン
            MenuState.SAVE_LOAD: (72, 61, 139)   # ダークスレートブルー
        }
        
        # タイトル画面の背景画像を読み込み
        title_background = self.asset_manager.load_image(
            "backgrounds/menu_background.png", 
            (self.screen_width, self.screen_height)
        )
        
        if title_background:
            self.backgrounds[MenuState.TITLE] = title_background
            print("✅ タイトル背景画像読み込み完了: menu_background.png")
        else:
            # フォールバック: デフォルト色
            title_surface = pygame.Surface((self.screen_width, self.screen_height))
            title_surface.fill((25, 25, 112))  # ミッドナイトブルー
            self.backgrounds[MenuState.TITLE] = title_surface
            print("⚠️ タイトル背景画像が見つかりません。デフォルト色を使用")
        
        # その他のメニュー背景
        for state, color in background_colors.items():
            surface = pygame.Surface((self.screen_width, self.screen_height))
            if len(color) == 4:  # アルファ値がある場合
                surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
                surface.fill(color)
            else:
                surface.fill(color)
            self.backgrounds[state] = surface
    
    def update(self, time_delta: float, events: List[pygame.event.Event]) -> MenuState:
        """メニュー更新"""
        # 画面遷移中の処理
        if self.transition:
            self._update_transition(time_delta)
            if self.transition.progress >= 1.0:
                self._complete_transition()
        
        # イベント処理
        for event in events:
            result = self._handle_event(event)
            if result:
                return result
        
        return self.current_state
    
    def _handle_event(self, event: pygame.event.Event) -> Optional[MenuState]:
        """イベント処理"""
        if event.type == pygame.MOUSEMOTION:
            self.mouse_pos = event.pos
            self._update_button_hover()
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                return self._handle_button_click()
        
        elif event.type == pygame.KEYDOWN:
            self.keys_pressed.add(event.key)
            return self._handle_keyboard_input(event.key)
        
        elif event.type == pygame.KEYUP:
            self.keys_pressed.discard(event.key)
        
        return None
    
    def _handle_keyboard_input(self, key: int) -> Optional[MenuState]:
        """キーボード入力処理"""
        current_buttons = self.menus.get(self.current_state, [])
        if not current_buttons:
            return None
        
        if key == pygame.K_UP or key == self.settings["key_bindings"]["up"]:
            self.selected_button = (self.selected_button - 1) % len(current_buttons)
        
        elif key == pygame.K_DOWN or key == self.settings["key_bindings"]["down"]:
            self.selected_button = (self.selected_button + 1) % len(current_buttons)
        
        elif key == pygame.K_RETURN or key == self.settings["key_bindings"]["action"]:
            if 0 <= self.selected_button < len(current_buttons):
                button = current_buttons[self.selected_button]
                if button.enabled:
                    return button.action()
        
        elif key == pygame.K_ESCAPE or key == self.settings["key_bindings"]["cancel"]:
            if self.current_state != MenuState.TITLE:
                return self._go_back()
        
        return None
    
    def _update_button_hover(self):
        """ボタンホバー状態を更新"""
        current_buttons = self.menus.get(self.current_state, [])
        for i, button in enumerate(current_buttons):
            if button.rect and button.rect.collidepoint(self.mouse_pos):
                self.selected_button = i
                break
    
    def _handle_button_click(self) -> Optional[MenuState]:
        """ボタンクリック処理"""
        current_buttons = self.menus.get(self.current_state, [])
        for button in current_buttons:
            if button.rect and button.rect.collidepoint(self.mouse_pos) and button.enabled:
                return button.action()
        return None
    
    def _update_transition(self, time_delta: float):
        """画面遷移を更新"""
        if not self.transition:
            return
        
        self.transition.current_time += time_delta
        self.transition.progress = min(1.0, self.transition.current_time / self.transition.duration)
    
    def _complete_transition(self):
        """画面遷移を完了"""
        if self.transition and self.transition.to_state:
            self.current_state = self.transition.to_state
        self.transition = None
    
    def start_transition(self, to_state: MenuState, transition_type: TransitionType = TransitionType.FADE, duration: float = 0.3):
        """画面遷移を開始"""
        self.transition = MenuTransition(
            transition_type=transition_type,
            duration=duration,
            from_state=self.current_state,
            to_state=to_state
        )
    
    def push_state(self, state: MenuState):
        """状態をスタックにプッシュ"""
        self.state_stack.append(self.current_state)
        self.previous_state = self.current_state
        self.current_state = state
    
    def pop_state(self) -> MenuState:
        """状態をスタックからポップ"""
        if self.state_stack:
            self.previous_state = self.current_state
            self.current_state = self.state_stack.pop()
        return self.current_state
    
    # メニューアクション
    def _start_game(self) -> MenuState:
        """ゲーム開始"""
        print("🎮 ゲーム開始")
        self.start_transition(MenuState.GAME, TransitionType.FADE)
        return MenuState.GAME
    
    def _open_settings(self) -> MenuState:
        """設定画面を開く"""
        print("⚙️ 設定画面を開く")
        self.push_state(MenuState.SETTINGS)
        self.start_transition(MenuState.SETTINGS, TransitionType.SLIDE_LEFT)
        return None
    
    def _open_pet_collection(self) -> MenuState:
        """ペット図鑑を開く"""
        print("📖 ペット図鑑を開く")
        self.push_state(MenuState.PET_COLLECTION)
        self.start_transition(MenuState.PET_COLLECTION, TransitionType.SLIDE_UP)
        return None
    
    def _open_save_load(self) -> MenuState:
        """セーブ/ロード画面を開く"""
        print("💾 セーブ/ロード画面を開く")
        self.push_state(MenuState.SAVE_LOAD)
        self.start_transition(MenuState.SAVE_LOAD, TransitionType.SLIDE_DOWN)
        return None
    
    def _quit_game(self) -> MenuState:
        """ゲーム終了"""
        print("👋 ゲーム終了")
        return MenuState.QUIT
    
    def _resume_game(self) -> MenuState:
        """ゲーム再開"""
        print("▶️ ゲーム再開")
        return MenuState.GAME
    
    def _return_to_title(self) -> MenuState:
        """タイトルに戻る"""
        print("🏠 タイトルに戻る")
        self.state_stack.clear()
        self.start_transition(MenuState.TITLE, TransitionType.FADE)
        return None
    
    def _go_back(self) -> MenuState:
        """前の画面に戻る"""
        print("⬅️ 前の画面に戻る")
        if self.state_stack:
            previous = self.state_stack[-1]
            self.pop_state()
            self.start_transition(previous, TransitionType.SLIDE_RIGHT)
        return None
    
    def _quick_save(self) -> MenuState:
        """クイックセーブ"""
        print("⚡ クイックセーブ実行中...")
        
        # 現在のゲームデータを取得（デモ用）
        game_data = self._get_current_game_data()
        
        # クイックセーブ実行
        if self.save_load_system.quick_save(game_data):
            print("✅ クイックセーブ完了")
        else:
            print("❌ クイックセーブ失敗")
            
        return None
    
    def _save_game(self) -> MenuState:
        """ゲームセーブ"""
        print("💾 セーブ画面を表示")
        
        # セーブスロット情報を取得
        save_slots = self.save_load_system.get_save_slots()
        
        print("📋 セーブスロット状況:")
        for i, slot in enumerate(save_slots):
            if slot:
                print(f"  スロット{i}: {slot.save_name} ({slot.save_date})")
            else:
                print(f"  スロット{i}: 空き")
        
        # デモ: 最初の空きスロットにセーブ
        game_data = self._get_current_game_data()
        for i, slot in enumerate(save_slots):
            if slot is None:
                if self.save_load_system.save_game(i, game_data, f"セーブデータ {i+1}"):
                    print(f"✅ スロット{i}にセーブ完了")
                    break
        else:
            print("⚠️ 空きスロットがありません")
            
        return None
    
    def _load_game(self) -> MenuState:
        """ゲームロード"""
        print("📂 ロード画面を表示")
        
        # セーブスロット情報を取得
        save_slots = self.save_load_system.get_save_slots()
        
        print("📋 ロード可能なセーブデータ:")
        available_saves = []
        for i, slot in enumerate(save_slots):
            if slot:
                print(f"  スロット{i}: {slot.save_name}")
                print(f"    日時: {slot.save_date}")
                print(f"    プレイ時間: {slot.play_time:.1f}秒")
                available_saves.append(i)
            else:
                print(f"  スロット{i}: 空き")
        
        # デモ: 最初のセーブデータをロード
        if available_saves:
            slot_id = available_saves[0]
            save_data = self.save_load_system.load_game(slot_id)
            if save_data:
                print(f"✅ {save_data.save_name} をロード完了")
                # ここで実際のゲーム状態を復元（今後実装）
            else:
                print("❌ ロードに失敗しました")
        else:
            print("⚠️ ロード可能なセーブデータがありません")
            
        return None
    
    def _view_collection(self) -> MenuState:
        """図鑑を見る"""
        print("📖 図鑑を表示")
        # ペット図鑑の詳細表示
        collection_data = self.settings.get('pet_collection', {})
        total_pets = 4  # デモでは4匹（犬、猫、うさぎ、鳥）
        found_pets = len([p for p in collection_data.values() if p.get('found', False)])
        print(f"  発見済み: {found_pets}/{total_pets}")
        
        pet_types = ['犬', '猫', 'うさぎ', '鳥']
        for pet_type in pet_types:
            status = "発見済み" if collection_data.get(pet_type, {}).get('found', False) else "未発見"
            print(f"  {pet_type}: {status}")
        return None
    
    def _view_stats(self) -> MenuState:
        """統計を見る"""
        print("📊 統計を表示")
        # ゲーム統計の詳細表示
        stats = self.settings.get('game_stats', {})
        play_time = stats.get('total_play_time', 0)
        pets_rescued = stats.get('pets_rescued', 0)
        areas_explored = stats.get('areas_explored', 0)
        items_collected = stats.get('items_collected', 0)
        
        print(f"  プレイ時間: {play_time//3600}時間{(play_time%3600)//60}分")
        print(f"  救出したペット: {pets_rescued}匹")
        print(f"  探索したエリア: {areas_explored}箇所")
        print(f"  収集したアイテム: {items_collected}個")
        return None
    
    def _open_audio_settings(self) -> MenuState:
        """音量設定"""
        print("🔊 音量設定")
        # 音量設定の詳細表示
        master_volume = self.settings.get('master_volume', 0.8)
        bgm_volume = self.settings.get('bgm_volume', 0.7)
        se_volume = self.settings.get('se_volume', 0.8)
        print(f"  マスター音量: {master_volume:.1%}")
        print(f"  BGM音量: {bgm_volume:.1%}")
        print(f"  効果音音量: {se_volume:.1%}")
        return None
    
    def _open_key_config(self) -> MenuState:
        """キー設定"""
        print("⌨️ キー設定")
        # キー設定の詳細表示
        key_bindings = self.settings.get('key_bindings', {
            'move_up': 'W',
            'move_down': 'S', 
            'move_left': 'A',
            'move_right': 'D',
            'interact': 'SPACE',
            'menu': 'ESC'
        })
        for action, key in key_bindings.items():
            print(f"  {action}: {key}")
        return None
    
    def _open_display_settings(self) -> MenuState:
        """画面設定"""
        print("🖥️ 画面設定")
        # 画面設定の詳細表示
        fullscreen = self.settings.get('fullscreen', False)
        resolution = self.settings.get('resolution', '1280x720')
        vsync = self.settings.get('vsync', True)
        print(f"  フルスクリーン: {'ON' if fullscreen else 'OFF'}")
        print(f"  解像度: {resolution}")
        print(f"  垂直同期: {'ON' if vsync else 'OFF'}")
        return None
    
    def draw(self):
        """メニューを描画"""
        # 背景描画
        if self.current_state in self.backgrounds:
            if self.current_state == MenuState.PAUSE:
                # ポーズメニューは半透明オーバーレイ
                self.screen.blit(self.backgrounds[self.current_state], (0, 0))
            else:
                self.screen.blit(self.backgrounds[self.current_state], (0, 0))
        
        # 画面遷移中の描画
        if self.transition:
            self._draw_transition()
        else:
            self._draw_current_menu()
    
    def _draw_current_menu(self):
        """現在のメニューを描画"""
        # タイトル描画
        self._draw_menu_title()
        
        # ボタン描画
        current_buttons = self.menus.get(self.current_state, [])
        for i, button in enumerate(current_buttons):
            if not button.visible:
                continue
            
            self._draw_button(button, i == self.selected_button)
    
    def _draw_menu_title(self):
        """メニュータイトルを描画"""
        titles = {
            MenuState.TITLE: "ミステリー・ペット・レスキュー",
            MenuState.SETTINGS: "設定",
            MenuState.PAUSE: "ポーズ",
            MenuState.PET_COLLECTION: "ペット図鑑",
            MenuState.SAVE_LOAD: "セーブ/ロード"
        }
        
        title = titles.get(self.current_state, "")
        if title:
            font_size = 48 if self.current_state == MenuState.TITLE else 36
            title_surface = self.font_manager.render_text(title, font_size, (255, 255, 255))
            title_rect = title_surface.get_rect(center=(self.screen_width // 2, 100))
            self.screen.blit(title_surface, title_rect)
    
    def _draw_button(self, button: MenuButton, is_selected: bool):
        """ボタンを描画"""
        if not button.rect:
            return
        
        # ボタン背景
        color = button.hover_color if is_selected else button.color
        if not button.enabled:
            color = tuple(c // 2 for c in color)  # 無効時は暗くする
        
        pygame.draw.rect(self.screen, color, button.rect)
        pygame.draw.rect(self.screen, (255, 255, 255), button.rect, 2)
        
        # ボタンテキスト
        text_color = button.text_color
        if not button.enabled:
            text_color = tuple(c // 2 for c in text_color)
        
        text_surface = self.font_manager.render_text(button.text, button.font_size, text_color)
        text_rect = text_surface.get_rect(center=button.rect.center)
        self.screen.blit(text_surface, text_rect)
    
    def _draw_transition(self):
        """画面遷移を描画"""
        if not self.transition:
            return
        
        progress = self.transition.progress
        
        if self.transition.transition_type == TransitionType.FADE:
            # フェード遷移
            alpha = int(255 * (1 - progress))
            fade_surface = pygame.Surface((self.screen_width, self.screen_height))
            fade_surface.fill((0, 0, 0))
            fade_surface.set_alpha(alpha)
            self._draw_current_menu()
            self.screen.blit(fade_surface, (0, 0))
        
        elif self.transition.transition_type == TransitionType.SLIDE_LEFT:
            # 左スライド遷移
            offset_x = int(self.screen_width * progress)
            self.transition_surface.fill((0, 0, 0))
            # 現在の画面を右にスライド
            self.screen.blit(self.transition_surface, (-offset_x, 0))
            self._draw_current_menu()
        
        # 他の遷移タイプも同様に実装可能
    
    def get_settings(self) -> Dict[str, Any]:
        """設定を取得"""
        return self.settings.copy()
    
    def update_setting(self, key: str, value: Any):
        """設定を更新"""
        self.settings[key] = value
        self._save_settings()
    
    def _get_current_game_data(self) -> Dict[str, Any]:
        """現在のゲームデータを取得（デモ用）"""
        import time
        return {
            'play_time': time.time() % 3600,  # デモ用の適当な時間
            'player_data': {
                'position': {'x': 100, 'y': 100},
                'health': 100,
                'stamina': 100,
                'level': 1
            },
            'game_progress': {
                'current_scene': 'residential',
                'pets_rescued': 0,
                'puzzles_solved': 0
            },
            'pet_collection': {
                'discovered_pets': [],
                'total_pets': 4
            },
            'game_stats': {
                'total_play_time': time.time() % 3600,
                'pets_rescued': 0,
                'areas_explored': 1,
                'items_collected': 0
            }
        }
    
    def cleanup(self):
        """クリーンアップ"""
        self._save_settings()
        print("🧹 メニューシステムクリーンアップ完了")
    
    def resize(self, new_width: int, new_height: int):
        """画面サイズ変更に対応"""
        self.screen_width = new_width
        self.screen_height = new_height
        
        # 背景を再設定（画像のリサイズ対応）
        self._setup_backgrounds()
        
        # ボタン位置を再計算
        self._calculate_button_positions()
        
        print(f"🖥️ メニューシステム解像度変更: {new_width}x{new_height}")
