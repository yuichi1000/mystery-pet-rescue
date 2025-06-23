"""
ペットデータローダー
JSONファイルからペット情報を読み込み・管理
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from src.utils.error_handler import handle_error, safe_execute

@dataclass
class PetColorVariant:
    """ペットの色バリエーション"""
    name: str
    name_en: str
    colors: List[str]

@dataclass
class PetPersonality:
    """ペットの性格"""
    traits: List[str]
    friendliness: int
    energy_level: int
    intelligence: int

@dataclass
class SpawnLocation:
    """出現場所"""
    x: int
    y: int
    probability: float

@dataclass
class BehaviorPattern:
    """行動パターン"""
    movement_speed: float
    detection_range: int
    escape_probability: float
    hiding_spots: List[str]
    flight_enabled: bool = False
    flight_height: int = 0

@dataclass
class PetData:
    """ペットデータ"""
    id: str
    name: str
    name_en: str
    species: str
    rarity: str
    description_ja: str
    description_en: str
    sprite_path: str
    color_variants: List[PetColorVariant]
    personality: PetPersonality
    favorite_food: str
    habits: List[str]
    rescue_difficulty: int
    required_items: List[str]
    spawn_locations: List[SpawnLocation]
    behavior_patterns: BehaviorPattern

@dataclass
class RescueItem:
    """救出アイテム"""
    name: str
    name_en: str
    description_ja: str
    description_en: str
    effectiveness: Dict[str, float]

class PetDataLoader:
    """ペットデータローダークラス"""
    
    def __init__(self, data_path: str = "data/pets"):
        self.data_path = Path(data_path)
        self.pets: Dict[str, PetData] = {}
        self.rescue_items: Dict[str, RescueItem] = {}
        self.difficulty_levels: Dict[int, Dict[str, str]] = {}
        self.rarity_info: Dict[str, Dict[str, Any]] = {}
        
        print("📋 ペットデータローダー初期化完了")
    
    def load_pet_data(self, version: str = "v1") -> bool:
        """
        ペットデータを読み込み
        
        Args:
            version: データバージョン
            
        Returns:
            bool: 読み込み成功かどうか
        """
        def _load_data_safe():
            data_file = self.data_path / f"pets_{version}.json"
            
            if not data_file.exists():
                raise FileNotFoundError(f"ペットデータファイルが見つかりません: {data_file}")
            
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # ペットデータの解析
            self._parse_pets(data.get('pets', []))
            
            # 救出アイテムの解析
            self._parse_rescue_items(data.get('rescue_items', {}))
            
            # 難易度レベルの解析
            self.difficulty_levels = data.get('difficulty_levels', {})
            
            # レア度情報の解析
            self.rarity_info = data.get('rarity_info', {})
            
            print(f"✅ ペットデータ読み込み完了: {len(self.pets)}匹のペット")
            print(f"✅ 救出アイテム読み込み完了: {len(self.rescue_items)}個のアイテム")
            
            return True
        
        return safe_execute(
            _load_data_safe,
            context=f"load_pet_data(version={version})",
            default=False
        ) or False
    
    def _parse_pets(self, pets_data: List[Dict[str, Any]]):
        """ペットデータを解析"""
        for pet_dict in pets_data:
            try:
                # 色バリエーション
                color_variants = []
                for variant in pet_dict.get('color_variants', []):
                    color_variants.append(PetColorVariant(
                        name=variant['name'],
                        name_en=variant['name_en'],
                        colors=variant['colors']
                    ))
                
                # 性格
                personality_data = pet_dict.get('personality', {})
                personality = PetPersonality(
                    traits=personality_data.get('traits', []),
                    friendliness=personality_data.get('friendliness', 5),
                    energy_level=personality_data.get('energy_level', 5),
                    intelligence=personality_data.get('intelligence', 5)
                )
                
                # 出現場所
                spawn_locations = []
                for location in pet_dict.get('spawn_locations', []):
                    spawn_locations.append(SpawnLocation(
                        x=location['x'],
                        y=location['y'],
                        probability=location['probability']
                    ))
                
                # 行動パターン
                behavior_data = pet_dict.get('behavior_patterns', {})
                behavior_patterns = BehaviorPattern(
                    movement_speed=behavior_data.get('movement_speed', 2.0),
                    detection_range=behavior_data.get('detection_range', 5),
                    escape_probability=behavior_data.get('escape_probability', 0.5),
                    hiding_spots=behavior_data.get('hiding_spots', []),
                    flight_enabled=behavior_data.get('flight_enabled', False),
                    flight_height=behavior_data.get('flight_height', 0)
                )
                
                # ペットデータ作成
                pet_data = PetData(
                    id=pet_dict['id'],
                    name=pet_dict['name'],
                    name_en=pet_dict['name_en'],
                    species=pet_dict['species'],
                    rarity=pet_dict['rarity'],
                    description_ja=pet_dict['description_ja'],
                    description_en=pet_dict['description_en'],
                    sprite_path=pet_dict['sprite_path'],
                    color_variants=color_variants,
                    personality=personality,
                    favorite_food=pet_dict['favorite_food'],
                    habits=pet_dict['habits'],
                    rescue_difficulty=pet_dict['rescue_difficulty'],
                    required_items=pet_dict['required_items'],
                    spawn_locations=spawn_locations,
                    behavior_patterns=behavior_patterns
                )
                
                self.pets[pet_data.id] = pet_data
                
            except Exception as e:
                handle_error(e, f"parse_pet({pet_dict.get('id', 'unknown')})")
    
    def _parse_rescue_items(self, items_data: Dict[str, Any]):
        """救出アイテムデータを解析"""
        for item_id, item_dict in items_data.items():
            try:
                rescue_item = RescueItem(
                    name=item_dict['name'],
                    name_en=item_dict['name_en'],
                    description_ja=item_dict['description_ja'],
                    description_en=item_dict['description_en'],
                    effectiveness=item_dict['effectiveness']
                )
                
                self.rescue_items[item_id] = rescue_item
                
            except Exception as e:
                handle_error(e, f"parse_rescue_item({item_id})")
    
    def get_pet(self, pet_id: str) -> Optional[PetData]:
        """ペットデータを取得"""
        return self.pets.get(pet_id)
    
    def get_pets_by_species(self, species: str) -> List[PetData]:
        """種族別ペットリストを取得"""
        return [pet for pet in self.pets.values() if pet.species == species]
    
    def get_pets_by_rarity(self, rarity: str) -> List[PetData]:
        """レア度別ペットリストを取得"""
        return [pet for pet in self.pets.values() if pet.rarity == rarity]
    
    def get_rescue_item(self, item_id: str) -> Optional[RescueItem]:
        """救出アイテムを取得"""
        return self.rescue_items.get(item_id)
    
    def get_item_effectiveness(self, item_id: str, species: str) -> float:
        """アイテムの効果を取得"""
        item = self.get_rescue_item(item_id)
        if item:
            return item.effectiveness.get(species, 0.0)
        return 0.0
    
    def get_difficulty_name(self, level: int, language: str = "ja") -> str:
        """難易度名を取得"""
        difficulty = self.difficulty_levels.get(str(level), {})
        if language == "en":
            return difficulty.get('name_en', f'Level {level}')
        else:
            return difficulty.get('name', f'レベル {level}')
    
    def get_rarity_info(self, rarity: str) -> Dict[str, Any]:
        """レア度情報を取得"""
        return self.rarity_info.get(rarity, {})
    
    def get_all_pets(self) -> List[PetData]:
        """全ペットリストを取得"""
        return list(self.pets.values())
    
    def get_all_rescue_items(self) -> List[RescueItem]:
        """全救出アイテムリストを取得"""
        return list(self.rescue_items.values())
    
    def get_pet_summary(self) -> Dict[str, Any]:
        """ペットデータサマリーを取得"""
        species_count = {}
        rarity_count = {}
        
        for pet in self.pets.values():
            species_count[pet.species] = species_count.get(pet.species, 0) + 1
            rarity_count[pet.rarity] = rarity_count.get(pet.rarity, 0) + 1
        
        return {
            'total_pets': len(self.pets),
            'species_count': species_count,
            'rarity_count': rarity_count,
            'total_items': len(self.rescue_items)
        }

# グローバルペットデータローダー
_global_pet_loader = None

def get_pet_data_loader() -> PetDataLoader:
    """グローバルペットデータローダーを取得"""
    global _global_pet_loader
    if _global_pet_loader is None:
        _global_pet_loader = PetDataLoader()
        _global_pet_loader.load_pet_data()
    return _global_pet_loader
