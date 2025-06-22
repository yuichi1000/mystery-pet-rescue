"""
インベントリシステム

プレイヤーのアイテム管理
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class ItemType(Enum):
    """アイテムタイプ"""
    FOOD = "food"           # ペット用食べ物
    TOY = "toy"             # ペット用おもちゃ
    TOOL = "tool"           # 道具
    KEY_ITEM = "key_item"   # 重要アイテム
    CONSUMABLE = "consumable"  # 消耗品


@dataclass
class Item:
    """アイテムクラス"""
    item_id: str
    name: str
    description: str
    item_type: ItemType
    rarity: int = 1  # 1-5 (1:コモン, 5:レジェンダリー)
    stackable: bool = True
    max_stack: int = 99
    value: int = 0
    effects: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = {}


class Inventory:
    """インベントリクラス"""
    
    def __init__(self, max_slots: int = 30):
        """
        インベントリを初期化
        
        Args:
            max_slots: 最大スロット数
        """
        self.max_slots = max_slots
        self.items: Dict[str, int] = {}  # item_id -> quantity
        self.item_database: Dict[str, Item] = {}
        
        # アイテムデータベースを初期化
        self._initialize_item_database()
    
    def _initialize_item_database(self):
        """アイテムデータベースを初期化"""
        # ペット用食べ物
        self.item_database["dog_food"] = Item(
            item_id="dog_food",
            name="ドッグフード",
            description="犬用の栄養満点フード",
            item_type=ItemType.FOOD,
            rarity=1,
            value=50,
            effects={"trust_boost": 10, "hunger_restore": 30}
        )
        
        self.item_database["cat_food"] = Item(
            item_id="cat_food",
            name="キャットフード",
            description="猫用の美味しいフード",
            item_type=ItemType.FOOD,
            rarity=1,
            value=50,
            effects={"trust_boost": 10, "hunger_restore": 30}
        )
        
        self.item_database["universal_food"] = Item(
            item_id="universal_food",
            name="万能ペットフード",
            description="どんなペットでも喜ぶ特別なフード",
            item_type=ItemType.FOOD,
            rarity=3,
            value=200,
            effects={"trust_boost": 25, "hunger_restore": 50, "fear_reduce": 15}
        )
        
        # ペット用おもちゃ
        self.item_database["ball"] = Item(
            item_id="ball",
            name="ボール",
            description="ペットが喜ぶカラフルなボール",
            item_type=ItemType.TOY,
            rarity=1,
            value=30,
            effects={"trust_boost": 15, "fear_reduce": 10}
        )
        
        self.item_database["feather_toy"] = Item(
            item_id="feather_toy",
            name="羽根のおもちゃ",
            description="猫が夢中になる羽根のおもちゃ",
            item_type=ItemType.TOY,
            rarity=2,
            value=80,
            effects={"trust_boost": 20, "fear_reduce": 15}
        )
        
        # 道具
        self.item_database["pet_carrier"] = Item(
            item_id="pet_carrier",
            name="ペットキャリー",
            description="ペットを安全に運ぶためのキャリー",
            item_type=ItemType.TOOL,
            rarity=2,
            stackable=False,
            max_stack=1,
            value=500,
            effects={"rescue_success_rate": 20}
        )
        
        self.item_database["flashlight"] = Item(
            item_id="flashlight",
            name="懐中電灯",
            description="暗い場所でペットを探すのに便利",
            item_type=ItemType.TOOL,
            rarity=1,
            stackable=False,
            max_stack=1,
            value=100,
            effects={"search_range": 50}
        )
        
        # 重要アイテム
        self.item_database["pet_license"] = Item(
            item_id="pet_license",
            name="ペット救助許可証",
            description="正式なペット救助活動の許可証",
            item_type=ItemType.KEY_ITEM,
            rarity=4,
            stackable=False,
            max_stack=1,
            value=0,
            effects={"official_rescuer": True}
        )
        
        # 消耗品
        self.item_database["energy_drink"] = Item(
            item_id="energy_drink",
            name="エナジードリンク",
            description="疲労回復に効果的な飲み物",
            item_type=ItemType.CONSUMABLE,
            rarity=1,
            value=100,
            effects={"energy_restore": 50}
        )
    
    def add_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        アイテムを追加
        
        Args:
            item_id: アイテムID
            quantity: 数量
            
        Returns:
            追加成功時True
        """
        if item_id not in self.item_database:
            print(f"未知のアイテム: {item_id}")
            return False
        
        item = self.item_database[item_id]
        
        # スロット数チェック
        if item_id not in self.items and len(self.items) >= self.max_slots:
            print("インベントリが満杯です")
            return False
        
        # スタック可能チェック
        if item.stackable:
            current_quantity = self.items.get(item_id, 0)
            new_quantity = current_quantity + quantity
            
            if new_quantity > item.max_stack:
                # スタック上限を超える場合
                quantity = item.max_stack - current_quantity
                if quantity <= 0:
                    print(f"{item.name}はこれ以上持てません")
                    return False
            
            self.items[item_id] = current_quantity + quantity
        else:
            # スタック不可の場合
            if item_id in self.items:
                print(f"{item.name}は既に持っています")
                return False
            self.items[item_id] = 1
        
        print(f"{item.name} x{quantity} を入手しました")
        return True
    
    def remove_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        アイテムを削除
        
        Args:
            item_id: アイテムID
            quantity: 数量
            
        Returns:
            削除成功時True
        """
        if item_id not in self.items:
            return False
        
        current_quantity = self.items[item_id]
        if current_quantity < quantity:
            return False
        
        new_quantity = current_quantity - quantity
        if new_quantity <= 0:
            del self.items[item_id]
        else:
            self.items[item_id] = new_quantity
        
        return True
    
    def has_item(self, item_id: str, quantity: int = 1) -> bool:
        """
        アイテムを持っているかチェック
        
        Args:
            item_id: アイテムID
            quantity: 必要数量
            
        Returns:
            持っている場合True
        """
        return self.items.get(item_id, 0) >= quantity
    
    def get_item_count(self, item_id: str) -> int:
        """
        アイテムの所持数を取得
        
        Args:
            item_id: アイテムID
            
        Returns:
            所持数
        """
        return self.items.get(item_id, 0)
    
    def get_item_info(self, item_id: str) -> Optional[Item]:
        """
        アイテム情報を取得
        
        Args:
            item_id: アイテムID
            
        Returns:
            アイテム情報（存在しない場合はNone）
        """
        return self.item_database.get(item_id)
    
    def get_items_by_type(self, item_type: ItemType) -> List[str]:
        """
        指定タイプのアイテムIDリストを取得
        
        Args:
            item_type: アイテムタイプ
            
        Returns:
            アイテムIDのリスト
        """
        result = []
        for item_id in self.items:
            item = self.item_database.get(item_id)
            if item and item.item_type == item_type:
                result.append(item_id)
        return result
    
    def use_item(self, item_id: str, target=None) -> Dict[str, Any]:
        """
        アイテムを使用
        
        Args:
            item_id: アイテムID
            target: 使用対象（ペット、プレイヤーなど）
            
        Returns:
            使用効果の辞書
        """
        if not self.has_item(item_id):
            return {"success": False, "message": "アイテムを持っていません"}
        
        item = self.get_item_info(item_id)
        if not item:
            return {"success": False, "message": "無効なアイテムです"}
        
        # アイテムタイプに応じた処理
        if item.item_type == ItemType.CONSUMABLE:
            # 消耗品は使用後に削除
            self.remove_item(item_id, 1)
        
        return {
            "success": True,
            "message": f"{item.name}を使用しました",
            "effects": item.effects.copy()
        }
    
    def get_inventory_summary(self) -> Dict[str, Any]:
        """
        インベントリの概要を取得
        
        Returns:
            インベントリ概要
        """
        total_items = sum(self.items.values())
        total_value = 0
        
        for item_id, quantity in self.items.items():
            item = self.get_item_info(item_id)
            if item:
                total_value += item.value * quantity
        
        return {
            "total_items": total_items,
            "unique_items": len(self.items),
            "total_value": total_value,
            "slots_used": len(self.items),
            "max_slots": self.max_slots,
            "slots_free": self.max_slots - len(self.items)
        }
    
    def get_all_items(self) -> List[Dict[str, Any]]:
        """
        全アイテムの詳細情報を取得
        
        Returns:
            アイテム詳細情報のリスト
        """
        result = []
        
        for item_id, quantity in self.items.items():
            item = self.get_item_info(item_id)
            if item:
                result.append({
                    "item_id": item_id,
                    "name": item.name,
                    "description": item.description,
                    "type": item.item_type.value,
                    "rarity": item.rarity,
                    "quantity": quantity,
                    "value": item.value,
                    "total_value": item.value * quantity
                })
        
        # レアリティと名前でソート
        result.sort(key=lambda x: (-x["rarity"], x["name"]))
        return result
    
    def clear_inventory(self):
        """インベントリをクリア"""
        self.items.clear()
    
    def is_full(self) -> bool:
        """インベントリが満杯かチェック"""
        return len(self.items) >= self.max_slots
