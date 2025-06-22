"""
セーブシステム

ゲームデータの保存・読み込みを管理
"""

import json
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

from config.settings import GameSettings


class SaveSystem:
    """セーブシステムクラス"""
    
    def __init__(self, settings: GameSettings):
        self.settings = settings
        self.saves_path = settings.saves_path
        self.backup_path = self.saves_path / "backup"
        
        # ディレクトリを作成
        self._ensure_directories()
    
    def _ensure_directories(self):
        """必要なディレクトリを作成"""
        self.saves_path.mkdir(exist_ok=True)
        self.backup_path.mkdir(exist_ok=True)
        
        # セーブスロットディレクトリを作成
        for i in range(1, self.settings.max_save_slots + 1):
            slot_path = self.saves_path / f"slot{i}"
            slot_path.mkdir(exist_ok=True)
    
    def save_game(self, slot_number: int, game_data: Dict[str, Any]) -> bool:
        """
        ゲームデータを保存
        
        Args:
            slot_number: セーブスロット番号 (1-3)
            game_data: 保存するゲームデータ
            
        Returns:
            保存成功時True
        """
        try:
            if not (1 <= slot_number <= self.settings.max_save_slots):
                raise ValueError(f"無効なスロット番号: {slot_number}")
            
            slot_path = self.saves_path / f"slot{slot_number}"
            save_file = slot_path / "save_data.json"
            
            # バックアップを作成
            if save_file.exists():
                self._create_backup(slot_number)
            
            # セーブデータを準備
            save_data = {
                "version": self.settings.version,
                "timestamp": datetime.now().isoformat(),
                "slot_number": slot_number,
                "game_data": game_data
            }
            
            # JSONファイルに保存
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            # メタデータを保存
            self._save_metadata(slot_number, game_data)
            
            print(f"ゲームデータをスロット{slot_number}に保存しました")
            return True
            
        except Exception as e:
            print(f"セーブエラー: {e}")
            return False
    
    def load_game(self, slot_number: int) -> Optional[Dict[str, Any]]:
        """
        ゲームデータを読み込み
        
        Args:
            slot_number: セーブスロット番号 (1-3)
            
        Returns:
            ゲームデータ（失敗時はNone）
        """
        try:
            if not (1 <= slot_number <= self.settings.max_save_slots):
                raise ValueError(f"無効なスロット番号: {slot_number}")
            
            slot_path = self.saves_path / f"slot{slot_number}"
            save_file = slot_path / "save_data.json"
            
            if not save_file.exists():
                print(f"スロット{slot_number}にセーブデータがありません")
                return None
            
            # JSONファイルから読み込み
            with open(save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            # バージョンチェック
            if save_data.get("version") != self.settings.version:
                print(f"警告: セーブデータのバージョンが異なります")
            
            print(f"スロット{slot_number}からゲームデータを読み込みました")
            return save_data.get("game_data")
            
        except Exception as e:
            print(f"ロードエラー: {e}")
            return None
    
    def delete_save(self, slot_number: int) -> bool:
        """
        セーブデータを削除
        
        Args:
            slot_number: セーブスロット番号 (1-3)
            
        Returns:
            削除成功時True
        """
        try:
            if not (1 <= slot_number <= self.settings.max_save_slots):
                raise ValueError(f"無効なスロット番号: {slot_number}")
            
            slot_path = self.saves_path / f"slot{slot_number}"
            save_file = slot_path / "save_data.json"
            metadata_file = slot_path / "metadata.json"
            
            # ファイルを削除
            if save_file.exists():
                save_file.unlink()
            if metadata_file.exists():
                metadata_file.unlink()
            
            print(f"スロット{slot_number}のセーブデータを削除しました")
            return True
            
        except Exception as e:
            print(f"削除エラー: {e}")
            return False
    
    def get_save_info(self, slot_number: int) -> Optional[Dict[str, Any]]:
        """
        セーブデータの情報を取得
        
        Args:
            slot_number: セーブスロット番号 (1-3)
            
        Returns:
            セーブデータ情報（存在しない場合はNone）
        """
        try:
            slot_path = self.saves_path / f"slot{slot_number}"
            metadata_file = slot_path / "metadata.json"
            
            if not metadata_file.exists():
                return None
            
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
            
            return metadata
            
        except Exception as e:
            print(f"メタデータ読み込みエラー: {e}")
            return None
    
    def list_saves(self) -> List[Dict[str, Any]]:
        """
        全セーブスロットの情報を取得
        
        Returns:
            セーブスロット情報のリスト
        """
        saves = []
        
        for i in range(1, self.settings.max_save_slots + 1):
            save_info = self.get_save_info(i)
            if save_info:
                save_info["slot_number"] = i
                saves.append(save_info)
            else:
                saves.append({
                    "slot_number": i,
                    "empty": True
                })
        
        return saves
    
    def _save_metadata(self, slot_number: int, game_data: Dict[str, Any]):
        """メタデータを保存"""
        slot_path = self.saves_path / f"slot{slot_number}"
        metadata_file = slot_path / "metadata.json"
        
        # プレイヤー情報から必要な情報を抽出
        player_data = game_data.get("player", {})
        
        metadata = {
            "slot_number": slot_number,
            "timestamp": datetime.now().isoformat(),
            "play_time": player_data.get("play_time", 0),
            "pets_rescued": player_data.get("pets_rescued", 0),
            "level": player_data.get("level", 1),
            "location": game_data.get("current_scene", "unknown"),
            "screenshot": None  # TODO: スクリーンショット機能
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    def _create_backup(self, slot_number: int):
        """バックアップを作成"""
        try:
            slot_path = self.saves_path / f"slot{slot_number}"
            save_file = slot_path / "save_data.json"
            
            if save_file.exists():
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = self.backup_path / f"slot{slot_number}_{timestamp}.json"
                shutil.copy2(save_file, backup_file)
                
                # 古いバックアップを削除（最新5個まで保持）
                self._cleanup_backups(slot_number)
                
        except Exception as e:
            print(f"バックアップ作成エラー: {e}")
    
    def _cleanup_backups(self, slot_number: int, max_backups: int = 5):
        """古いバックアップを削除"""
        try:
            pattern = f"slot{slot_number}_*.json"
            backup_files = list(self.backup_path.glob(pattern))
            
            # 作成日時でソート
            backup_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # 古いファイルを削除
            for backup_file in backup_files[max_backups:]:
                backup_file.unlink()
                
        except Exception as e:
            print(f"バックアップクリーンアップエラー: {e}")
    
    def auto_save(self, game_data: Dict[str, Any]) -> bool:
        """
        オートセーブ
        
        Args:
            game_data: 保存するゲームデータ
            
        Returns:
            保存成功時True
        """
        try:
            auto_save_file = self.saves_path / "auto_save.json"
            
            save_data = {
                "version": self.settings.version,
                "timestamp": datetime.now().isoformat(),
                "auto_save": True,
                "game_data": game_data
            }
            
            with open(auto_save_file, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"オートセーブエラー: {e}")
            return False
    
    def load_auto_save(self) -> Optional[Dict[str, Any]]:
        """
        オートセーブデータを読み込み
        
        Returns:
            ゲームデータ（失敗時はNone）
        """
        try:
            auto_save_file = self.saves_path / "auto_save.json"
            
            if not auto_save_file.exists():
                return None
            
            with open(auto_save_file, 'r', encoding='utf-8') as f:
                save_data = json.load(f)
            
            return save_data.get("game_data")
            
        except Exception as e:
            print(f"オートセーブ読み込みエラー: {e}")
            return None
