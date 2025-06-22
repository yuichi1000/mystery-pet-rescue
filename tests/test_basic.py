"""
基本機能のテスト

ゲームの基本機能をテストする
"""

import unittest
import sys
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from config.settings import GameSettings
from config.constants import *
from src.entities.player import Player
from src.entities.pet import Pet
from src.systems.inventory import Inventory
from src.systems.save_system import SaveSystem


class TestGameSettings(unittest.TestCase):
    """ゲーム設定のテスト"""
    
    def setUp(self):
        self.settings = GameSettings()
    
    def test_default_settings(self):
        """デフォルト設定のテスト"""
        self.assertEqual(self.settings.title, GAME_TITLE)
        self.assertEqual(self.settings.screen_width, SCREEN_WIDTH)
        self.assertEqual(self.settings.screen_height, SCREEN_HEIGHT)
        self.assertEqual(self.settings.fps, TARGET_FPS)
        self.assertFalse(self.settings.debug_mode)
    
    def test_validate_settings(self):
        """設定値検証のテスト"""
        # 無効な値を設定
        self.settings.screen_width = 100
        self.settings.master_volume = 2.0
        self.settings.fps = 200
        
        # 検証実行
        self.settings.validate_settings()
        
        # 修正されているかチェック
        self.assertGreaterEqual(self.settings.screen_width, MIN_SCREEN_WIDTH)
        self.assertLessEqual(self.settings.master_volume, 1.0)
        self.assertLessEqual(self.settings.fps, MAX_FPS)


class TestPlayer(unittest.TestCase):
    """プレイヤークラスのテスト"""
    
    def setUp(self):
        self.player = Player(100, 100)
    
    def test_initial_state(self):
        """初期状態のテスト"""
        self.assertEqual(self.player.x, 100)
        self.assertEqual(self.player.y, 100)
        self.assertEqual(self.player.health, 100)
        self.assertEqual(self.player.energy, 100)
        self.assertEqual(self.player.pets_rescued, 0)
    
    def test_position_methods(self):
        """位置関連メソッドのテスト"""
        # 位置取得
        pos = self.player.get_position()
        self.assertEqual(pos, (100, 100))
        
        # 位置設定
        self.player.set_position(200, 150)
        self.assertEqual(self.player.x, 200)
        self.assertEqual(self.player.y, 150)
    
    def test_inventory_methods(self):
        """インベントリ関連メソッドのテスト"""
        # アイテム追加
        result = self.player.add_to_inventory("test_item")
        self.assertTrue(result)
        self.assertIn("test_item", self.player.inventory)
        
        # アイテム削除
        result = self.player.remove_from_inventory("test_item")
        self.assertTrue(result)
        self.assertNotIn("test_item", self.player.inventory)
    
    def test_stats_methods(self):
        """ステータス関連メソッドのテスト"""
        # 体力回復
        self.player.health = 50
        self.player.heal(30)
        self.assertEqual(self.player.health, 80)
        
        # 上限チェック
        self.player.heal(50)
        self.assertEqual(self.player.health, 100)
        
        # ペット救助
        initial_count = self.player.pets_rescued
        self.player.rescue_pet()
        self.assertEqual(self.player.pets_rescued, initial_count + 1)


class TestPet(unittest.TestCase):
    """ペットクラスのテスト"""
    
    def setUp(self):
        self.pet = Pet("dog", 50, 50, "test_dog_001")
    
    def test_initial_state(self):
        """初期状態のテスト"""
        self.assertEqual(self.pet.pet_type, "dog")
        self.assertEqual(self.pet.x, 50)
        self.assertEqual(self.pet.y, 50)
        self.assertEqual(self.pet.state, PET_STATE_LOST)
        self.assertFalse(self.pet.is_discovered)
    
    def test_interaction(self):
        """相互作用のテスト"""
        initial_trust = self.pet.trust_level
        initial_fear = self.pet.fear_level
        
        # 餌やり
        self.pet.interact_with_player("feed")
        self.assertGreater(self.pet.trust_level, initial_trust)
        self.assertLess(self.pet.fear_level, initial_fear)
    
    def test_rescue_conditions(self):
        """救助条件のテスト"""
        # 初期状態では救助不可
        self.assertFalse(self.pet.can_be_rescued())
        
        # 信頼度を上げる
        self.pet.trust_level = 80
        self.pet.fear_level = 20
        
        # 救助可能になる
        self.assertTrue(self.pet.can_be_rescued())
        
        # 救助実行
        result = self.pet.rescue()
        self.assertTrue(result)
        self.assertEqual(self.pet.state, PET_STATE_RESCUED)
    
    def test_pet_info(self):
        """ペット情報取得のテスト"""
        info = self.pet.get_info()
        
        self.assertIn("id", info)
        self.assertIn("type", info)
        self.assertIn("state", info)
        self.assertIn("trust_level", info)
        self.assertIn("owner_name", info)
        self.assertEqual(info["id"], "test_dog_001")
        self.assertEqual(info["type"], "dog")


