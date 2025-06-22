"""
セーブ/ロードメニュー
ゲームデータの保存と読み込み
"""

import pygame
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import datetime

from src.utils.font_manager import get_font_manager

@dataclass
class SaveSlot:
    """セーブスロット"""
    slot_id: int
    save_name: str
    save_date: str
    play_time: str
    progress: str
    screenshot_path: str = ""
    is_empty: bool = True

class SaveLoadMenu:
    """セーブ/ロードメニュークラス"""
    
    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.screen_width = screen.get_width()
        self.screen_height = screen.get_height()
        
        # フォントマネージャー
        self.font_manager = get_font_manager()
        
        # UI状態
        self.mode = "save"  # "save" or "load"
        self.selected_slot = 0
        self.max_slots = 6
        self.is_confirming = False
        self.confirm_action = None
        
        # 色設定
        self.colors = {
            'background': (72, 61, 139),
            'panel': (100, 100, 150),
            'selected': (150, 150, 200),
            'text': (255, 255, 255),
            'empty_slot': (80, 80, 80),
            'save_button': (34, 139, 34),
            'load_button': (70, 130, 180),
            'delete_button': (220, 20, 60)
        }
        
        # セーブスロットを初期化
        self.save_slots = self._load_save_slots()
        
        print("💾 セーブ/ロードメニュー初期化完了")
    
    def _load_save_slots(self) -> List[SaveSlot]:
        """セーブスロットを読み込み"""
        slots = []
        saves_dir = Path("saves")
        
        for i in range(self.max_slots):
            slot = SaveSlot(
                slot_id=i,
                save_name=f"セーブデータ {i + 1}",
                save_date="",
                play_time="",
                progress="",
                is_empty=True
            )
            
            save_file = saves_dir / f"save_slot_{i}.json"
            if save_file.exists():
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        save_data = json.load(f)
                    
                    slot.save_name = save_data.get('save_name', f'セーブデータ {i + 1}')
                    slot.save_date = save_data.get('save_date', '')
                    slot.play_time = save_data.get('play_time', '00:00:00')
                    slot.progress = save_data.get('progress', '0%')
                    slot.screenshot_path = save_data.get('screenshot_path', '')
                    slot.is_empty = False
                    
                except Exception as e:
                    print(f"⚠️ セーブスロット{i}読み込みエラー: {e}")
            
            slots.append(slot)
        
        return slots
    
    def update(self, events: List[pygame.event.Event]) -> Optional[str]:
        """セーブ/ロードメニューを更新"""
        for event in events:
            if event.type == pygame.KEYDOWN:
                result = self._handle_keyboard_input(event.key)
                if result:
                    return result
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # 左クリック
                    self._handle_mouse_click(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_hover(event.pos)
        
        return None
    
    def _handle_keyboard_input(self, key: int) -> Optional[str]:
        """キーボード入力処理"""
        if self.is_confirming:
            return self._handle_confirm_input(key)
        
        if key == pygame.K_ESCAPE:
            return "back"
        
        elif key == pygame.K_TAB:
            self.mode = "load" if self.mode == "save" else "save"
            print(f"🔄 モード切り替え: {self.mode}")
        
        elif key == pygame.K_UP:
            self.selected_slot = (self.selected_slot - 1) % self.max_slots
        
        elif key == pygame.K_DOWN:
            self.selected_slot = (self.selected_slot + 1) % self.max_slots
        
        elif key == pygame.K_RETURN:
            self._activate_slot()
        
        elif key == pygame.K_DELETE:
            if not self.save_slots[self.selected_slot].is_empty:
                self._confirm_delete()
        
        return None
    
    def _handle_confirm_input(self, key: int) -> Optional[str]:
        """確認ダイアログの入力処理"""
        if key == pygame.K_y:
            result = self._execute_confirm_action()
            self.is_confirming = False
            self.confirm_action = None
            return result
        
        elif key == pygame.K_n or key == pygame.K_ESCAPE:
            self.is_confirming = False
            self.confirm_action = None
        
        return None
    
    def _handle_mouse_click(self, pos):
        """マウスクリック処理"""
        if self.is_confirming:
            # 確認ダイアログのボタンクリック処理
            confirm_buttons = self._get_confirm_button_rects()
            if confirm_buttons['yes'].collidepoint(pos):
                result = self._execute_confirm_action()
                self.is_confirming = False
                self.confirm_action = None
                return result
            elif confirm_buttons['no'].collidepoint(pos):
                self.is_confirming = False
                self.confirm_action = None
            return
        
        # モード切り替えボタン
        mode_buttons = self._get_mode_button_rects()
        if mode_buttons['save'].collidepoint(pos):
            self.mode = "save"
        elif mode_buttons['load'].collidepoint(pos):
            self.mode = "load"
        
        # スロットクリック
        slot_rects = self._get_slot_rects()
        for i, rect in enumerate(slot_rects):
            if rect.collidepoint(pos):
                self.selected_slot = i
                self._activate_slot()
                break
        
        # アクションボタン
        action_buttons = self._get_action_button_rects()
        if action_buttons['delete'].collidepoint(pos) and not self.save_slots[self.selected_slot].is_empty:
            self._confirm_delete()
    
    def _handle_mouse_hover(self, pos):
        """マウスホバー処理"""
        if self.is_confirming:
            return
        
        slot_rects = self._get_slot_rects()
        for i, rect in enumerate(slot_rects):
            if rect.collidepoint(pos):
                self.selected_slot = i
                break
    
    def _activate_slot(self):
        """スロットを有効化"""
        slot = self.save_slots[self.selected_slot]
        
        if self.mode == "save":
            self._confirm_save()
        elif self.mode == "load":
            if not slot.is_empty:
                self._confirm_load()
            else:
                print("⚠️ 空のスロットです")
    
    def _confirm_save(self):
        """セーブ確認"""
        slot = self.save_slots[self.selected_slot]
        if slot.is_empty:
            self.confirm_action = "save"
            self.is_confirming = True
        else:
            self.confirm_action = "overwrite"
            self.is_confirming = True
    
    def _confirm_load(self):
        """ロード確認"""
        self.confirm_action = "load"
        self.is_confirming = True
    
    def _confirm_delete(self):
        """削除確認"""
        self.confirm_action = "delete"
        self.is_confirming = True
    
    def _execute_confirm_action(self) -> Optional[str]:
        """確認アクションを実行"""
        if self.confirm_action == "save" or self.confirm_action == "overwrite":
            return self._save_game()
        elif self.confirm_action == "load":
            return self._load_game()
        elif self.confirm_action == "delete":
            self._delete_save()
        
        return None
    
    def _save_game(self) -> Optional[str]:
        """ゲームをセーブ"""
        slot_id = self.selected_slot
        save_data = self._create_save_data()
        
        try:
            saves_dir = Path("saves")
            saves_dir.mkdir(exist_ok=True)
            
            save_file = saves_dir / f"save_slot_{slot_id}.json"
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            # スロット情報を更新
            slot = self.save_slots[slot_id]
            slot.save_name = save_data['save_name']
            slot.save_date = save_data['save_date']
            slot.play_time = save_data['play_time']
            slot.progress = save_data['progress']
            slot.is_empty = False
            
            print(f"💾 ゲームセーブ完了: スロット{slot_id + 1}")
            return "save_complete"
            
        except Exception as e:
            print(f"❌ セーブエラー: {e}")
            return None
    
    def _load_game(self) -> Optional[str]:
        """ゲームをロード"""
        slot_id = self.selected_slot
        
        try:
            save_file = Path("saves") / f"save_slot_{slot_id}.json"
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            print(f"📂 ゲームロード完了: スロット{slot_id + 1}")
            return "load_complete"
            
        except Exception as e:
            print(f"❌ ロードエラー: {e}")
            return None
    
    def _delete_save(self):
        """セーブデータを削除"""
        slot_id = self.selected_slot
        
        try:
            save_file = Path("saves") / f"save_slot_{slot_id}.json"
            if save_file.exists():
                save_file.unlink()
            
            # スロット情報をリセット
            slot = self.save_slots[slot_id]
            slot.save_name = f"セーブデータ {slot_id + 1}"
            slot.save_date = ""
            slot.play_time = ""
            slot.progress = ""
            slot.is_empty = True
            
            print(f"🗑️ セーブデータ削除完了: スロット{slot_id + 1}")
            
        except Exception as e:
            print(f"❌ 削除エラー: {e}")
    
    def _create_save_data(self) -> Dict[str, Any]:
        """セーブデータを作成"""
        now = datetime.datetime.now()
        
        # TODO: 実際のゲームデータを取得
        save_data = {
            'save_name': f'セーブデータ {self.selected_slot + 1}',
            'save_date': now.strftime('%Y-%m-%d %H:%M:%S'),
            'play_time': '01:23:45',  # 実際のプレイ時間
            'progress': '45%',        # 実際の進行度
            'player_data': {
                'name': 'プレイヤー',
                'level': 5,
                'location': '住宅街'
            },
            'game_state': {
                'current_scene': 'residential_area',
                'completed_puzzles': ['puzzle_001'],
                'discovered_pets': ['cat_001', 'dog_001']
            },
            'settings': {
                'master_volume': 0.8,
                'music_volume': 0.7
            }
        }
        
        return save_data
    
    def _get_mode_button_rects(self) -> Dict[str, pygame.Rect]:
        """モードボタンの矩形を取得"""
        button_width = 120
        button_height = 40
        
        return {
            'save': pygame.Rect(200, 100, button_width, button_height),
            'load': pygame.Rect(340, 100, button_width, button_height)
        }
    
    def _get_slot_rects(self) -> List[pygame.Rect]:
        """スロット矩形のリストを取得"""
        rects = []
        slot_width = self.screen_width - 200
        slot_height = 80
        start_y = 160
        
        for i in range(self.max_slots):
            rect = pygame.Rect(100, start_y + i * (slot_height + 10), slot_width, slot_height)
            rects.append(rect)
        
        return rects
    
    def _get_action_button_rects(self) -> Dict[str, pygame.Rect]:
        """アクションボタンの矩形を取得"""
        return {
            'delete': pygame.Rect(self.screen_width - 150, self.screen_height - 100, 100, 40)
        }
    
    def _get_confirm_button_rects(self) -> Dict[str, pygame.Rect]:
        """確認ボタンの矩形を取得"""
        center_x = self.screen_width // 2
        center_y = self.screen_height // 2
        
        return {
            'yes': pygame.Rect(center_x - 80, center_y + 20, 60, 40),
            'no': pygame.Rect(center_x + 20, center_y + 20, 60, 40)
        }
    
    def draw(self):
        """セーブ/ロードメニューを描画"""
        # 背景
        self.screen.fill(self.colors['background'])
        
        # タイトル
        title_surface = self.font_manager.render_text("セーブ/ロード", 36, self.colors['text'])
        title_rect = title_surface.get_rect(center=(self.screen_width // 2, 50))
        self.screen.blit(title_surface, title_rect)
        
        # モード切り替えボタン
        self._draw_mode_buttons()
        
        # スロット一覧
        self._draw_slots()
        
        # アクションボタン
        self._draw_action_buttons()
        
        # 確認ダイアログ
        if self.is_confirming:
            self._draw_confirm_dialog()
        
        # 操作説明
        self._draw_controls()
    
    def _draw_mode_buttons(self):
        """モードボタンを描画"""
        mode_buttons = self._get_mode_button_rects()
        
        for mode_name, rect in mode_buttons.items():
            is_selected = mode_name == self.mode
            bg_color = self.colors['selected'] if is_selected else self.colors['panel']
            
            pygame.draw.rect(self.screen, bg_color, rect)
            pygame.draw.rect(self.screen, self.colors['text'], rect, 2)
            
            # ボタンテキスト
            text = "セーブ" if mode_name == "save" else "ロード"
            text_surface = self.font_manager.render_text(text, 18, self.colors['text'])
            text_rect = text_surface.get_rect(center=rect.center)
            self.screen.blit(text_surface, text_rect)
    
    def _draw_slots(self):
        """スロットを描画"""
        slot_rects = self._get_slot_rects()
        
        for i, (slot, rect) in enumerate(zip(self.save_slots, slot_rects)):
            is_selected = i == self.selected_slot
            
            # スロット背景
            if is_selected:
                bg_color = self.colors['selected']
            elif slot.is_empty:
                bg_color = self.colors['empty_slot']
            else:
                bg_color = self.colors['panel']
            
            pygame.draw.rect(self.screen, bg_color, rect)
            pygame.draw.rect(self.screen, self.colors['text'], rect, 2)
            
            # スロット情報
            if slot.is_empty:
                # 空スロット
                empty_text = f"スロット {i + 1} - 空"
                empty_surface = self.font_manager.render_text(empty_text, 20, self.colors['text'])
                empty_rect = empty_surface.get_rect(center=rect.center)
                self.screen.blit(empty_surface, empty_rect)
            else:
                # セーブデータ情報
                info_x = rect.x + 20
                info_y = rect.y + 10
                
                # セーブ名
                name_surface = self.font_manager.render_text(slot.save_name, 18, self.colors['text'])
                self.screen.blit(name_surface, (info_x, info_y))
                
                # 日時
                date_surface = self.font_manager.render_text(slot.save_date, 14, self.colors['text'])
                self.screen.blit(date_surface, (info_x, info_y + 25))
                
                # プレイ時間と進行度
                time_text = f"プレイ時間: {slot.play_time}"
                time_surface = self.font_manager.render_text(time_text, 14, self.colors['text'])
                self.screen.blit(time_surface, (info_x + 300, info_y + 25))
                
                progress_text = f"進行度: {slot.progress}"
                progress_surface = self.font_manager.render_text(progress_text, 14, self.colors['text'])
                self.screen.blit(progress_surface, (info_x + 500, info_y + 25))
    
    def _draw_action_buttons(self):
        """アクションボタンを描画"""
        action_buttons = self._get_action_button_rects()
        
        # 削除ボタン
        delete_rect = action_buttons['delete']
        if not self.save_slots[self.selected_slot].is_empty:
            pygame.draw.rect(self.screen, self.colors['delete_button'], delete_rect)
            pygame.draw.rect(self.screen, self.colors['text'], delete_rect, 2)
            
            delete_text = self.font_manager.render_text("削除", 16, self.colors['text'])
            delete_text_rect = delete_text.get_rect(center=delete_rect.center)
            self.screen.blit(delete_text, delete_text_rect)
    
    def _draw_confirm_dialog(self):
        """確認ダイアログを描画"""
        # オーバーレイ
        overlay = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 128))
        self.screen.blit(overlay, (0, 0))
        
        # ダイアログ背景
        dialog_rect = pygame.Rect(self.screen_width // 2 - 200, self.screen_height // 2 - 80, 400, 160)
        pygame.draw.rect(self.screen, self.colors['panel'], dialog_rect)
        pygame.draw.rect(self.screen, self.colors['text'], dialog_rect, 3)
        
        # 確認メッセージ
        messages = {
            'save': 'このスロットにセーブしますか？',
            'overwrite': '既存のデータを上書きしますか？',
            'load': 'このデータをロードしますか？',
            'delete': 'このセーブデータを削除しますか？'
        }
        
        message = messages.get(self.confirm_action, '実行しますか？')
        message_surface = self.font_manager.render_text(message, 18, self.colors['text'])
        message_rect = message_surface.get_rect(center=(dialog_rect.centerx, dialog_rect.y + 40))
        self.screen.blit(message_surface, message_rect)
        
        # 確認ボタン
        confirm_buttons = self._get_confirm_button_rects()
        
        # はいボタン
        yes_rect = confirm_buttons['yes']
        pygame.draw.rect(self.screen, self.colors['save_button'], yes_rect)
        pygame.draw.rect(self.screen, self.colors['text'], yes_rect, 2)
        yes_text = self.font_manager.render_text("はい", 16, self.colors['text'])
        yes_text_rect = yes_text.get_rect(center=yes_rect.center)
        self.screen.blit(yes_text, yes_text_rect)
        
        # いいえボタン
        no_rect = confirm_buttons['no']
        pygame.draw.rect(self.screen, self.colors['delete_button'], no_rect)
        pygame.draw.rect(self.screen, self.colors['text'], no_rect, 2)
        no_text = self.font_manager.render_text("いいえ", 16, self.colors['text'])
        no_text_rect = no_text.get_rect(center=no_rect.center)
        self.screen.blit(no_text, no_text_rect)
        
        # キー操作説明
        key_help = "Y: はい / N: いいえ"
        key_surface = self.font_manager.render_text(key_help, 14, self.colors['text'])
        key_rect = key_surface.get_rect(center=(dialog_rect.centerx, dialog_rect.bottom - 20))
        self.screen.blit(key_surface, key_rect)
    
    def _draw_controls(self):
        """操作説明を描画"""
        if self.is_confirming:
            return
        
        controls = [
            "TAB: モード切り替え",
            "↑↓: スロット選択",
            "Enter: 実行",
            "Delete: 削除",
            "ESC: 戻る"
        ]
        
        start_y = self.screen_height - 120
        for i, control in enumerate(controls):
            control_surface = self.font_manager.render_text(control, 14, self.colors['text'])
            self.screen.blit(control_surface, (50, start_y + i * 20))
