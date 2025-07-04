"""
ゲームシーン
メインゲームプレイを管理（新マップローダー統合版）
"""

import pygame
import time
from typing import Optional, List, Dict, Any, Tuple
from src.core.scene import Scene
from src.entities.player import Player
from src.entities.pet import Pet, PetData, PetType
from src.systems.map_system import MapSystem
from src.systems.audio_system import get_audio_system
from src.systems.timer_system import TimerSystem
from src.systems.map_data_loader import get_map_data_loader
from src.systems.pet_data_loader import get_pet_data_loader
from src.ui.game_ui import GameUI, NotificationType, QuickSlotItem
from src.utils.asset_manager import get_asset_manager
from src.utils.font_manager import get_font_manager
from src.utils.language_manager import get_language_manager, get_text

class GameScene(Scene):
    """ゲームシーン"""
    
    def __init__(self, screen: pygame.Surface, flow_manager=None):
        super().__init__(screen)
        self.flow_manager = flow_manager
        
        # キー押下状態の管理
        self.e_key_pressed = False
        
        # 新しいデータローダーの初期化
        self.map_loader = get_map_data_loader()
        self.pet_data_loader = get_pet_data_loader()
        
        # リアル住宅街マップを読み込み
        if not self.map_loader.load_map('realistic_city_v1'):
            print("⚠️ リアル住宅街マップ読み込み失敗、従来マップを使用")
        else:
            print("✅ リアル住宅街マップ読み込み成功")
        
        # ゲーム要素の初期化
        self._initialize_game_elements()
        
        # ゲーム状態
        self.paused = False
        self.game_over = False
        self.victory = False
        self.pets_rescued = []
        
        # 勝利表示用
        self.victory_display_time = 0.0
        self.victory_message_shown = False
        
        # 敗北表示用
        self.defeat_display_time = 0.0
        self.defeat_message_shown = False
        
        # ゲーム制限
        self.time_limit = 180.0  # 3分制限
        self.remaining_time = self.time_limit
        self.player_lives = 3  # プレイヤーのライフ
        
        # 統計情報
        self.start_time = time.time()
        self.total_pets = len(self.pets)
    
    def _initialize_game_elements(self):
        """ゲーム要素を初期化"""
        # アセットマネージャーとフォントマネージャー
        self.asset_manager = get_asset_manager()
        self.font_manager = get_font_manager()
        self.language_manager = get_language_manager()
        
        # 背景画像の読み込み
        self.background_image = None
        self._load_background()
        
        # プレイヤー初期化
        self.player = Player(x=100, y=100)
        
        # マップシステム初期化
        self.map_system = MapSystem()
        
        # 新しいマップデータを使用してMapSystemを更新
        current_map = self.map_loader.get_current_map()
        if current_map:
            print(f"🗺️ MapSystemを新データで更新: {current_map.dimensions.width}x{current_map.dimensions.height}")
            # MapSystemに新しいサイズを設定
            self.map_system._update_from_new_map_data(current_map)
        else:
            # フォールバック: リアル住宅街マップを読み込み
            if not self.map_system.load_map("realistic_city_v1.json"):
                print("⚠️ マップファイルが見つからないため、デフォルトマップを使用します")
        
        # ペット初期化
        self.pets = self._create_pets()
        
        # パズルシステム初期化（削除済み）
        # self.puzzle_system = PuzzleSystem()
        self.current_puzzle = None
        
        # UI初期化
        self.game_ui = GameUI(self.screen)
        
        # UI画像の読み込み
        self.game_ui._load_ui_images()
        
        # UIレイアウト設定
        try:
            self.game_ui._setup_ui_layout()
            print("✅ UIレイアウト設定完了")
        except Exception as e:
            print(f"❌ UIレイアウト設定エラー: {e}")
            import traceback
            traceback.print_exc()
        
        # 音響システム初期化
        self.audio_system = get_audio_system()
        
        # タイマーシステム初期化（3分）
        self.timer_system = TimerSystem(180.0)
        self.timer_system.set_time_warning_callback(self._on_time_warning)
        self.timer_system.set_time_up_callback(self._on_time_up)
        
        # GameUIにタイマーシステムを設定
        self.game_ui.set_timer_system(self.timer_system)
        
        # カメラオフセット
        self.camera_x = 0
        self.camera_y = 0
    
    def _load_background(self):
        """背景画像を読み込み"""
        try:
            self.background_image = self.asset_manager.get_image("backgrounds/game_background.png")
            if self.background_image:
                print(f"✅ ゲーム背景画像読み込み成功: {self.background_image.get_size()}")
                # 画面サイズに合わせてスケール
                screen_size = (self.screen.get_width(), self.screen.get_height())
                self.background_image = pygame.transform.scale(self.background_image, screen_size)
                print(f"✅ ゲーム背景画像スケール完了: {screen_size}")
            else:
                print("⚠️ ゲーム背景画像が見つかりません")
        except Exception as e:
            print(f"❌ ゲーム背景画像読み込みエラー: {e}")
            self.background_image = None
    
    def _create_pets(self) -> List[Pet]:
        """ペットを作成（ランダム配置版）"""
        pets = []
        
        print("🐾 ランダム配置でペット生成中...")
        
        # 建物情報をデバッグ出力
        self._debug_building_info()
        
        # ペットデータ定義
        pet_definitions = [
            {
                "id": "dog_001",
                "name": "dog",
                "type": PetType.DOG,
                "personality": "friendly",
                "rarity": "common",
                "description": "忠実な柴犬"
            },
            {
                "id": "cat_001", 
                "name": "cat",
                "type": PetType.CAT,
                "personality": "shy",
                "rarity": "common",
                "description": "三毛猫の女の子"
            },
            {
                "id": "rabbit_001",
                "name": "rabbit",
                "type": PetType.RABBIT,
                "personality": "gentle",
                "rarity": "uncommon",
                "description": "白いうさぎ"
            },
            {
                "id": "bird_001",
                "name": "bird",
                "type": PetType.BIRD,
                "personality": "active",
                "rarity": "rare",
                "description": "カラフルな小鳥"
            }
        ]
        
        # 各ペットをランダム位置に配置（互いに離れた位置に）
        placed_positions = []
        
        for pet_def in pet_definitions:
            position = self._find_random_walkable_position(placed_positions)
            if not position:
                # フォールバック: より緩い条件で再試行
                print(f"  🔄 {pet_def['name']} のフォールバック配置を試行...")
                position = self._find_fallback_position(placed_positions)
            
            if position:
                x, y = position
                placed_positions.append((x, y))  # 配置済み位置を記録
                pet_data = PetData(
                    pet_id=pet_def["id"],
                    name=pet_def["name"],
                    pet_type=pet_def["type"],
                    personality=pet_def["personality"],
                    rarity=pet_def["rarity"],
                    description=pet_def["description"]
                )
                pet = Pet(pet_data, x=x, y=y)
                pets.append(pet)
                print(f"  🐾 {pet.data.name} ({pet.data.pet_type.value}) at ({x:.1f}, {y:.1f})")
            else:
                print(f"  ❌ {pet_def['name']} の配置場所が見つかりませんでした")
        
        print(f"✅ ランダムペット生成完了: {len(pets)}匹")
        return pets
    
    def _find_random_walkable_position(self, existing_positions: List[Tuple[float, float]] = None, max_attempts: int = 500) -> Optional[Tuple[float, float]]:
        """建物間の中央に配置する位置を見つける"""
        import random
        
        if existing_positions is None:
            existing_positions = []
        
        # マップサイズを取得
        if self.map_system.current_map:
            map_width = self.map_system.current_map.width * self.map_system.tile_size
            map_height = self.map_system.current_map.height * self.map_system.tile_size
        else:
            # デフォルトマップサイズ
            map_width = 1600  # 25 * 64
            map_height = 1280  # 20 * 64
        
        min_pet_distance = 200  # ペット同士の最小距離
        
        print(f"🔍 ペット配置場所を探索中... (マップサイズ: {map_width}x{map_height})")
        
        # 建物間のスペースを特定して配置
        building_gaps = self._find_building_gaps(map_width, map_height)
        
        for attempt in range(max_attempts):
            # 建物間のギャップから選択（優先）
            if building_gaps and attempt < max_attempts * 2 // 3:
                gap = random.choice(building_gaps)
                # ギャップの中央付近に配置
                x = gap['center_x'] + random.uniform(-gap['width']/4, gap['width']/4)
                y = gap['center_y'] + random.uniform(-gap['height']/4, gap['height']/4)
                # 境界チェック
                x = max(64, min(map_width - 64, x))
                y = max(64, min(map_height - 64, y))
            else:
                # フォールバック: 従来のランダム配置
                margin = 120
                x = random.uniform(margin, map_width - margin)
                y = random.uniform(margin, map_height - margin)
            
            # 通過可能かチェック
            if not self.map_system.is_walkable(x, y):
                if attempt % 100 == 0:  # 100回ごとにログ出力
                    print(f"  試行 {attempt}: ({x:.1f}, {y:.1f}) - 通過不可")
                continue
            
            # 建物との衝突チェック（常に実行）
            if self._is_position_blocked_by_building(x, y):
                if attempt % 100 == 0:
                    print(f"  試行 {attempt}: ({x:.1f}, {y:.1f}) - 建物と重複")
                continue
            
            # プレイヤーの初期位置から離れているかチェック
            player_x, player_y = self.player.x, self.player.y
            distance_to_player = ((x - player_x) ** 2 + (y - player_y) ** 2) ** 0.5
            min_player_distance = 150 if attempt < max_attempts // 2 else 100  # 後半は緩い条件
            if distance_to_player <= min_player_distance:
                if attempt % 100 == 0:
                    print(f"  試行 {attempt}: ({x:.1f}, {y:.1f}) - プレイヤーに近すぎる (距離: {distance_to_player:.1f})")
                continue
            
            # 他のペットから離れているかチェック
            too_close_to_other_pet = False
            current_min_distance = min_pet_distance if attempt < max_attempts // 2 else min_pet_distance // 2  # 後半は緩い条件
            for existing_x, existing_y in existing_positions:
                distance_to_pet = ((x - existing_x) ** 2 + (y - existing_y) ** 2) ** 0.5
                if distance_to_pet < current_min_distance:
                    too_close_to_other_pet = True
                    if attempt % 100 == 0:
                        print(f"  試行 {attempt}: ({x:.1f}, {y:.1f}) - 他のペットに近すぎる (距離: {distance_to_pet:.1f})")
                    break
            
            if too_close_to_other_pet:
                continue
            
            print(f"  ✅ 適切な位置発見: ({x:.1f}, {y:.1f}) - 試行回数: {attempt + 1}")
            return (x, y)
        
        print(f"⚠️ {max_attempts}回試行しても適切な位置が見つかりませんでした")
        return None
    
    def _find_fallback_position(self, existing_positions: List[Tuple[float, float]] = None, max_attempts: int = 200) -> Optional[Tuple[float, float]]:
        """フォールバック配置：建物は絶対避けるが、距離制約を緩くした配置"""
        import random
        
        if existing_positions is None:
            existing_positions = []
        
        # マップサイズを取得
        if self.map_system.current_map:
            map_width = self.map_system.current_map.width * self.map_system.tile_size
            map_height = self.map_system.current_map.height * self.map_system.tile_size
        else:
            map_width = 1600
            map_height = 1280
        
        # 緩い制約
        margin = 64  # 最小マージン
        min_pet_distance = 50  # ペット間距離を大幅に緩和
        min_player_distance = 50  # プレイヤー距離も緩和
        
        print(f"  📍 フォールバック配置: 距離制約を緩和して再試行")
        
        for attempt in range(max_attempts):
            x = random.uniform(margin, map_width - margin)
            y = random.uniform(margin, map_height - margin)
            
            # 通過可能性チェック（必須）
            if not self.map_system.is_walkable(x, y):
                continue
            
            # 建物チェック（必須 - 絶対に避ける）
            if self._is_position_blocked_by_building(x, y):
                continue
            
            # プレイヤー距離チェック（緩い）
            player_x, player_y = self.player.x, self.player.y
            distance_to_player = ((x - player_x) ** 2 + (y - player_y) ** 2) ** 0.5
            if distance_to_player <= min_player_distance:
                continue
            
            # 他のペット距離チェック（緩い）
            too_close = False
            for existing_x, existing_y in existing_positions:
                distance = ((x - existing_x) ** 2 + (y - existing_y) ** 2) ** 0.5
                if distance < min_pet_distance:
                    too_close = True
                    break
            
            if too_close:
                continue
            
            print(f"  ✅ フォールバック配置成功: ({x:.1f}, {y:.1f}) - 試行回数: {attempt + 1}")
            return (x, y)
        
        print(f"  ⚠️ フォールバック配置も失敗: {max_attempts}回試行")
        return None
    
    def _find_building_gaps(self, map_width: int, map_height: int) -> List[dict]:
        """建物間のギャップ（空きスペース）を特定する"""
        gaps = []
        
        # グリッドサイズ（建物間のスペースを検出するため）
        grid_size = 128  # 2タイル分
        
        print(f"🏠 建物間ギャップを検索中... (グリッドサイズ: {grid_size})")
        
        for y in range(128, map_height - 128, grid_size):
            for x in range(128, map_width - 128, grid_size):
                # グリッドの中心点
                center_x = x + grid_size // 2
                center_y = y + grid_size // 2
                
                # このエリアが建物間のギャップかチェック
                if self._is_building_gap(x, y, grid_size, map_width, map_height):
                    gaps.append({
                        'center_x': center_x,
                        'center_y': center_y,
                        'width': grid_size,
                        'height': grid_size,
                        'x': x,
                        'y': y
                    })
        
        print(f"  ✅ {len(gaps)}個の建物間ギャップを発見")
        return gaps
    
    def _is_building_gap(self, x: int, y: int, size: int, map_width: int, map_height: int) -> bool:
        """指定エリアが建物間のギャップ（空きスペース）かどうかチェック"""
        # エリア内の複数ポイントをチェック
        test_points = [
            (x + size//4, y + size//4),      # 左上
            (x + 3*size//4, y + size//4),    # 右上
            (x + size//4, y + 3*size//4),    # 左下
            (x + 3*size//4, y + 3*size//4),  # 右下
            (x + size//2, y + size//2),      # 中央
        ]
        
        walkable_count = 0
        for test_x, test_y in test_points:
            # 境界チェック
            if (test_x < 0 or test_x >= map_width or 
                test_y < 0 or test_y >= map_height):
                continue
                
            # 通過可能で建物に重複していないかチェック
            if (self.map_system.is_walkable(test_x, test_y) and
                not self._is_position_blocked_by_building(test_x, test_y)):
                walkable_count += 1
        
        # 5点中4点以上が通過可能ならギャップとみなす
        return walkable_count >= 4
    
    def _get_safe_placement_areas(self, map_width: int, map_height: int) -> List[dict]:
        """建物から離れた安全な配置エリアを定義"""
        safe_areas = []
        
        # マップを格子状に分割して、建物のない安全なエリアを特定
        grid_size = 150  # 150x150ピクセルのグリッド（より小さく）
        
        print(f"🛡️ 安全エリア検索中... (グリッドサイズ: {grid_size})")
        
        for y in range(100, map_height - 100, grid_size // 2):  # オーバーラップを許可
            for x in range(100, map_width - 100, grid_size // 2):
                # グリッドの中心点をチェック
                center_x = x + grid_size // 2
                center_y = y + grid_size // 2
                
                # マップ境界チェック
                if (center_x < 100 or center_x > map_width - 100 or
                    center_y < 100 or center_y > map_height - 100):
                    continue
                
                # この領域が安全かチェック
                if (self.map_system.is_walkable(center_x, center_y) and
                    not self._is_position_blocked_by_building(center_x, center_y)):
                    
                    # 複数のポイントをチェック（より緩い条件）
                    test_points = [
                        (center_x, center_y),
                        (x + 30, y + 30),
                        (x + grid_size - 30, y + 30),
                        (x + 30, y + grid_size - 30),
                        (x + grid_size - 30, y + grid_size - 30)
                    ]
                    
                    safe_points = 0
                    for test_x, test_y in test_points:
                        if (test_x >= 0 and test_x < map_width and 
                            test_y >= 0 and test_y < map_height and
                            self.map_system.is_walkable(test_x, test_y) and
                            not self._is_position_blocked_by_building(test_x, test_y)):
                            safe_points += 1
                    
                    # 5点中3点以上が安全なら採用
                    if safe_points >= 3:
                        safe_areas.append({
                            'x': x + 30,
                            'y': y + 30,
                            'width': grid_size - 60,
                            'height': grid_size - 60
                        })
        
        print(f"🛡️ 安全な配置エリア: {len(safe_areas)}個発見")
        
        # 安全エリアが少ない場合は、より緩い条件で追加
        if len(safe_areas) < 10:
            print("🔍 安全エリアが少ないため、追加検索中...")
            for y in range(200, map_height - 200, 100):
                for x in range(200, map_width - 200, 100):
                    if (self.map_system.is_walkable(x, y) and
                        not self._is_position_blocked_by_building(x, y)):
                        safe_areas.append({
                            'x': x - 50,
                            'y': y - 50,
                            'width': 100,
                            'height': 100
                        })
            print(f"🛡️ 追加検索後の安全エリア: {len(safe_areas)}個")
        
        return safe_areas
    
    def _is_position_blocked_by_building(self, x: float, y: float) -> bool:
        """位置が建物によってブロックされているかチェック"""
        # ペットのサイズを考慮したマージン（適度な距離）
        margin = 60  # ペットのサイズ + 適度な余裕
        
        # MapSystemの建物情報をチェック
        if hasattr(self.map_system, 'buildings') and self.map_system.buildings:
            for building in self.map_system.buildings:
                # 建物の位置とサイズを取得
                pos = building.get('position', {})
                size = building.get('size', {})
                
                building_x = pos.get('x', 0) * self.map_system.tile_size
                building_y = pos.get('y', 0) * self.map_system.tile_size
                building_width = size.get('width', 1) * self.map_system.tile_size
                building_height = size.get('height', 1) * self.map_system.tile_size
                
                # マージンを含めた建物の範囲をチェック
                if (building_x - margin < x < building_x + building_width + margin and
                    building_y - margin < y < building_y + building_height + margin):
                    return True
        
        # BuildingSystemの建物情報もチェック（フォールバック）
        if hasattr(self.map_system, 'building_system') and self.map_system.building_system:
            if hasattr(self.map_system.building_system, 'buildings'):
                for building in self.map_system.building_system.buildings:
                    # BuildingSystemの建物オブジェクトの場合
                    if hasattr(building, 'x') and hasattr(building, 'y'):
                        building_width = getattr(building, 'width', 64)
                        building_height = getattr(building, 'height', 64)
                        
                        if (building.x - margin < x < building.x + building_width + margin and
                            building.y - margin < y < building.y + building_height + margin):
                            return True
            
            # is_position_blocked_by_buildingメソッドも使用（より緩い条件）
            if hasattr(self.map_system.building_system, 'is_position_blocked_by_building'):
                # タイル座標に変換してチェック
                tile_x = int(x // self.map_system.tile_size)
                tile_y = int(y // self.map_system.tile_size)
                
                # 中心のタイルのみチェック（周辺タイルのチェックを削除）
                if self.map_system.building_system.is_position_blocked_by_building(tile_x, tile_y):
                    return True
        
        return False
    
    def _debug_building_info(self):
        """建物情報をデバッグ出力"""
        print("🏠 建物情報デバッグ:")
        
        # MapSystemの建物情報
        if hasattr(self.map_system, 'buildings') and self.map_system.buildings:
            print(f"  MapSystem.buildings: {len(self.map_system.buildings)}個")
            for i, building in enumerate(self.map_system.buildings[:3]):  # 最初の3個のみ表示
                pos = building.get('position', {})
                size = building.get('size', {})
                building_x = pos.get('x', 0) * self.map_system.tile_size
                building_y = pos.get('y', 0) * self.map_system.tile_size
                building_width = size.get('width', 1) * self.map_system.tile_size
                building_height = size.get('height', 1) * self.map_system.tile_size
                print(f"    建物{i}: ({building_x}, {building_y}) サイズ({building_width}x{building_height})")
        
        # BuildingSystemの建物情報
        if hasattr(self.map_system, 'building_system') and self.map_system.building_system:
            if hasattr(self.map_system.building_system, 'buildings'):
                buildings = self.map_system.building_system.buildings
                print(f"  BuildingSystem.buildings: {len(buildings)}個")
                for i, building in enumerate(buildings[:3]):  # 最初の3個のみ表示
                    if hasattr(building, 'x') and hasattr(building, 'y'):
                        width = getattr(building, 'width', 64)
                        height = getattr(building, 'height', 64)
                        print(f"    建物{i}: ({building.x}, {building.y}) サイズ({width}x{height})")
    
    
    def enter(self) -> None:
        """シーンに入る時の処理"""
        self.start_time = time.time()
        self.pets_rescued = []
        self.game_over = False
        self.victory = False
        self.paused = False
        
        # 言語マネージャーを再取得（メニューでの言語変更を反映）
        self.language_manager = get_language_manager()
        current_lang = self.language_manager.get_current_language()
        print(f"🌐 ゲーム開始時の言語: {current_lang.value}")
        
        # GameUIの言語も更新
        if hasattr(self, 'game_ui') and self.game_ui:
            self.game_ui.update_language()
        
        # 救出ペットUIをクリア
        self.game_ui.clear_rescued_pets()
        
        # タイマー開始
        self.timer_system.start()
        
        # BGM開始
        self.audio_system.play_bgm("residential_bgm")
        
        # UIに初期状態を設定
        self.game_ui.add_notification(get_text("find_pets"), NotificationType.INFO)
        self._update_ui_stats()
    
    def exit(self) -> None:
        """シーンから出る時の処理"""
        pass
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """イベント処理"""
        # テキスト入力イベントを無視（日本語入力対策）
        if event.type == pygame.TEXTINPUT:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                # Eキーが押された
                self.e_key_pressed = True
            elif event.key == pygame.K_ESCAPE:
                if self.current_puzzle:
                    # パズル中の場合はパズルを終了
                    self.current_puzzle = None
                else:
                    # ゲームを一時停止してメニューに戻る
                    return "menu"
            
            elif event.key == pygame.K_p:
                # ポーズ切り替え
                self.paused = not self.paused
                if self.paused:
                    self.timer_system.pause()
                    self.game_ui.add_notification(get_text("game_paused"), NotificationType.INFO)
                else:
                    self.timer_system.start()
                    self.game_ui.add_notification(get_text("game_resumed"), NotificationType.INFO)
            
            elif event.key == pygame.K_c:
                # デモではCキーでペット図鑑切り替えはなし
                pass
            
            elif event.key == pygame.K_F5:
                # デバッグ: 衝突判定情報を表示
                player_tile_x = int(self.player.x // 64)
                player_tile_y = int(self.player.y // 64)
                print(f"🔍 プレイヤー位置: ピクセル({self.player.x:.1f}, {self.player.y:.1f}) タイル({player_tile_x}, {player_tile_y})")
                
                # 周辺の衝突判定をチェック
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        check_x = player_tile_x + dx
                        check_y = player_tile_y + dy
                        is_blocked = self.map_system.building_system.is_position_blocked_by_building(check_x, check_y, debug=True)
                        tile_type = self.map_system.get_tile_at_position(check_x * 64, check_y * 64)
                        print(f"  タイル({check_x}, {check_y}): {'🚫' if is_blocked else '✅'} {tile_type.value if tile_type else 'None'}")
                
                self.game_ui.add_notification(get_text("collision_debug_output"), NotificationType.INFO)
            
            elif event.key == pygame.K_F6:
                # デバッグ: 衝突判定の視覚表示を切り替え
                self.map_system.debug_collision = not getattr(self.map_system, 'debug_collision', False)
                status_key = "collision_display_on" if self.map_system.debug_collision else "collision_display_off"
                self.game_ui.add_notification(get_text(status_key), NotificationType.INFO)
                print(f"🔍 衝突判定表示: {'ON' if self.map_system.debug_collision else 'OFF'}")
        
        elif event.type == pygame.KEYUP:
            if event.key == pygame.K_e:
                # Eキーが離された
                self.e_key_pressed = False
        
        elif event.type == pygame.USEREVENT + 1:
            # ゲーム完了タイマー（旧）
            if self.victory:
                return "result"
        
        elif event.type == pygame.USEREVENT + 2:
            # ゲーム勝利タイマー（新）
            if self.victory:
                print("🎉 勝利画面に移行")
                return "result"
        
        elif event.type == pygame.USEREVENT + 3:
            # ゲームクリア後メニューに戻る
            print(f"🎯 USEREVENT+3 受信: victory={self.victory}")
            if self.victory:
                print("🏠 メニューに戻ります")
                return "menu"
        
        elif event.type == pygame.USEREVENT + 4:
            # ゲーム敗北タイマー（旧）
            if self.game_over:
                print("💀 敗北画面に移行")
                return "result"
        
        elif event.type == pygame.USEREVENT + 5:
            # 敗北後メニューに戻る（新）
            if self.game_over:
                print("🏠 メニューに戻ります（敗北）")
                return "menu"
        
        # パズル中の場合はパズルUIにイベントを渡す
        if self.current_puzzle:
            # パズル機能削除済み - 何もしない
            pass
        else:
            # 通常のゲームイベント処理
            self.player.handle_event(event)
            self.game_ui.handle_input(event)
        
        return None
    
    def update(self, time_delta: float) -> Optional[str]:
        """更新処理"""
        if self.paused:
            return None
        
        # 敗北表示時間更新（game_over状態でも実行）
        if self.game_over:
            self.defeat_display_time += time_delta
            # 3秒経過したら直接メニューに戻る
            if self.defeat_display_time >= 3.0:
                print("⏰ 3秒経過によりメニューに戻ります（敗北）")
                return "menu"
            # game_over状態では他の処理をスキップ
            return None
        
        # 勝利表示時間更新
        if self.victory:
            self.victory_display_time += time_delta
            # 3秒経過したら直接メニューに戻る（フォールバック）
            if self.victory_display_time >= 3.0:
                print("⏰ 3秒経過によりメニューに戻ります")
                return "menu"
            # victory状態では他の処理をスキップ
            return None
        
        # タイマー更新
        self.timer_system.update()
        
        # 時間切れチェック
        if self.timer_system.is_finished():
            self.game_over = True
            return None
        
        # Phase 1: プレイヤー基本更新
        keys_pressed: pygame.key.ScancodeWrapper = pygame.key.get_pressed()
        self.player.update(time_delta, keys_pressed, self.map_system)
        
        # ペット更新（デモで動いていた処理を追加）
        player_pos = (self.player.x, self.player.y)
        for pet in self.pets:
            if pet.data.pet_id not in self.pets_rescued:
                pet.update(time_delta, player_pos, self.map_system)
        
        # カメラ更新
        self._update_camera()
        
        # ペットとの衝突判定
        self._check_pet_interactions()
        
        # パズル更新（削除済み）
        # if self.current_puzzle:
        #     self.puzzle_ui.update(time_delta, [])
        
        # UI更新
        self.game_ui.update(time_delta)
        self._update_ui_stats()
        
        # 時間更新
        if not self.paused and not self.victory and not self.game_over:
            self.remaining_time -= time_delta
        
        # 敗北条件チェック
        if not self.game_over and not self.victory:
            if self.timer_system.is_finished():
                self.game_over = True
                self.game_ui.add_notification(get_text("time_up"), NotificationType.ERROR)
                print("⏰ 時間切れで敗北")
                
                # 敗北表示開始
                self.defeat_display_time = 0.0
                self.defeat_message_shown = False
                
            elif self.player_lives <= 0:
                self.game_over = True
                self.game_ui.add_notification(get_text("no_lives"), NotificationType.ERROR)
                print("💔 ライフ切れで敗北")
                pygame.time.set_timer(pygame.USEREVENT + 4, 2000)  # 敗北画面へ
        
        # 勝利条件チェック（ペットが存在する場合のみ）
        if self.total_pets > 0 and len(self.pets_rescued) >= self.total_pets and not self.victory and not self.game_over:
            print(f"🎉 勝利条件達成！ 救出: {len(self.pets_rescued)}/{self.total_pets}")
            self.victory = True
            
            # タイマー停止
            self.timer_system.pause()
            
            # タイムボーナス計算
            time_bonus = self.timer_system.calculate_time_bonus()
            bonus_message = get_text("time_bonus_message").format(bonus=time_bonus)
            
            self.game_ui.add_notification(get_text("all_pets_rescued"), NotificationType.SUCCESS)
            self.game_ui.add_notification(bonus_message, NotificationType.INFO)
            print("🎉 勝利条件達成！")
            
            # 勝利BGMに変更
            self.audio_system.play_bgm("victory_bgm")
            
            # 勝利表示開始
            self.victory_display_time = 0.0
            self.victory_message_shown = False
            
            # 3秒後にメニューに戻る（無条件で設定）
            pygame.time.set_timer(pygame.USEREVENT + 3, 3000)
            print("⏰ 3秒後にメニューに戻るタイマー設定完了")
        
        return None
    
    def draw(self, surface: pygame.Surface) -> None:
        """描画処理（マップ優先版）"""
        # まず背景色でクリア
        surface.fill((50, 100, 50))  # 緑っぽい背景
        
        # マップ描画（最優先）
        self.map_system.draw(surface, self.camera_x, self.camera_y)
        
        # 背景画像は使用しない（マップが背景の役割）
        # if self.background_image:
        #     surface.blit(self.background_image, (0, 0))
        
        # ペット描画（救出済みは非表示）
        for pet in self.pets:
            if pet.data.pet_id not in self.pets_rescued and not getattr(pet, 'rescued', False):
                pet.draw(surface, (self.camera_x, self.camera_y))
        
        # プレイヤー描画
        camera_offset = (self.camera_x, self.camera_y)
        self.player.draw(surface, camera_offset)
        
        # パズルUI描画（削除済み）
        # if self.current_puzzle:
        #     self.puzzle_ui.draw()
        
        # ゲームUI描画
        player_stats = {
            'health': self.player.stats.health,
            'max_health': self.player.stats.max_health,
            'stamina': self.player.stats.stamina,
            'max_stamina': self.player.stats.max_stamina
        }
        self.game_ui.draw(player_stats, [], (self.player.x, self.player.y))
        
        # 勝利画面描画
        if self.victory:
            self._draw_victory_screen(surface)
        
        # 敗北画面描画
        elif self.game_over:
            self._draw_defeat_screen(surface)
        
        # ポーズ表示
        if self.paused:
            self._draw_pause_overlay(surface)
    
    def _update_camera(self):
        """カメラ位置を更新"""
        # プレイヤーを中心にカメラを配置
        target_x = self.player.x - self.screen.get_width() // 2
        target_y = self.player.y - self.screen.get_height() // 2
        
        # スムーズなカメラ移動
        self.camera_x += (target_x - self.camera_x) * 0.1
        self.camera_y += (target_y - self.camera_y) * 0.1
        
        # カメラ範囲制限（実際のマップサイズに基づく）
        if self.map_system and self.map_system.map_surface:
            map_width, map_height = self.map_system.map_surface.get_size()
            screen_width = self.screen.get_width()
            screen_height = self.screen.get_height()
            
            # カメラがマップの境界を超えないように制限
            max_camera_x = max(0, map_width - screen_width)
            max_camera_y = max(0, map_height - screen_height)
            
            self.camera_x = max(0, min(self.camera_x, max_camera_x))
            self.camera_y = max(0, min(self.camera_y, max_camera_y))
            
            # デバッグ情報（境界付近でのみ表示）
            if (self.camera_x <= 0 or self.camera_x >= max_camera_x or 
                self.camera_y <= 0 or self.camera_y >= max_camera_y):
                print(f"📷 カメラ境界制限: ({self.camera_x:.1f}, {self.camera_y:.1f}) - マップ: {map_width}x{map_height}")
        else:
            # フォールバック: 従来の制限
            self.camera_x = max(0, min(self.camera_x, 1000))
            self.camera_y = max(0, min(self.camera_y, 1000))
    
    def _check_pet_interactions(self):
        """ペットとの相互作用をチェック"""
        player_rect = pygame.Rect(self.player.x - 20, self.player.y - 20, 40, 40)
        
        for pet in self.pets:
            if pet.data.pet_id in self.pets_rescued:
                continue
            
            pet_rect = pygame.Rect(pet.x - 20, pet.y - 20, 40, 40)
            
            if player_rect.colliderect(pet_rect):
                # ペット発見通知（音なし）
                if not hasattr(pet, 'discovered'):
                    pet.discovered = True
                    # self.audio_system.play_sfx("pet_found", loops=0)  # 音を出さない
                    self.game_ui.add_notification(f"{pet.get_display_name()}{get_text('pet_found')}", NotificationType.INFO)
                    self.game_ui.add_notification(get_text("rescue_instruction"), NotificationType.INFO)
                
                # Eキーで救出（イベントベース）
                if self.e_key_pressed:
                    self._rescue_pet(pet)
                    self.e_key_pressed = False  # 1回だけ実行
    
    def _rescue_pet(self, pet: Pet):
        """ペットを救出（パズルなし）"""
        if pet.data.pet_id not in self.pets_rescued:
            self.pets_rescued.append(pet.data.pet_id)
            self.game_ui.add_notification(f"{pet.get_display_name()}{get_text('pet_rescued')}", NotificationType.SUCCESS)
            
            # ペットタイプを文字列に変換
            pet_type_str = str(pet.data.pet_type).lower().replace('pettype.', '')
            
            # 救出されたペットをUIに追加
            self.game_ui.add_rescued_pet(pet.get_display_name(), pet_type_str)
            
            # 短い効果音を1回のみ再生
            self.audio_system.play_sfx("pet_rescued")
            
            # ペットを非表示にする
            pet.rescued = True
    
    def _calculate_final_score(self) -> int:
        """最終スコアを計算"""
        base_score = 0
        
        # ペット救出ボーナス
        pets_rescued_count = len(self.pets_rescued)
        base_score += pets_rescued_count * 1000
        
        # 完全クリアボーナス
        if pets_rescued_count >= self.total_pets:
            base_score += 2000
        
        # タイムボーナス（新システム）
        if self.victory:
            time_bonus = self.timer_system.calculate_time_bonus()
            base_score += time_bonus
        
        # ライフボーナス
        if self.victory:
            life_bonus = self.player_lives * 50
            base_score += life_bonus
        
        # 効率ボーナス（短時間でクリア）
        elapsed_time = time.time() - self.start_time
        if self.victory and elapsed_time < 180:  # 3分以内
            base_score += 200
        
        return max(0, base_score)
    
    def get_game_result(self) -> Dict[str, Any]:
        """ゲーム結果を取得"""
        elapsed_time = time.time() - self.start_time
        final_score = self._calculate_final_score()
        
        # 敗北理由を判定
        defeat_reason = None
        if self.game_over:
            if self.timer_system.is_finished():
                defeat_reason = "time_up"
            elif self.player_lives <= 0:
                defeat_reason = "no_lives"
            else:
                defeat_reason = "other"
        
        return {
            'victory': self.victory,
            'game_over': self.game_over,
            'defeat_reason': defeat_reason,
            'pets_rescued': len(self.pets_rescued),
            'total_pets': self.total_pets,
            'time_taken': elapsed_time,
            'remaining_time': max(0, self.remaining_time),
            'player_lives': self.player_lives,
            'score': final_score,
            'completion_rate': (len(self.pets_rescued) / self.total_pets) * 100 if self.total_pets > 0 else 0
        }
    
    def _update_ui_stats(self):
        """UI統計情報を更新"""
        elapsed_time = time.time() - self.start_time
        minutes = int(elapsed_time // 60)
        seconds = int(elapsed_time % 60)
        
        # 残り時間の計算
        remaining_minutes = int(self.remaining_time // 60)
        remaining_seconds = int(self.remaining_time % 60)
        
        stats = {
            'pets_rescued': len(self.pets_rescued),
            'total_pets': self.total_pets,
            'time': f"{minutes:02d}:{seconds:02d}",
            'remaining_time': f"{remaining_minutes:02d}:{remaining_seconds:02d}",
            'lives': self.player_lives,
            'health': getattr(self.player, 'health', 100),
            'stamina': getattr(self.player, 'stamina', 100)
        }
        
        self.game_ui.update_stats(stats)
    
    def _draw_pause_overlay(self, surface: pygame.Surface):
        """ポーズオーバーレイを描画"""
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # ポーズテキスト
        font = self.font_manager.get_font("default", 48)
        pause_text = font.render(get_text("paused"), True, (255, 255, 255))
        pause_rect = pause_text.get_rect(center=(surface.get_width()//2, surface.get_height()//2))
        surface.blit(pause_text, pause_rect)
        
        # 操作説明
        help_font = self.font_manager.get_font("default", 24)
        help_text = help_font.render(get_text("pause_instructions"), True, (200, 200, 200))
        help_rect = help_text.get_rect(center=(surface.get_width()//2, surface.get_height()//2 + 60))
        surface.blit(help_text, help_rect)
    
    def _on_time_warning(self):
        """時間警告コールバック"""
        # 警告は一度だけ表示
        if not hasattr(self, '_warning_shown'):
            self.game_ui.add_notification(get_text("time_warning"), NotificationType.WARNING)
            self._warning_shown = True
            
            # 警告効果音再生
            if self.audio_system:
                self.audio_system.play_sfx("time_warning")  # 1回のみ再生
    
    def _on_time_up(self):
        """時間切れコールバック"""
        self.game_ui.add_notification(get_text("time_up") + "！", NotificationType.ERROR)
        
        # ゲームオーバー効果音再生
        if self.audio_system:
            self.audio_system.play_sfx("game_over")  # 1回のみ再生
        
        # 時間切れ処理は update() メソッドで行われる
    
    def start_game(self):
        """ゲーム開始（タイマー開始）"""
        self.timer_system.start()
        self.game_ui.add_notification(get_text("find_pets"), NotificationType.INFO)
    def _draw_victory_screen(self, surface: pygame.Surface):
        """勝利画面を描画"""
        # 半透明オーバーレイ
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # ゲームクリアテキスト
        font_large = self.font_manager.get_font('default', 72)
        font_medium = self.font_manager.get_font('default', 36)
        font_small = self.font_manager.get_font('default', 24)
        
        # メインタイトル
        clear_text = font_large.render(get_text("game_clear"), True, (255, 215, 0))  # ゴールド色
        clear_rect = clear_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 100))
        surface.blit(clear_text, clear_rect)
        
        # サブタイトル
        subtitle_text = font_medium.render(get_text("all_pets_rescued_subtitle"), True, (255, 255, 255))
        subtitle_rect = subtitle_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 40))
        surface.blit(subtitle_text, subtitle_rect)
        
        # 統計情報
        stats_y = surface.get_height() // 2 + 20
        
        # 救出ペット数
        pets_text = font_small.render(
            get_text("pets_found_count").format(count=len(self.pets_rescued), total=self.total_pets), 
            True, (255, 255, 255)
        )
        pets_rect = pets_text.get_rect(center=(surface.get_width() // 2, stats_y))
        surface.blit(pets_text, pets_rect)
        
        # 残り時間
        time_text = font_small.render(
            get_text("remaining_time_display").format(time=self.timer_system.get_time_string()), 
            True, (255, 255, 255)
        )
        time_rect = time_text.get_rect(center=(surface.get_width() // 2, stats_y + 30))
        surface.blit(time_text, time_rect)
        
        # メニューに戻る案内（2秒後に表示）
        if self.victory_display_time > 2.0:
            menu_text = font_small.render(get_text("returning_to_menu"), True, (200, 200, 200))
            menu_rect = menu_text.get_rect(center=(surface.get_width() // 2, stats_y + 80))
            surface.blit(menu_text, menu_rect)
    
    def _draw_defeat_screen(self, surface: pygame.Surface):
        """敗北画面を描画（勝利画面と同様のスタイル）"""
        # 半透明オーバーレイ
        overlay = pygame.Surface((surface.get_width(), surface.get_height()))
        overlay.set_alpha(200)
        overlay.fill((0, 0, 0))
        surface.blit(overlay, (0, 0))
        
        # フォント設定
        font_large = self.font_manager.get_font('default', 72)
        font_medium = self.font_manager.get_font('default', 36)
        font_small = self.font_manager.get_font('default', 24)
        
        # メインタイトル（時間切れ）
        defeat_text = font_large.render(get_text("time_up"), True, (255, 165, 0))  # オレンジ色
        defeat_rect = defeat_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 100))
        surface.blit(defeat_text, defeat_rect)
        
        # サブタイトル
        subtitle_text = font_medium.render(
            get_text("pets_rescued_subtitle").format(count=len(self.pets_rescued), total=self.total_pets), 
            True, (255, 255, 255)
        )
        subtitle_rect = subtitle_text.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2 - 40))
        surface.blit(subtitle_text, subtitle_rect)
        
        # 統計情報
        stats_y = surface.get_height() // 2 + 20
        
        # 救出ペット数のみ表示
        pets_text = font_small.render(
            get_text("pets_rescued_count").format(count=len(self.pets_rescued), total=self.total_pets), 
            True, (255, 255, 255)
        )
        pets_rect = pets_text.get_rect(center=(surface.get_width() // 2, stats_y))
        surface.blit(pets_text, pets_rect)
        
        # メニューに戻る案内（2秒後に表示）
        if self.defeat_display_time > 2.0:
            menu_text = font_small.render(get_text("returning_to_menu"), True, (200, 200, 200))
            menu_rect = menu_text.get_rect(center=(surface.get_width() // 2, stats_y + 50))
            surface.blit(menu_text, menu_rect)
