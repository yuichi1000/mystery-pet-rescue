"""
インベントリシステムの単体テスト
"""

import pytest
import sys
from pathlib import Path

# プロジェクトルートをPythonパスに追加
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.systems.item_system import (
    Item, ItemEffect, ItemRecipe, InventorySlot, 
    Inventory, ItemSystem, ItemType, ItemRarity
)

class TestItem:
    """アイテムクラスのテスト"""
    
    def test_item_creation(self):
        """アイテム作成テスト"""
        effect = ItemEffect("heal", 50, 10, "player")
        item = Item(
            id="potion",
            name="回復ポーション",
            description="HPを回復する",
            item_type=ItemType.CONSUMABLE.value,
            rarity=ItemRarity.COMMON.value,
            icon_path="test.png",
            effects=[effect]
        )
        
        assert item.id == "potion"
        assert item.name == "回復ポーション"
        assert len(item.effects) == 1
        assert item.effects[0].effect_type == "heal"

class TestInventorySlot:
    """インベントリスロットのテスト"""
    
    def test_empty_slot(self):
        """空スロットテスト"""
        slot = InventorySlot()
        assert slot.is_empty()
        assert slot.item_id is None
        assert slot.quantity == 0
    
    def test_add_item_to_empty_slot(self):
        """空スロットへのアイテム追加"""
        slot = InventorySlot()
        item = Item("test", "テスト", "説明", "tool", "common", "test.png")
        
        remaining = slot.add_item(item, 5)
        assert remaining == 0
        assert slot.item_id == "test"
        assert slot.quantity == 5
    
    def test_stack_items(self):
        """アイテムスタック"""
        slot = InventorySlot()
        item = Item("test", "テスト", "説明", "tool", "common", "test.png", 
                   stackable=True, max_stack=10)
        
        # 最初の追加
        remaining = slot.add_item(item, 3)
        assert remaining == 0
        assert slot.quantity == 3
        
        # 追加スタック
        remaining = slot.add_item(item, 4)
        assert remaining == 0
        assert slot.quantity == 7
        
        # 最大スタック超過
        remaining = slot.add_item(item, 5)
        assert remaining == 2  # 3個は追加できない
        assert slot.quantity == 10
    
    def test_remove_item(self):
        """アイテム削除"""
        slot = InventorySlot()
        item = Item("test", "テスト", "説明", "tool", "common", "test.png")
        
        slot.add_item(item, 5)
        
        # 一部削除
        removed = slot.remove_item(2)
        assert removed == 2
        assert slot.quantity == 3
        
        # 全削除
        removed = slot.remove_item(5)
        assert removed == 3
        assert slot.is_empty()

class TestInventory:
    """インベントリクラスのテスト"""
    
    def test_inventory_creation(self):
        """インベントリ作成テスト"""
        inventory = Inventory(size=10)
        assert len(inventory.slots) == 10
        assert inventory.get_empty_slots_count() == 10
        assert inventory.is_full() == False
    
    def test_add_item(self):
        """アイテム追加テスト"""
        item_system = ItemSystem()
        inventory = Inventory(size=5, item_system=item_system)
        
        # テスト用アイテムを追加
        remaining = inventory.add_item("dog_treat", 3)
        assert remaining == 0
        assert inventory.has_item("dog_treat", 3)
        assert inventory.get_item_count("dog_treat") == 3
    
    def test_remove_item(self):
        """アイテム削除テスト"""
        item_system = ItemSystem()
        inventory = Inventory(size=5, item_system=item_system)
        
        inventory.add_item("dog_treat", 5)
        
        removed = inventory.remove_item("dog_treat", 2)
        assert removed == 2
        assert inventory.get_item_count("dog_treat") == 3
    
    def test_move_item(self):
        """アイテム移動テスト"""
        item_system = ItemSystem()
        inventory = Inventory(size=5, item_system=item_system)
        
        inventory.add_item("dog_treat", 3)
        inventory.add_item("cat_toy", 2)
        
        # アイテム移動
        success = inventory.move_item(0, 2)
        assert success == True
        
        # 移動後の確認
        slot_0 = inventory.get_slot(0)
        slot_2 = inventory.get_slot(2)
        assert slot_0.item_id == "cat_toy"
        assert slot_2.item_id == "dog_treat"

class TestItemSystem:
    """アイテムシステムのテスト"""
    
    def test_item_system_creation(self):
        """アイテムシステム作成テスト"""
        item_system = ItemSystem()
        assert len(item_system.items) > 0
        assert len(item_system.recipes) > 0
    
    def test_get_item(self):
        """アイテム取得テスト"""
        item_system = ItemSystem()
        item = item_system.get_item("dog_treat")
        assert item is not None
        assert item.name == "犬のおやつ"
    
    def test_find_recipe(self):
        """レシピ検索テスト"""
        item_system = ItemSystem()
        recipe = item_system.find_recipe(["dog_treat", "cat_toy"])
        assert recipe is not None
        assert recipe.result == "pet_lure"
    
    def test_combine_items(self):
        """アイテム組み合わせテスト"""
        item_system = ItemSystem()
        result = item_system.combine_items(["dog_treat", "cat_toy"])
        assert result == "pet_lure"
        
        # 存在しない組み合わせ
        result = item_system.combine_items(["dog_treat", "house_key"])
        assert result is None
    
    def test_use_item(self):
        """アイテム使用テスト"""
        item_system = ItemSystem()
        context = {"game_state": {}}
        
        success = item_system.use_item("dog_treat", context)
        assert success == True
        assert context["game_state"]["dog_attraction"] == True

class TestIntegration:
    """統合テスト"""
    
    def test_full_inventory_workflow(self):
        """完全なインベントリワークフローテスト"""
        item_system = ItemSystem()
        inventory = Inventory(size=10, item_system=item_system)
        
        # アイテム追加
        inventory.add_item("dog_treat", 2)
        inventory.add_item("cat_toy", 1)
        
        # 組み合わせ材料があることを確認
        assert inventory.has_item("dog_treat", 1)
        assert inventory.has_item("cat_toy", 1)
        
        # 組み合わせ可能かチェック
        can_combine = item_system.can_combine_items(["dog_treat", "cat_toy"])
        assert can_combine == True
        
        # 材料を削除
        inventory.remove_item("dog_treat", 1)
        inventory.remove_item("cat_toy", 1)
        
        # 結果アイテムを追加
        inventory.add_item("pet_lure", 1)
        
        # 結果確認
        assert inventory.has_item("pet_lure", 1)
        assert inventory.get_item_count("dog_treat") == 1  # 1個残っている
    
    def test_inventory_save_load(self):
        """インベントリ保存・読み込みテスト"""
        item_system = ItemSystem()
        inventory = Inventory(size=5, item_system=item_system)
        
        # アイテム追加
        inventory.add_item("dog_treat", 3)
        inventory.add_item("house_key", 1)
        
        # 保存
        save_data = inventory.save_to_dict()
        
        # 新しいインベントリに読み込み
        new_inventory = Inventory(size=5, item_system=item_system)
        new_inventory.load_from_dict(save_data)
        
        # 確認
        assert new_inventory.has_item("dog_treat", 3)
        assert new_inventory.has_item("house_key", 1)
