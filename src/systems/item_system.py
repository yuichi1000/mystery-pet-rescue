"""
アイテムシステム
アイテムの定義、管理、使用、組み合わせ機能を提供
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple, Callable
from dataclasses import dataclass, asdict
from enum import Enum

class ItemType(Enum):
    """アイテムタイプ"""
    TOOL = "tool"           # 道具
    FOOD = "food"           # 食べ物
    KEY = "key"             # 鍵
    CLUE = "clue"           # 手がかり
    CONSUMABLE = "consumable"  # 消耗品
    QUEST = "quest"         # クエストアイテム

class ItemRarity(Enum):
    """アイテムレア度"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    LEGENDARY = "legendary"

@dataclass
class ItemEffect:
    """アイテム効果"""
    effect_type: str        # 効果タイプ
    value: int             # 効果値
    duration: int = 0      # 持続時間（秒）
    target: str = "player" # 対象

@dataclass
class ItemRecipe:
    """アイテム組み合わせレシピ"""
    ingredients: List[str]  # 必要アイテムID
    result: str            # 結果アイテムID
    description: str       # 組み合わせ説明

@dataclass
class Item:
    """アイテムデータクラス"""
    id: str
    name: str
    description: str
    item_type: str
    rarity: str
    icon_path: str
    stackable: bool = True
    max_stack: int = 99
    usable: bool = True
    effects: List[ItemEffect] = None
    use_description: str = ""
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = []

@dataclass
class InventorySlot:
    """インベントリスロット"""
    item_id: Optional[str] = None
    quantity: int = 0
    
    def is_empty(self) -> bool:
        return self.item_id is None or self.quantity <= 0
    
    def can_add_item(self, item: Item, quantity: int = 1) -> bool:
        if self.is_empty():
            return True
        if self.item_id == item.id and item.stackable:
            return self.quantity + quantity <= item.max_stack
        return False
    
    def add_item(self, item: Item, quantity: int = 1) -> int:
        """アイテムを追加し、追加できなかった数を返す"""
        if self.is_empty():
            self.item_id = item.id
            self.quantity = min(quantity, item.max_stack)
            return max(0, quantity - item.max_stack)
        
        if self.item_id == item.id and item.stackable:
            can_add = item.max_stack - self.quantity
            added = min(quantity, can_add)
            self.quantity += added
            return quantity - added
        
        return quantity  # 追加できなかった
    
    def remove_item(self, quantity: int = 1) -> int:
        """アイテムを削除し、実際に削除した数を返す"""
        if self.is_empty():
            return 0
        
        removed = min(quantity, self.quantity)
        self.quantity -= removed
        
        if self.quantity <= 0:
            self.item_id = None
            self.quantity = 0
        
        return removed

