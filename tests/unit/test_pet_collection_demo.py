#!/usr/bin/env python3
"""
ペット図鑑システムのテスト
実際の動作確認を行う
"""

import sys
import os
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.systems.pet_collection import PetCollection, PetInfo, PetRescueRecord

def test_pet_collection():
    """ペット図鑑システムのテスト"""
    print("🐾 ペット図鑑システムテスト開始")
    print("=" * 50)
    
    # ペット図鑑の初期化
    try:
        pet_collection = PetCollection()
        print("✅ ペット図鑑の初期化: 成功")
    except Exception as e:
        print(f"❌ ペット図鑑の初期化: 失敗 - {e}")
        return
    
    # 全ペット情報の取得
    all_pets = pet_collection.get_all_pets()
    print(f"📊 登録ペット数: {len(all_pets)}匹")
    
    # ペット一覧表示
    print("\n🐕 登録ペット一覧:")
    for i, pet in enumerate(all_pets, 1):
        rescued_status = "✅ 救助済み" if pet_collection.is_pet_rescued(pet.id) else "❌ 未救助"
        print(f"  {i}. {pet.name} ({pet.species} - {pet.breed}) - {rescued_status}")
        print(f"     レア度: {pet.rarity} | 難易度: {pet.rescue_difficulty}")
    
    # ペット救助のテスト
    print(f"\n🚀 ペット救助テスト:")
    test_pet_id = "dog_001"  # チョコ
    if test_pet_id in [pet.id for pet in all_pets]:
        result = pet_collection.rescue_pet(test_pet_id, "住宅街の公園", 120)
        if result:
            print(f"✅ {test_pet_id} の救助: 成功")
            record = pet_collection.get_rescue_record(test_pet_id)
            if record:
                print(f"   救助場所: {record.rescue_location}")
                print(f"   救助時間: {record.rescue_time_spent}秒")
        else:
            print(f"❌ {test_pet_id} の救助: 失敗")
    
    # 統計情報の表示
    print(f"\n📈 図鑑統計情報:")
    stats = pet_collection.get_collection_stats()
    print(f"  総ペット数: {stats['total_pets']}匹")
    print(f"  救助済み: {stats['rescued_pets']}匹")
    print(f"  完成率: {stats['completion_rate']:.1f}%")
    
    # レア度別統計
    print(f"\n🌟 レア度別統計:")
    for rarity, data in stats['rarity_stats'].items():
        rarity_info = pet_collection.get_rarity_info(rarity)
        print(f"  {rarity_info['name']}: {data['rescued']}/{data['total']} ({data['completion_rate']:.1f}%)")
    
    # 種類別統計
    print(f"\n🐾 種類別統計:")
    for species, data in stats['species_stats'].items():
        print(f"  {species}: {data['rescued']}/{data['total']} ({data['completion_rate']:.1f}%)")
    
    # 検索機能のテスト
    print(f"\n🔍 検索機能テスト:")
    search_results = pet_collection.search_pets("チワワ")
    print(f"  「チワワ」の検索結果: {len(search_results)}件")
    for pet in search_results:
        print(f"    - {pet.name} ({pet.breed})")
    
    # フィルター機能のテスト
    print(f"\n🔽 フィルター機能テスト:")
    
    # 救助済みペット
    rescued_pets = pet_collection.get_rescued_pets()
    print(f"  救助済みペット: {len(rescued_pets)}匹")
    
    # 未救助ペット
    unrescued_pets = pet_collection.get_unrescued_pets()
    print(f"  未救助ペット: {len(unrescued_pets)}匹")
    
    # レア度フィルター
    rare_pets = pet_collection.filter_pets_by_rarity("rare")
    print(f"  レアペット: {len(rare_pets)}匹")
    
    # 種類フィルター
    dogs = pet_collection.filter_pets_by_species("犬")
    print(f"  犬: {len(dogs)}匹")
    
    cats = pet_collection.filter_pets_by_species("猫")
    print(f"  猫: {len(cats)}匹")
    
    print("\n" + "=" * 50)
    print("🎉 ペット図鑑システムテスト完了")

if __name__ == "__main__":
    test_pet_collection()
