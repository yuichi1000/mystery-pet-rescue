"""
セーブ/ロードシステム
ゲームデータの保存と読み込み（エラーハンドリング強化版）
"""

import json
import os
import time
from pathlib import Path
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict
from datetime import datetime
import shutil

from src.utils.exceptions import SaveLoadError
from src.utils.error_handler import handle_error, safe_execute

@dataclass
class SaveData:
    """セーブデータ構造"""
    slot_id: int
    save_name: str
    save_date: str
    play_time: float
    player_data: Dict[str, Any]
    game_progress: Dict[str, Any]
    pet_collection: Dict[str, Any]
    game_stats: Dict[str, Any]
    version: str = "1.0.0"

class SaveLoadSystem:
    """セーブ/ロードシステム"""
    
    def __init__(self):
        self.save_dir = Path("saves")
        self.save_dir.mkdir(exist_ok=True)
        self.max_slots = 3
        
    def get_save_slots(self) -> List[Optional[SaveData]]:
        """全セーブスロットの情報を取得"""
        slots = [None] * self.max_slots
        
        for slot_id in range(self.max_slots):
            save_file = self.save_dir / f"save_slot_{slot_id}.json"
            if save_file.exists():
                try:
                    with open(save_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        slots[slot_id] = SaveData(**data)
                except Exception as e:
                    print(f"❌ セーブスロット{slot_id}読み込みエラー: {e}")
                    
        return slots
    
    def save_game(self, slot_id: int, game_data: Dict[str, Any], 
                  save_name: str = None) -> bool:
        """ゲームをセーブ（エラーハンドリング強化版）"""
        
        def _save_game_safe():
            # 入力検証
            if not isinstance(slot_id, int) or slot_id < 0 or slot_id >= self.max_slots:
                raise SaveLoadError("save", f"無効なスロットID: {slot_id}")
            
            if not isinstance(game_data, dict):
                raise SaveLoadError("save", f"無効なゲームデータ: {type(game_data)}")
            
            # セーブデータ作成
            if save_name is None:
                save_name = f"セーブデータ {slot_id + 1}"
            
            # データ検証
            required_keys = ['play_time', 'player_data', 'game_progress', 'pet_collection', 'game_stats']
            for key in required_keys:
                if key not in game_data:
                    game_data[key] = {}
            
            save_data = SaveData(
                slot_id=slot_id,
                save_name=save_name,
                save_date=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                play_time=float(game_data.get('play_time', 0)),
                player_data=dict(game_data.get('player_data', {})),
                game_progress=dict(game_data.get('game_progress', {})),
                pet_collection=dict(game_data.get('pet_collection', {})),
                game_stats=dict(game_data.get('game_stats', {}))
            )
            
            # ファイルパス
            save_file = self.save_dir / f"save_slot_{slot_id}.json"
            backup_file = self.save_dir / f"save_slot_{slot_id}.json.backup"
            
            # 既存ファイルのバックアップ
            if save_file.exists():
                shutil.copy2(save_file, backup_file)
            
            # 一時ファイルに書き込み
            temp_file = self.save_dir / f"save_slot_{slot_id}.json.tmp"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(save_data), f, ensure_ascii=False, indent=2)
            
            # ファイルサイズチェック
            if temp_file.stat().st_size == 0:
                raise SaveLoadError("save", "セーブファイルの書き込みに失敗しました")
            
            # 一時ファイルを本ファイルに移動
            temp_file.replace(save_file)
            
            # バックアップファイルを削除
            if backup_file.exists():
                backup_file.unlink()
            
            print(f"✅ セーブ完了: スロット{slot_id} - {save_name}")
            return True
        
        # 安全な実行
        result = safe_execute(
            _save_game_safe,
            context=f"save_game(slot_id={slot_id})",
            default=False
        )
        
        return result if result is not None else False
    
    def load_game(self, slot_id: int) -> Optional[SaveData]:
        """ゲームをロード"""
        if slot_id < 0 or slot_id >= self.max_slots:
            print(f"❌ 無効なスロットID: {slot_id}")
            return None
            
        save_file = self.save_dir / f"save_slot_{slot_id}.json"
        if not save_file.exists():
            print(f"❌ セーブファイルが存在しません: スロット{slot_id}")
            return None
            
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                save_data = SaveData(**data)
                print(f"✅ ロード完了: {save_data.save_name}")
                return save_data
                
        except Exception as e:
            print(f"❌ ロードエラー: {e}")
            return None
    
    def delete_save(self, slot_id: int) -> bool:
        """セーブデータを削除"""
        if slot_id < 0 or slot_id >= self.max_slots:
            return False
            
        save_file = self.save_dir / f"save_slot_{slot_id}.json"
        if save_file.exists():
            try:
                save_file.unlink()
                print(f"✅ セーブデータ削除: スロット{slot_id}")
                return True
            except Exception as e:
                print(f"❌ 削除エラー: {e}")
                return False
        return False
    
    def quick_save(self, game_data: Dict[str, Any]) -> bool:
        """クイックセーブ（スロット0に自動保存）"""
        return self.save_game(0, game_data, "クイックセーブ")
    
    def auto_save(self, game_data: Dict[str, Any]) -> bool:
        """オートセーブ（専用ファイル）"""
        try:
            auto_save_file = self.save_dir / "auto_save.json"
            save_data = {
                'save_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'play_time': game_data.get('play_time', 0),
                'player_data': game_data.get('player_data', {}),
                'game_progress': game_data.get('game_progress', {}),
                'pet_collection': game_data.get('pet_collection', {}),
                'game_stats': game_data.get('game_stats', {}),
                'version': "1.0.0"
            }
            
            with open(auto_save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
                
            print("✅ オートセーブ完了")
            return True
            
        except Exception as e:
            print(f"❌ オートセーブエラー: {e}")
            return False