class TestInventory(unittest.TestCase):
    """インベントリシステムのテスト"""
    
    def setUp(self):
        self.inventory = Inventory(max_slots=10)
    
    def test_add_item(self):
        """アイテム追加のテスト"""
        # 有効なアイテム追加
        result = self.inventory.add_item("dog_food", 5)
        self.assertTrue(result)
        self.assertEqual(self.inventory.get_item_count("dog_food"), 5)
        
        # 無効なアイテム追加
        result = self.inventory.add_item("invalid_item")
        self.assertFalse(result)
    
    def test_remove_item(self):
        """アイテム削除のテスト"""
        # アイテムを追加してから削除
        self.inventory.add_item("dog_food", 10)
        
        result = self.inventory.remove_item("dog_food", 3)
        self.assertTrue(result)
        self.assertEqual(self.inventory.get_item_count("dog_food"), 7)
        
        # 存在しないアイテムの削除
        result = self.inventory.remove_item("invalid_item")
        self.assertFalse(result)
    
    def test_has_item(self):
        """アイテム所持チェックのテスト"""
        self.inventory.add_item("ball", 2)
        
        self.assertTrue(self.inventory.has_item("ball"))
        self.assertTrue(self.inventory.has_item("ball", 2))
        self.assertFalse(self.inventory.has_item("ball", 3))
        self.assertFalse(self.inventory.has_item("cat_food"))
    
    def test_use_item(self):
        """アイテム使用のテスト"""
        self.inventory.add_item("energy_drink", 1)
        
        result = self.inventory.use_item("energy_drink")
        self.assertTrue(result["success"])
        self.assertIn("effects", result)
        
        # 使用後は削除される（消耗品の場合）
        self.assertFalse(self.inventory.has_item("energy_drink"))
    
    def test_inventory_limits(self):
        """インベントリ制限のテスト"""
        # スロット上限まで追加
        for i in range(10):
            self.inventory.add_item(f"item_{i}", 1)
        
        # 上限を超えた追加は失敗
        result = self.inventory.add_item("extra_item")
        self.assertFalse(result)
        
        # 満杯チェック
        self.assertTrue(self.inventory.is_full())


class TestSaveSystem(unittest.TestCase):
    """セーブシステムのテスト"""
    
    def setUp(self):
        self.settings = GameSettings()
        self.save_system = SaveSystem(self.settings)
        self.test_data = {
            "player": {
                "x": 100,
                "y": 200,
                "health": 80,
                "level": 5
            },
            "pets_rescued": 3,
            "play_time": 1800
        }
    
    def test_save_and_load(self):
        """セーブ・ロードのテスト"""
        # セーブ
        result = self.save_system.save_game(1, self.test_data)
        self.assertTrue(result)
        
        # ロード
        loaded_data = self.save_system.load_game(1)
        self.assertIsNotNone(loaded_data)
        self.assertEqual(loaded_data["player"]["x"], 100)
        self.assertEqual(loaded_data["pets_rescued"], 3)
    
    def test_invalid_slot(self):
        """無効なスロット番号のテスト"""
        # 無効なスロット番号でセーブ
        result = self.save_system.save_game(0, self.test_data)
        self.assertFalse(result)
        
        result = self.save_system.save_game(10, self.test_data)
        self.assertFalse(result)
        
        # 無効なスロット番号でロード
        data = self.save_system.load_game(0)
        self.assertIsNone(data)
    
    def test_save_info(self):
        """セーブ情報取得のテスト"""
        # セーブしてから情報取得
        self.save_system.save_game(1, self.test_data)
        
        save_info = self.save_system.get_save_info(1)
        self.assertIsNotNone(save_info)
        self.assertIn("timestamp", save_info)
        self.assertIn("play_time", save_info)
    
    def test_list_saves(self):
        """セーブ一覧取得のテスト"""
        # 複数のスロットにセーブ
        self.save_system.save_game(1, self.test_data)
        self.save_system.save_game(2, self.test_data)
        
        saves = self.save_system.list_saves()
        self.assertEqual(len(saves), 3)  # 3スロット分
        
        # スロット1と2は使用済み、3は空
        self.assertFalse(saves[0].get("empty", False))
        self.assertFalse(saves[1].get("empty", False))
        self.assertTrue(saves[2].get("empty", False))


if __name__ == "__main__":
    # テスト実行
    unittest.main(verbosity=2)
