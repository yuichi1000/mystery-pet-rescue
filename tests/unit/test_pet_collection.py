"""
ペット図鑑システムの単体テスト
"""

import pytest
import json
import os
import tempfile
from datetime import datetime
from unittest.mock import patch, mock_open

from src.systems.pet_collection import PetCollection, PetInfo, PetRescueRecord

class TestPetCollection:
    """ペット図鑑システムのテストクラス"""
    
    @pytest.fixture
    def sample_pets_data(self):
        """テスト用のペットデータ"""
        return {
            "pets": [
                {
                    "id": "test_dog_001",
                    "name": "テストドッグ",
                    "species": "犬",
                    "breed": "テスト犬種",
                    "description": "テスト用の犬です",
                    "characteristics": ["テスト特徴1", "テスト特徴2"],
                    "rarity": "common",
                    "image_path": "test/path.png",
                    "found_locations": ["テスト場所1", "テスト場所2"],
                    "rescue_difficulty": 1,
                    "rescue_hints": ["テストヒント1", "テストヒント2"]
                }
            ],
            "rarity_info": {
                "common": {
                    "name": "コモン",
                    "color": "#4CAF50",
                    "description": "よく見かけるペット"
                }
            }
        }
    
    @pytest.fixture
    def temp_files(self):
        """一時ファイルを作成"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as data_file, \
             tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as save_file:
            
            yield data_file.name, save_file.name
            
            # クリーンアップ
            try:
                os.unlink(data_file.name)
                os.unlink(save_file.name)
            except FileNotFoundError:
                pass
    
    def test_pet_info_creation(self):
        """PetInfoデータクラスのテスト"""
        pet_info = PetInfo(
            id="test_001",
            name="テストペット",
            species="犬",
            breed="テスト犬種",
            description="テスト説明",
            characteristics=["特徴1", "特徴2"],
            rarity="common",
            image_path="test.png",
            found_locations=["場所1"],
            rescue_difficulty=1,
            rescue_hints=["ヒント1"]
        )
        
        assert pet_info.id == "test_001"
        assert pet_info.name == "テストペット"
        assert pet_info.species == "犬"
        assert len(pet_info.characteristics) == 2
    
    def test_pet_rescue_record_creation(self):
        """PetRescueRecordデータクラスのテスト"""
        record = PetRescueRecord(pet_id="test_001")
        
        assert record.pet_id == "test_001"
        assert record.rescued is False
        assert record.rescue_date is None
        assert record.rescue_attempts == 0
    
    def test_pet_collection_initialization(self, sample_pets_data, temp_files):
        """PetCollectionの初期化テスト"""
        data_file, save_file = temp_files
        
        # テストデータを書き込み
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(sample_pets_data, f)
        
        # PetCollectionを初期化
        collection = PetCollection(data_path=data_file, save_path=save_file)
        
        assert len(collection.pets_data) == 1
        assert "test_dog_001" in collection.pets_data
        assert collection.pets_data["test_dog_001"].name == "テストドッグ"
    
    def test_pet_rescue(self, sample_pets_data, temp_files):
        """ペット救助機能のテスト"""
        data_file, save_file = temp_files
        
        # テストデータを書き込み
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(sample_pets_data, f)
        
        collection = PetCollection(data_path=data_file, save_path=save_file)
        
        # ペットを救助
        success = collection.rescue_pet("test_dog_001", "テスト公園", 30)
        
        assert success is True
        assert collection.is_pet_rescued("test_dog_001") is True
        
        # 救助記録を確認
        record = collection.get_rescue_record("test_dog_001")
        assert record is not None
        assert record.rescued is True
        assert record.rescue_location == "テスト公園"
        assert record.rescue_time_spent == 30
        assert record.rescue_attempts == 1
    
    def test_pet_filtering(self, sample_pets_data, temp_files):
        """ペットフィルタリング機能のテスト"""
        # 複数のペットデータを追加
        sample_pets_data["pets"].append({
            "id": "test_cat_001",
            "name": "テストキャット",
            "species": "猫",
            "breed": "テスト猫種",
            "description": "テスト用の猫です",
            "characteristics": ["テスト特徴"],
            "rarity": "rare",
            "image_path": "test/cat.png",
            "found_locations": ["テスト場所"],
            "rescue_difficulty": 2,
            "rescue_hints": ["テストヒント"]
        })
        
        data_file, save_file = temp_files
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(sample_pets_data, f)
        
        collection = PetCollection(data_path=data_file, save_path=save_file)
        
        # 種類別フィルター
        dogs = collection.filter_pets_by_species("犬")
        cats = collection.filter_pets_by_species("猫")
        
        assert len(dogs) == 1
        assert len(cats) == 1
        assert dogs[0].name == "テストドッグ"
        assert cats[0].name == "テストキャット"
        
        # レア度別フィルター
        common_pets = collection.filter_pets_by_rarity("common")
        rare_pets = collection.filter_pets_by_rarity("rare")
        
        assert len(common_pets) == 1
        assert len(rare_pets) == 1
    
    def test_pet_search(self, sample_pets_data, temp_files):
        """ペット検索機能のテスト"""
        data_file, save_file = temp_files
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(sample_pets_data, f)
        
        collection = PetCollection(data_path=data_file, save_path=save_file)
        
        # 名前で検索
        results = collection.search_pets("テストドッグ")
        assert len(results) == 1
        assert results[0].name == "テストドッグ"
        
        # 種類で検索
        results = collection.search_pets("犬")
        assert len(results) == 1
        
        # 特徴で検索
        results = collection.search_pets("テスト特徴1")
        assert len(results) == 1
        
        # 見つからない場合
        results = collection.search_pets("存在しないペット")
        assert len(results) == 0
    
    def test_collection_stats(self, sample_pets_data, temp_files):
        """図鑑統計機能のテスト"""
        data_file, save_file = temp_files
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(sample_pets_data, f)
        
        collection = PetCollection(data_path=data_file, save_path=save_file)
        
        # 初期状態の統計
        stats = collection.get_collection_stats()
        assert stats['total_pets'] == 1
        assert stats['rescued_pets'] == 0
        assert stats['completion_rate'] == 0.0
        
        # ペットを救助後の統計
        collection.rescue_pet("test_dog_001", "テスト場所", 30)
        stats = collection.get_collection_stats()
        assert stats['rescued_pets'] == 1
        assert stats['completion_rate'] == 100.0
    
    def test_save_and_load_rescue_records(self, sample_pets_data, temp_files):
        """救助記録の保存・読み込みテスト"""
        data_file, save_file = temp_files
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(sample_pets_data, f)
        
        # 最初のコレクション
        collection1 = PetCollection(data_path=data_file, save_path=save_file)
        collection1.rescue_pet("test_dog_001", "テスト場所", 30)
        
        # 新しいコレクションで同じファイルを読み込み
        collection2 = PetCollection(data_path=data_file, save_path=save_file)
        
        # 救助記録が保持されているかチェック
        assert collection2.is_pet_rescued("test_dog_001") is True
        record = collection2.get_rescue_record("test_dog_001")
        assert record.rescue_location == "テスト場所"
        assert record.rescue_time_spent == 30
    
    def test_invalid_pet_rescue(self, sample_pets_data, temp_files):
        """存在しないペットの救助テスト"""
        data_file, save_file = temp_files
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(sample_pets_data, f)
        
        collection = PetCollection(data_path=data_file, save_path=save_file)
        
        # 存在しないペットIDで救助を試行
        success = collection.rescue_pet("invalid_pet_id", "テスト場所", 30)
        assert success is False
    
    def test_rarity_info(self, sample_pets_data, temp_files):
        """レア度情報取得のテスト"""
        data_file, save_file = temp_files
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(sample_pets_data, f)
        
        collection = PetCollection(data_path=data_file, save_path=save_file)
        
        # 存在するレア度
        rarity_info = collection.get_rarity_info("common")
        assert rarity_info['name'] == "コモン"
        assert rarity_info['color'] == "#4CAF50"
        
        # 存在しないレア度
        rarity_info = collection.get_rarity_info("unknown")
        assert rarity_info['name'] == "Unknown"
        assert rarity_info['color'] == "#666666"