class ItemSystem:
    """アイテムシステム管理クラス"""
    
    def __init__(self, items_data_path: str = "data/items_database.json"):
        self.items_data_path = items_data_path
        self.items: Dict[str, Item] = {}
        self.recipes: List[ItemRecipe] = []
        self.use_handlers: Dict[str, Callable] = {}
        
        self._load_items_database()
        self._register_default_handlers()
    
    def _load_items_database(self) -> None:
        """アイテムデータベースを読み込み"""
        try:
            with open(self.items_data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # アイテム情報を読み込み
            for item_data in data.get('items', []):
                effects = []
                for effect_data in item_data.get('effects', []):
                    effects.append(ItemEffect(**effect_data))
                
                item_data['effects'] = effects
                item = Item(**item_data)
                self.items[item.id] = item
            
            # レシピ情報を読み込み
            for recipe_data in data.get('recipes', []):
                recipe = ItemRecipe(**recipe_data)
                self.recipes.append(recipe)
                
        except FileNotFoundError:
            print(f"警告: アイテムデータベースファイルが見つかりません: {self.items_data_path}")
            self._create_default_items()
        except json.JSONDecodeError as e:
            print(f"エラー: アイテムデータベースの読み込みに失敗しました: {e}")
            self._create_default_items()
    
    def _create_default_items(self) -> None:
        """デフォルトアイテムを作成"""
        default_items = [
            Item(
                id="dog_treat",
                name="犬のおやつ",
                description="犬が大好きなおやつ。警戒心を和らげる効果がある。",
                item_type=ItemType.FOOD.value,
                rarity=ItemRarity.COMMON.value,
                icon_path="assets/images/items/dog_treat.png",
                effects=[ItemEffect("attract_dog", 1, 30)],
                use_description="犬に与えて警戒心を和らげる"
            ),
            Item(
                id="cat_toy",
                name="猫じゃらし",
                description="猫の注意を引く玩具。猫を誘導するのに使える。",
                item_type=ItemType.TOOL.value,
                rarity=ItemRarity.COMMON.value,
                icon_path="assets/images/items/cat_toy.png",
                effects=[ItemEffect("attract_cat", 1, 20)],
                use_description="猫の注意を引いて誘導する"
            ),
            Item(
                id="house_key",
                name="家の鍵",
                description="住宅街の家の鍵。特定の場所を開けることができる。",
                item_type=ItemType.KEY.value,
                rarity=ItemRarity.UNCOMMON.value,
                icon_path="assets/images/items/house_key.png",
                stackable=False,
                effects=[ItemEffect("unlock_door", 1)],
                use_description="扉を開ける"
            ),
            Item(
                id="magnifying_glass",
                name="虫眼鏡",
                description="小さな手がかりを見つけるのに役立つ道具。",
                item_type=ItemType.TOOL.value,
                rarity=ItemRarity.UNCOMMON.value,
                icon_path="assets/images/items/magnifying_glass.png",
                stackable=False,
                effects=[ItemEffect("reveal_clues", 1, 60)],
                use_description="隠れた手がかりを見つける"
            )
        ]
        
        for item in default_items:
            self.items[item.id] = item
        
        # デフォルトレシピ
        self.recipes = [
            ItemRecipe(
                ingredients=["dog_treat", "cat_toy"],
                result="pet_lure",
                description="犬のおやつと猫じゃらしを組み合わせて万能ペット誘導具を作る"
            )
        ]
    
    def _register_default_handlers(self) -> None:
        """デフォルトの使用ハンドラーを登録"""
        self.use_handlers["dog_treat"] = self._use_dog_treat
        self.use_handlers["cat_toy"] = self._use_cat_toy
        self.use_handlers["house_key"] = self._use_house_key
        self.use_handlers["magnifying_glass"] = self._use_magnifying_glass
    
    def _use_dog_treat(self, item: Item, context: Dict[str, Any]) -> bool:
        """犬のおやつ使用処理"""
        print(f"{item.name}を使用しました。近くの犬が寄ってきます。")
        # ゲーム状態に効果を適用
        if 'game_state' in context:
            context['game_state']['dog_attraction'] = True
            context['game_state']['dog_attraction_time'] = 30
        return True
    
    def _use_cat_toy(self, item: Item, context: Dict[str, Any]) -> bool:
        """猫じゃらし使用処理"""
        print(f"{item.name}を使用しました。猫の注意を引きます。")
        if 'game_state' in context:
            context['game_state']['cat_attraction'] = True
            context['game_state']['cat_attraction_time'] = 20
        return True
    
    def _use_house_key(self, item: Item, context: Dict[str, Any]) -> bool:
        """家の鍵使用処理"""
        print(f"{item.name}を使用しました。扉を開けます。")
        if 'target_door' in context:
            context['target_door']['locked'] = False
            return True
        print("使用できる扉が見つかりません。")
        return False
    
    def _use_magnifying_glass(self, item: Item, context: Dict[str, Any]) -> bool:
        """虫眼鏡使用処理"""
        print(f"{item.name}を使用しました。隠れた手がかりを探します。")
        if 'game_state' in context:
            context['game_state']['clue_detection'] = True
            context['game_state']['clue_detection_time'] = 60
        return True
    
    def get_item(self, item_id: str) -> Optional[Item]:
        """アイテム情報を取得"""
        return self.items.get(item_id)
    
    def get_all_items(self) -> List[Item]:
        """全アイテム情報を取得"""
        return list(self.items.values())
    
    def use_item(self, item_id: str, context: Dict[str, Any] = None) -> bool:
        """アイテムを使用"""
        if context is None:
            context = {}
        
        item = self.get_item(item_id)
        if not item or not item.usable:
            return False
        
        handler = self.use_handlers.get(item_id)
        if handler:
            return handler(item, context)
        
        print(f"{item.name}は使用できません。")
        return False
    
    def find_recipe(self, ingredients: List[str]) -> Optional[ItemRecipe]:
        """レシピを検索"""
        ingredients_set = set(ingredients)
        
        for recipe in self.recipes:
            recipe_ingredients = set(recipe.ingredients)
            if ingredients_set == recipe_ingredients:
                return recipe
        
        return None
    
    def can_combine_items(self, item_ids: List[str]) -> bool:
        """アイテムを組み合わせ可能かチェック"""
        return self.find_recipe(item_ids) is not None
    
    def combine_items(self, item_ids: List[str]) -> Optional[str]:
        """アイテムを組み合わせて新しいアイテムを作成"""
        recipe = self.find_recipe(item_ids)
        if recipe:
            return recipe.result
        return None
    
    def register_use_handler(self, item_id: str, handler: Callable) -> None:
        """アイテム使用ハンドラーを登録"""
        self.use_handlers[item_id] = handler
    
    def get_items_by_type(self, item_type: str) -> List[Item]:
        """タイプ別アイテム取得"""
        return [item for item in self.items.values() if item.item_type == item_type]
    
    def get_items_by_rarity(self, rarity: str) -> List[Item]:
        """レア度別アイテム取得"""
        return [item for item in self.items.values() if item.rarity == rarity]

class Inventory:
    """インベントリクラス"""
    
    def __init__(self, size: int = 20, item_system: ItemSystem = None):
        self.size = size
        self.slots: List[InventorySlot] = [InventorySlot() for _ in range(size)]
        self.item_system = item_system or ItemSystem()
    
    def add_item(self, item_id: str, quantity: int = 1) -> int:
        """アイテムを追加し、追加できなかった数を返す"""
        item = self.item_system.get_item(item_id)
        if not item:
            return quantity
        
        remaining = quantity
        
        # 既存のスタックに追加を試行
        if item.stackable:
            for slot in self.slots:
                if slot.item_id == item_id:
                    remaining = slot.add_item(item, remaining)
                    if remaining <= 0:
                        break
        
        # 空きスロットに追加
        if remaining > 0:
            for slot in self.slots:
                if slot.is_empty():
                    remaining = slot.add_item(item, remaining)
                    if remaining <= 0:
                        break
        
        return remaining
    
    def remove_item(self, item_id: str, quantity: int = 1) -> int:
        """アイテムを削除し、実際に削除した数を返す"""
        removed_total = 0
        remaining = quantity
        
        for slot in self.slots:
            if slot.item_id == item_id and remaining > 0:
                removed = slot.remove_item(remaining)
                removed_total += removed
                remaining -= removed
        
        return removed_total
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """アイテムを持っているかチェック"""
        total = 0
        for slot in self.slots:
            if slot.item_id == item_id:
                total += slot.quantity
                if total >= quantity:
                    return True
        return False
    
    def get_item_count(self, item_id: str) -> int:
        """アイテムの総数を取得"""
        total = 0
        for slot in self.slots:
            if slot.item_id == item_id:
                total += slot.quantity
        return total
    
    def get_slot(self, index: int) -> Optional[InventorySlot]:
        """スロットを取得"""
        if 0 <= index < len(self.slots):
            return self.slots[index]
        return None
    
    def move_item(self, from_index: int, to_index: int) -> bool:
        """アイテムを移動"""
        if not (0 <= from_index < len(self.slots) and 0 <= to_index < len(self.slots)):
            return False
        
        from_slot = self.slots[from_index]
        to_slot = self.slots[to_index]
        
        if from_slot.is_empty():
            return False
        
        # 移動先が空の場合
        if to_slot.is_empty():
            to_slot.item_id = from_slot.item_id
            to_slot.quantity = from_slot.quantity
            from_slot.item_id = None
            from_slot.quantity = 0
            return True
        
        # 同じアイテムでスタック可能な場合
        if from_slot.item_id == to_slot.item_id:
            item = self.item_system.get_item(from_slot.item_id)
            if item and item.stackable:
                can_add = item.max_stack - to_slot.quantity
                if can_add > 0:
                    transfer = min(from_slot.quantity, can_add)
                    to_slot.quantity += transfer
                    from_slot.quantity -= transfer
                    
                    if from_slot.quantity <= 0:
                        from_slot.item_id = None
                        from_slot.quantity = 0
                    
                    return True
        
        # アイテムを交換
        from_slot.item_id, to_slot.item_id = to_slot.item_id, from_slot.item_id
        from_slot.quantity, to_slot.quantity = to_slot.quantity, from_slot.quantity
        return True
    
    def use_item(self, slot_index: int, context: Dict[str, Any] = None) -> bool:
        """スロットのアイテムを使用"""
        slot = self.get_slot(slot_index)
        if not slot or slot.is_empty():
            return False
        
        item = self.item_system.get_item(slot.item_id)
        if not item or not item.usable:
            return False
        
        # アイテムを使用
        if self.item_system.use_item(slot.item_id, context):
            # 消耗品の場合は数量を減らす
            if item.item_type in [ItemType.CONSUMABLE.value, ItemType.FOOD.value]:
                slot.remove_item(1)
            return True
        
        return False
    
    def get_empty_slots_count(self) -> int:
        """空きスロット数を取得"""
        return sum(1 for slot in self.slots if slot.is_empty())
    
    def is_full(self) -> bool:
        """インベントリが満杯かチェック"""
        return self.get_empty_slots_count() == 0
    
    def get_all_items(self) -> List[Tuple[Item, int]]:
        """全アイテムとその数量を取得"""
        items = []
        for slot in self.slots:
            if not slot.is_empty():
                item = self.item_system.get_item(slot.item_id)
                if item:
                    items.append((item, slot.quantity))
        return items
    
    def save_to_dict(self) -> Dict[str, Any]:
        """辞書形式で保存"""
        return {
            'size': self.size,
            'slots': [asdict(slot) for slot in self.slots]
        }
    
    def load_from_dict(self, data: Dict[str, Any]) -> None:
        """辞書から読み込み"""
        self.size = data.get('size', 20)
        slots_data = data.get('slots', [])
        
        self.slots = []
        for i in range(self.size):
            if i < len(slots_data):
                slot_data = slots_data[i]
                slot = InventorySlot(
                    item_id=slot_data.get('item_id'),
                    quantity=slot_data.get('quantity', 0)
                )
            else:
                slot = InventorySlot()
            self.slots.append(slot)
