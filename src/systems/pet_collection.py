"""
ペット図鑑システム

発見・救助したペットの記録を管理
"""

import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from pathlib import Path

from config.constants import PET_TYPES, PET_STATE_RESCUED, PET_STATE_RETURNED


@dataclass
class PetRecord:
    """ペット記録クラス"""
    pet_id: str
    pet_type: str
    name: str = ""
    discovery_date: str = ""
    rescue_date: str = ""
    return_date: str = ""
    owner_name: str = ""
    location_found: str = ""
    trust_level_final: int = 0
    personality_traits: Dict[str, int] = None
    rescue_method: str = ""
    rescue_time_minutes: int = 0
    mini_games_played: List[str] = None
    photos_taken: int = 0
    notes: str = ""
    rarity: int = 1  # 1-5 (1:コモン, 5:レジェンダリー)
    
    def __post_init__(self):
        if self.personality_traits is None:
            self.personality_traits = {}
        if self.mini_games_played is None:
            self.mini_games_played = []


class PetCollection:
    """ペット図鑑クラス"""
    
    def __init__(self, data_path: Path):
        """
        ペット図鑑を初期化
        
        Args:
            data_path: データディレクトリのパス
        """
        self.data_path = data_path
        self.collection_file = data_path / "pet_collection.json"
        
        # ペット記録
        self.discovered_pets: Dict[str, PetRecord] = {}
        self.rescued_pets: Dict[str, PetRecord] = {}
        self.returned_pets: Dict[str, PetRecord] = {}
        
        # 統計情報
        self.stats = {
            "total_discovered": 0,
            "total_rescued": 0,
            "total_returned": 0,
            "discovery_rate": {},  # pet_type -> count
            "rescue_rate": {},     # pet_type -> count
            "average_rescue_time": 0,
            "favorite_pet_type": "",
            "rarest_pet_rescued": None,
            "first_discovery_date": "",
            "last_activity_date": ""
        }
        
        # ペット種類別の情報
        self.pet_type_info = self._initialize_pet_type_info()
        
        # データを読み込み
        self.load_collection()
    
    def _initialize_pet_type_info(self) -> Dict[str, Dict[str, Any]]:
        """ペット種類別の情報を初期化"""
        return {
            "dog": {
                "name_ja": "犬",
                "name_en": "Dog",
                "description": "人懐っこく忠実なパートナー",
                "common_traits": ["friendly", "loyal", "energetic"],
                "preferred_items": ["dog_food", "ball"],
                "base_rarity": 1
            },
            "cat": {
                "name_ja": "猫",
                "name_en": "Cat", 
                "description": "独立心旺盛で気まぐれな友達",
                "common_traits": ["independent", "curious", "aloof"],
                "preferred_items": ["cat_food", "feather_toy"],
                "base_rarity": 1
            },
            "rabbit": {
                "name_ja": "うさぎ",
                "name_en": "Rabbit",
                "description": "おとなしく優しい小動物",
                "common_traits": ["timid", "gentle", "quick"],
                "preferred_items": ["universal_food"],
                "base_rarity": 2
            },
            "hamster": {
                "name_ja": "ハムスター", 
                "name_en": "Hamster",
                "description": "小さくて活発な愛らしいペット",
                "common_traits": ["active", "small", "nocturnal"],
                "preferred_items": ["universal_food"],
                "base_rarity": 2
            },
            "bird": {
                "name_ja": "鳥",
                "name_en": "Bird",
                "description": "美しい鳴き声を持つ知的な生き物",
                "common_traits": ["vocal", "intelligent", "social"],
                "preferred_items": ["universal_food"],
                "base_rarity": 3
            },
            "fish": {
                "name_ja": "魚",
                "name_en": "Fish",
                "description": "静かで優雅な水中の住人",
                "common_traits": ["calm", "silent", "graceful"],
                "preferred_items": ["universal_food"],
                "base_rarity": 3
            },
            "turtle": {
                "name_ja": "カメ",
                "name_en": "Turtle",
                "description": "ゆっくりと着実に生きる賢者",
                "common_traits": ["slow", "patient", "wise"],
                "preferred_items": ["universal_food"],
                "base_rarity": 4
            },
            "ferret": {
                "name_ja": "フェレット",
                "name_en": "Ferret",
                "description": "いたずら好きで元気いっぱい",
                "common_traits": ["playful", "mischievous", "energetic"],
                "preferred_items": ["universal_food"],
                "base_rarity": 4
            }
        }
    
    def discover_pet(self, pet_info: Dict[str, Any]) -> bool:
        """
        ペットを発見記録
        
        Args:
            pet_info: ペット情報
            
        Returns:
            記録成功時True
        """
        try:
            pet_id = pet_info.get("id")
            if not pet_id or pet_id in self.discovered_pets:
                return False
            
            # ペット記録を作成
            record = PetRecord(
                pet_id=pet_id,
                pet_type=pet_info.get("type", "unknown"),
                name=pet_info.get("name", f"{pet_info.get('type', 'Pet')}_{pet_id[-4:]}"),
                discovery_date=datetime.now().isoformat(),
                owner_name=pet_info.get("owner_name", ""),
                location_found=pet_info.get("location", ""),
                personality_traits=pet_info.get("personality", {}),
                rarity=self._calculate_rarity(pet_info)
            )
            
            # 記録を追加
            self.discovered_pets[pet_id] = record
            
            # 統計を更新
            self._update_discovery_stats(record)
            
            print(f"新しいペットを発見: {record.name} ({record.pet_type})")
            return True
            
        except Exception as e:
            print(f"ペット発見記録エラー: {e}")
            return False
    
    def rescue_pet(self, pet_id: str, rescue_info: Dict[str, Any]) -> bool:
        """
        ペット救助記録
        
        Args:
            pet_id: ペットID
            rescue_info: 救助情報
            
        Returns:
            記録成功時True
        """
        try:
            if pet_id not in self.discovered_pets:
                print(f"未発見のペット: {pet_id}")
                return False
            
            if pet_id in self.rescued_pets:
                print(f"既に救助済み: {pet_id}")
                return False
            
            # 発見記録をコピーして救助情報を追加
            record = self.discovered_pets[pet_id]
            record.rescue_date = datetime.now().isoformat()
            record.trust_level_final = rescue_info.get("trust_level", 0)
            record.rescue_method = rescue_info.get("method", "")
            record.rescue_time_minutes = rescue_info.get("time_minutes", 0)
            record.mini_games_played = rescue_info.get("mini_games", [])
            record.notes = rescue_info.get("notes", "")
            
            # 救助記録に追加
            self.rescued_pets[pet_id] = record
            
            # 統計を更新
            self._update_rescue_stats(record)
            
            print(f"ペットを救助: {record.name}")
            return True
            
        except Exception as e:
            print(f"ペット救助記録エラー: {e}")
            return False
    
    def return_pet(self, pet_id: str, return_info: Dict[str, Any]) -> bool:
        """
        ペット返却記録
        
        Args:
            pet_id: ペットID
            return_info: 返却情報
            
        Returns:
            記録成功時True
        """
        try:
            if pet_id not in self.rescued_pets:
                print(f"未救助のペット: {pet_id}")
                return False
            
            if pet_id in self.returned_pets:
                print(f"既に返却済み: {pet_id}")
                return False
            
            # 救助記録をコピーして返却情報を追加
            record = self.rescued_pets[pet_id]
            record.return_date = datetime.now().isoformat()
            
            # 返却記録に追加
            self.returned_pets[pet_id] = record
            
            # 統計を更新
            self._update_return_stats(record)
            
            print(f"ペットを返却: {record.name}")
            return True
            
        except Exception as e:
            print(f"ペット返却記録エラー: {e}")
            return False
    
    def _calculate_rarity(self, pet_info: Dict[str, Any]) -> int:
        """ペットのレアリティを計算"""
        pet_type = pet_info.get("type", "dog")
        base_rarity = self.pet_type_info.get(pet_type, {}).get("base_rarity", 1)
        
        # 個性の特殊性でレアリティを調整
        personality = pet_info.get("personality", {})
        special_traits = sum(1 for value in personality.values() if value > 90)
        
        rarity = base_rarity + (special_traits // 2)
        return min(5, max(1, rarity))
    
    def _update_discovery_stats(self, record: PetRecord):
        """発見統計を更新"""
        self.stats["total_discovered"] += 1
        
        # 種類別統計
        pet_type = record.pet_type
        if pet_type not in self.stats["discovery_rate"]:
            self.stats["discovery_rate"][pet_type] = 0
        self.stats["discovery_rate"][pet_type] += 1
        
        # 初回発見日
        if not self.stats["first_discovery_date"]:
            self.stats["first_discovery_date"] = record.discovery_date
        
        self.stats["last_activity_date"] = record.discovery_date
    
    def _update_rescue_stats(self, record: PetRecord):
        """救助統計を更新"""
        self.stats["total_rescued"] += 1
        
        # 種類別統計
        pet_type = record.pet_type
        if pet_type not in self.stats["rescue_rate"]:
            self.stats["rescue_rate"][pet_type] = 0
        self.stats["rescue_rate"][pet_type] += 1
        
        # 平均救助時間
        total_time = self.stats["average_rescue_time"] * (self.stats["total_rescued"] - 1)
        total_time += record.rescue_time_minutes
        self.stats["average_rescue_time"] = total_time / self.stats["total_rescued"]
        
        # 最もレアなペット
        if (not self.stats["rarest_pet_rescued"] or 
            record.rarity > self.stats["rarest_pet_rescued"]["rarity"]):
            self.stats["rarest_pet_rescued"] = {
                "pet_id": record.pet_id,
                "name": record.name,
                "type": record.pet_type,
                "rarity": record.rarity
            }
        
        self.stats["last_activity_date"] = record.rescue_date
    
    def _update_return_stats(self, record: PetRecord):
        """返却統計を更新"""
        self.stats["total_returned"] += 1
        self.stats["last_activity_date"] = record.return_date
    
    def get_collection_summary(self) -> Dict[str, Any]:
        """図鑑の概要を取得"""
        # お気に入りのペット種類を計算
        if self.stats["rescue_rate"]:
            favorite_type = max(self.stats["rescue_rate"], 
                              key=self.stats["rescue_rate"].get)
            self.stats["favorite_pet_type"] = favorite_type
        
        return {
            "stats": self.stats.copy(),
            "completion_rate": {
                "discovered": len(self.discovered_pets),
                "rescued": len(self.rescued_pets),
                "returned": len(self.returned_pets),
                "total_possible": len(PET_TYPES) * 10  # 仮の総数
            },
            "pet_types_discovered": len(set(record.pet_type for record in self.discovered_pets.values())),
            "pet_types_total": len(PET_TYPES)
        }
    
    def get_pets_by_type(self, pet_type: str) -> List[Dict[str, Any]]:
        """指定種類のペット記録を取得"""
        result = []
        
        for record in self.discovered_pets.values():
            if record.pet_type == pet_type:
                result.append({
                    "record": asdict(record),
                    "status": self._get_pet_status(record.pet_id)
                })
        
        return result
    
    def _get_pet_status(self, pet_id: str) -> str:
        """ペットの状態を取得"""
        if pet_id in self.returned_pets:
            return "returned"
        elif pet_id in self.rescued_pets:
            return "rescued"
        elif pet_id in self.discovered_pets:
            return "discovered"
        else:
            return "unknown"
    
    def get_pet_details(self, pet_id: str) -> Optional[Dict[str, Any]]:
        """ペットの詳細情報を取得"""
        if pet_id not in self.discovered_pets:
            return None
        
        record = self.discovered_pets[pet_id]
        status = self._get_pet_status(pet_id)
        
        return {
            "record": asdict(record),
            "status": status,
            "type_info": self.pet_type_info.get(record.pet_type, {}),
            "achievements": self._get_pet_achievements(record)
        }
    
    def _get_pet_achievements(self, record: PetRecord) -> List[str]:
        """ペットの実績を取得"""
        achievements = []
        
        if record.trust_level_final >= 90:
            achievements.append("完全な信頼")
        if record.rescue_time_minutes <= 5:
            achievements.append("スピード救助")
        if record.rarity >= 4:
            achievements.append("レアペット")
        if len(record.mini_games_played) >= 3:
            achievements.append("ゲームマスター")
        
        return achievements
    
    def search_pets(self, query: str) -> List[Dict[str, Any]]:
        """ペットを検索"""
        results = []
        query_lower = query.lower()
        
        for record in self.discovered_pets.values():
            if (query_lower in record.name.lower() or
                query_lower in record.pet_type.lower() or
                query_lower in record.owner_name.lower()):
                
                results.append({
                    "record": asdict(record),
                    "status": self._get_pet_status(record.pet_id)
                })
        
        return results
    
    def save_collection(self) -> bool:
        """図鑑データを保存"""
        try:
            data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "discovered_pets": {k: asdict(v) for k, v in self.discovered_pets.items()},
                "rescued_pets": {k: asdict(v) for k, v in self.rescued_pets.items()},
                "returned_pets": {k: asdict(v) for k, v in self.returned_pets.items()},
                "stats": self.stats
            }
            
            with open(self.collection_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"図鑑保存エラー: {e}")
            return False
    
    def load_collection(self) -> bool:
        """図鑑データを読み込み"""
        try:
            if not self.collection_file.exists():
                return True  # 新規作成
            
            with open(self.collection_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # データを復元
            for pet_id, record_data in data.get("discovered_pets", {}).items():
                self.discovered_pets[pet_id] = PetRecord(**record_data)
            
            for pet_id, record_data in data.get("rescued_pets", {}).items():
                self.rescued_pets[pet_id] = PetRecord(**record_data)
            
            for pet_id, record_data in data.get("returned_pets", {}).items():
                self.returned_pets[pet_id] = PetRecord(**record_data)
            
            self.stats.update(data.get("stats", {}))
            
            return True
            
        except Exception as e:
            print(f"図鑑読み込みエラー: {e}")
            return False
