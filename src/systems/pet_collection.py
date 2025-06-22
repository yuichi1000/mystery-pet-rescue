"""
ペット図鑑システム
ペット情報の管理、救助状態の追跡、図鑑データの操作を行う
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict
from enum import Enum

class PetRarity(Enum):
    """ペットのレア度"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"

@dataclass
class PetInfo:
    """ペット情報データクラス"""
    id: str
    name: str
    species: str
    breed: str
    description: str
    characteristics: List[str]
    rarity: str
    image_path: str
    found_locations: List[str]
    rescue_difficulty: int
    rescue_hints: List[str]

@dataclass
class PetRescueRecord:
    """ペット救助記録データクラス"""
    pet_id: str
    rescued: bool = False
    rescue_date: Optional[str] = None
    rescue_location: Optional[str] = None
    rescue_time_spent: Optional[int] = None  # 秒単位
    rescue_attempts: int = 0

class PetCollection:
    """ペット図鑑管理クラス"""
    
    def __init__(self, data_path: str = "data/pets_database.json", 
                 save_path: str = "saves/pet_collection.json"):
        self.data_path = data_path
        self.save_path = save_path
        self.pets_data: Dict[str, PetInfo] = {}
        self.rarity_info: Dict[str, Dict[str, Any]] = {}
        self.rescue_records: Dict[str, PetRescueRecord] = {}
        
        self._load_pets_database()
        self._load_rescue_records()
    
    def _load_pets_database(self) -> None:
        """ペットデータベースを読み込み"""
        try:
            with open(self.data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # ペット情報を読み込み
            for pet_data in data.get('pets', []):
                pet_info = PetInfo(**pet_data)
                self.pets_data[pet_info.id] = pet_info
            
            # レア度情報を読み込み
            self.rarity_info = data.get('rarity_info', {})
            
        except FileNotFoundError:
            print(f"警告: ペットデータベースファイルが見つかりません: {self.data_path}")
        except json.JSONDecodeError as e:
            print(f"エラー: ペットデータベースの読み込みに失敗しました: {e}")
    
    def _load_rescue_records(self) -> None:
        """救助記録を読み込み"""
        try:
            with open(self.save_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for record_data in data.get('rescue_records', []):
                record = PetRescueRecord(**record_data)
                self.rescue_records[record.pet_id] = record
                
        except FileNotFoundError:
            # 初回起動時はファイルが存在しないので、空の記録で初期化
            self._initialize_rescue_records()
        except json.JSONDecodeError as e:
            print(f"エラー: 救助記録の読み込みに失敗しました: {e}")
            self._initialize_rescue_records()
    
    def _initialize_rescue_records(self) -> None:
        """救助記録を初期化"""
        for pet_id in self.pets_data.keys():
            self.rescue_records[pet_id] = PetRescueRecord(pet_id=pet_id)
    
    def save_rescue_records(self) -> bool:
        """救助記録を保存"""
        try:
            # 保存ディレクトリを作成
            os.makedirs(os.path.dirname(self.save_path), exist_ok=True)
            
            # 救助記録をJSON形式で保存
            save_data = {
                'rescue_records': [asdict(record) for record in self.rescue_records.values()],
                'last_updated': datetime.now().isoformat()
            }
            
            with open(self.save_path, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"エラー: 救助記録の保存に失敗しました: {e}")
            return False
    
    def rescue_pet(self, pet_id: str, location: str, time_spent: int) -> bool:
        """ペットを救助する"""
        if pet_id not in self.pets_data:
            return False
        
        if pet_id not in self.rescue_records:
            self.rescue_records[pet_id] = PetRescueRecord(pet_id=pet_id)
        
        record = self.rescue_records[pet_id]
        record.rescued = True
        record.rescue_date = datetime.now().isoformat()
        record.rescue_location = location
        record.rescue_time_spent = time_spent
        record.rescue_attempts += 1
        
        self.save_rescue_records()
        return True
    
    def is_pet_rescued(self, pet_id: str) -> bool:
        """ペットが救助済みかチェック"""
        return self.rescue_records.get(pet_id, PetRescueRecord(pet_id)).rescued
    
    def get_pet_info(self, pet_id: str) -> Optional[PetInfo]:
        """ペット情報を取得"""
        return self.pets_data.get(pet_id)
    
    def get_rescue_record(self, pet_id: str) -> Optional[PetRescueRecord]:
        """救助記録を取得"""
        return self.rescue_records.get(pet_id)
    
    def get_all_pets(self) -> List[PetInfo]:
        """全ペット情報を取得"""
        return list(self.pets_data.values())
    
    def get_rescued_pets(self) -> List[PetInfo]:
        """救助済みペット一覧を取得"""
        rescued_pets = []
        for pet_id, pet_info in self.pets_data.items():
            if self.is_pet_rescued(pet_id):
                rescued_pets.append(pet_info)
        return rescued_pets
    
    def get_unrescued_pets(self) -> List[PetInfo]:
        """未救助ペット一覧を取得"""
        unrescued_pets = []
        for pet_id, pet_info in self.pets_data.items():
            if not self.is_pet_rescued(pet_id):
                unrescued_pets.append(pet_info)
        return unrescued_pets
    
    def filter_pets_by_species(self, species: str) -> List[PetInfo]:
        """種類でペットをフィルター"""
        return [pet for pet in self.pets_data.values() if pet.species == species]
    
    def filter_pets_by_rarity(self, rarity: str) -> List[PetInfo]:
        """レア度でペットをフィルター"""
        return [pet for pet in self.pets_data.values() if pet.rarity == rarity]
    
    def search_pets(self, query: str) -> List[PetInfo]:
        """ペットを検索（名前、種類、品種で検索）"""
        query = query.lower()
        results = []
        
        for pet in self.pets_data.values():
            if (query in pet.name.lower() or 
                query in pet.species.lower() or 
                query in pet.breed.lower() or
                any(query in char.lower() for char in pet.characteristics)):
                results.append(pet)
        
        return results
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """図鑑の統計情報を取得"""
        total_pets = len(self.pets_data)
        rescued_count = len(self.get_rescued_pets())
        
        # レア度別統計
        rarity_stats = {}
        for rarity in PetRarity:
            rarity_pets = self.filter_pets_by_rarity(rarity.value)
            rescued_rarity_pets = [pet for pet in rarity_pets if self.is_pet_rescued(pet.id)]
            rarity_stats[rarity.value] = {
                'total': len(rarity_pets),
                'rescued': len(rescued_rarity_pets),
                'completion_rate': len(rescued_rarity_pets) / len(rarity_pets) * 100 if rarity_pets else 0
            }
        
        # 種類別統計
        species_stats = {}
        species_list = list(set(pet.species for pet in self.pets_data.values()))
        for species in species_list:
            species_pets = self.filter_pets_by_species(species)
            rescued_species_pets = [pet for pet in species_pets if self.is_pet_rescued(pet.id)]
            species_stats[species] = {
                'total': len(species_pets),
                'rescued': len(rescued_species_pets),
                'completion_rate': len(rescued_species_pets) / len(species_pets) * 100 if species_pets else 0
            }
        
        return {
            'total_pets': total_pets,
            'rescued_pets': rescued_count,
            'completion_rate': rescued_count / total_pets * 100 if total_pets > 0 else 0,
            'rarity_stats': rarity_stats,
            'species_stats': species_stats
        }
    
    def get_rarity_info(self, rarity: str) -> Dict[str, Any]:
        """レア度情報を取得"""
        return self.rarity_info.get(rarity, {
            'name': rarity.capitalize(),
            'color': '#666666',
            'description': '不明なレア度'
        })
