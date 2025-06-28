"""
ペットデータローダー（簡素化版）
JSONファイルからペット情報を読み込み・管理
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

@dataclass
class PetInfo:
    """簡素化されたペット情報"""
    id: str
    name: str
    species: str
    description: str
    rarity: str
    image_path: str
    habitat: str
    personality: str
    favorite_food: str

class PetDataLoader:
    """ペットデータローダー（簡素化版）"""
    
    def __init__(self, data_path: str = "data"):
        """
        ペットデータローダーを初期化
        
        Args:
            data_path: データファイルのパス
        """
        self.data_path = Path(data_path)
        self.pets: Dict[str, PetInfo] = {}
        
        # 初期化時に自動読み込み
        self.load_pet_data()
        
        print("📋 ペットデータローダー初期化完了")
    
    def load_pet_data(self, version: str = "v1") -> bool:
        """
        ペットデータを読み込み
        
        Args:
            version: データバージョン
            
        Returns:
            bool: 読み込み成功かどうか
        """
        try:
            # 実際のファイル名を使用
            data_file = self.data_path / "pets_database.json"
            
            if not data_file.exists():
                print(f"⚠️ ペットデータファイルが見つかりません: {data_file}")
                # フォールバック: 基本ペットデータを作成
                self._create_fallback_pets()
                return True
            
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # ペットデータの解析
            self._parse_pets(data.get('pets', []))
            
            print(f"✅ ペットデータ読み込み完了: {len(self.pets)}匹のペット")
            
            return True
            
        except Exception as e:
            print(f"⚠️ ペットデータ読み込みエラー: {e}")
            # フォールバック: 基本ペットデータを作成
            self._create_fallback_pets()
            return False
    
    def _parse_pets(self, pets_data: List[Dict[str, Any]]):
        """ペットデータを解析（簡素化版）"""
        for pet_dict in pets_data:
            try:
                # 簡素化されたペットデータ構造
                pet_info = PetInfo(
                    id=pet_dict['id'],
                    name=pet_dict['name'],
                    species=pet_dict['species'],
                    description=pet_dict['description'],
                    rarity=pet_dict.get('rarity', 'common'),
                    image_path=pet_dict.get('image_path', ''),
                    habitat=pet_dict.get('habitat', ''),
                    personality=pet_dict.get('personality', 'friendly'),
                    favorite_food=pet_dict.get('favorite_food', '')
                )
                
                self.pets[pet_info.id] = pet_info
                print(f"🐾 ペット登録: {pet_info.name} ({pet_info.species})")
                
            except KeyError as e:
                print(f"⚠️ ペットデータ解析エラー: 必須フィールド不足 {e}")
            except Exception as e:
                print(f"⚠️ ペットデータ解析エラー: {e}")
    
    def _create_fallback_pets(self):
        """フォールバック用の基本ペットデータを作成"""
        fallback_pets = [
            {
                "id": "pet_cat_001",
                "name": "ミケ",
                "species": "三毛猫",
                "description": "人懐っこい三毛猫",
                "rarity": "common",
                "image_path": "assets/images/pets/cat_001.png",
                "habitat": "住宅街",
                "personality": "好奇心旺盛",
                "favorite_food": "魚"
            },
            {
                "id": "pet_dog_001", 
                "name": "ポチ",
                "species": "柴犬",
                "description": "忠実な柴犬",
                "rarity": "common",
                "image_path": "assets/images/pets/dog_001.png",
                "habitat": "住宅街",
                "personality": "忠実",
                "favorite_food": "肉"
            },
            {
                "id": "pet_rabbit_001",
                "name": "ミミ", 
                "species": "うさぎ",
                "description": "白いうさぎ",
                "rarity": "uncommon",
                "image_path": "assets/images/pets/rabbit_001.png",
                "habitat": "住宅街",
                "personality": "おとなしい",
                "favorite_food": "にんじん"
            },
            {
                "id": "pet_bird_001",
                "name": "ピーちゃん",
                "species": "小鳥", 
                "description": "カラフルな小鳥",
                "rarity": "rare",
                "image_path": "assets/images/pets/bird_001.png",
                "habitat": "住宅街",
                "personality": "活発",
                "favorite_food": "種"
            }
        ]
        
        print("🔄 フォールバックペットデータを作成中...")
        for pet_data in fallback_pets:
            pet_info = PetInfo(
                id=pet_data['id'],
                name=pet_data['name'],
                species=pet_data['species'],
                description=pet_data['description'],
                rarity=pet_data['rarity'],
                image_path=pet_data['image_path'],
                habitat=pet_data['habitat'],
                personality=pet_data['personality'],
                favorite_food=pet_data['favorite_food']
            )
            self.pets[pet_info.id] = pet_info
            print(f"🐾 フォールバックペット登録: {pet_info.name} ({pet_info.species})")
    
    def get_pet(self, pet_id: str) -> Optional[PetInfo]:
        """ペット情報を取得"""
        return self.pets.get(pet_id)
    
    def get_all_pets(self) -> Dict[str, PetInfo]:
        """全ペット情報を取得"""
        return self.pets.copy()

# グローバルインスタンス
_pet_data_loader: Optional[PetDataLoader] = None

def get_pet_data_loader() -> PetDataLoader:
    """PetDataLoaderのシングルトンインスタンスを取得"""
    global _pet_data_loader
    if _pet_data_loader is None:
        _pet_data_loader = PetDataLoader()
    return _pet_data_loader
