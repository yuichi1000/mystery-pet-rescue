"""
マップデータローダー
JSONファイルからマップ情報を読み込み・管理
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from src.utils.error_handler import handle_error, safe_execute

@dataclass
class MapDimensions:
    """マップサイズ"""
    width: int
    height: int
    tile_size: int

@dataclass
class Position:
    """位置情報"""
    x: int
    y: int

@dataclass
class Zone:
    """ゾーン情報"""
    name: str
    name_en: str
    bounds: Dict[str, int]
    description: str
    estimated_time: str

@dataclass
class Building:
    """建物情報"""
    id: str
    type: str
    position: Position
    size: Dict[str, int]
    name: str
    name_en: str

@dataclass
class NPC:
    """NPC情報"""
    id: str
    name: str
    name_en: str
    type: str
    position: Position
    sprite: str
    role: str
    dialogue: Dict[str, Any]
    items_to_give: List[Dict[str, Any]]
    interaction_radius: float
    movement_pattern: str

@dataclass
class PetHidingSpot:
    """ペット隠れ場所"""
    id: str
    name: str
    name_en: str
    position: Position
    type: str
    pet_id: str
    discovery_difficulty: int
    hints: List[Dict[str, str]]
    required_items: List[str]
    interaction_radius: float
    special_requirements: Optional[Dict[str, str]] = None

@dataclass
class ItemSpawn:
    """アイテム出現場所"""
    id: str
    item_id: str
    position: Position
    type: str
    respawn: bool
    hint: Dict[str, str]

@dataclass
class PuzzlePoint:
    """謎解きポイント"""
    id: str
    name: str
    name_en: str
    position: Position
    type: str
    difficulty: int
    description: Dict[str, str]
    puzzle_data: Dict[str, Any]
    reward: Dict[str, Any]
    hints: List[Dict[str, str]]

@dataclass
class InteractiveObject:
    """インタラクティブオブジェクト"""
    id: str
    type: str
    position: Position
    name: str
    name_en: str
    interactions: List[Dict[str, Any]]

@dataclass
class TutorialStep:
    """チュートリアルステップ"""
    step: int
    type: str
    instruction: Dict[str, str]
    target_position: Optional[Position] = None
    target_npc: Optional[str] = None
    target_spot: Optional[str] = None
    completion_radius: Optional[int] = None

@dataclass
class MapData:
    """マップデータ"""
    version: str
    map_id: str
    name: str
    name_en: str
    description: str
    estimated_playtime: str
    dimensions: MapDimensions
    spawn_point: Dict[str, Any]
    zones: Dict[str, Zone]
    terrain: Dict[str, Any]
    npcs: List[NPC]
    pet_hiding_spots: List[PetHidingSpot]
    items: List[ItemSpawn]
    puzzle_points: List[PuzzlePoint]
    interactive_objects: List[InteractiveObject]
    tutorial_sequence: List[TutorialStep]
    victory_conditions: Dict[str, Any]
    metadata: Dict[str, Any]

class MapDataLoader:
    """マップデータローダークラス"""
    
    def __init__(self, data_path: str = "data/maps"):
        self.data_path = Path(data_path)
        self.current_map: Optional[MapData] = None
        self.loaded_maps: Dict[str, MapData] = {}
        
        print("🗺️ マップデータローダー初期化完了")
    
    def load_map(self, map_id: str) -> bool:
        """
        マップデータを読み込み
        
        Args:
            map_id: マップID
            
        Returns:
            bool: 読み込み成功かどうか
        """
        def _load_map_safe():
            # キャッシュチェック
            if map_id in self.loaded_maps:
                self.current_map = self.loaded_maps[map_id]
                print(f"✅ マップデータ（キャッシュ）: {map_id}")
                return True
            
            data_file = self.data_path / f"{map_id}.json"
            
            if not data_file.exists():
                raise FileNotFoundError(f"マップデータファイルが見つかりません: {data_file}")
            
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # マップデータの解析
            map_data = self._parse_map_data(data)
            
            # キャッシュに保存
            self.loaded_maps[map_id] = map_data
            self.current_map = map_data
            
            print(f"✅ マップデータ読み込み完了: {map_data.name}")
            print(f"  サイズ: {map_data.dimensions.width}x{map_data.dimensions.height}")
            print(f"  NPC数: {len(map_data.npcs)}人")
            print(f"  ペット隠れ場所: {len(map_data.pet_hiding_spots)}箇所")
            print(f"  謎解きポイント: {len(map_data.puzzle_points)}箇所")
            
            return True
        
        return safe_execute(
            _load_map_safe,
            context=f"load_map(map_id={map_id})",
            default=False
        ) or False
    
    def _parse_map_data(self, data: Dict[str, Any]) -> MapData:
        """マップデータを解析"""
        # 基本情報
        dimensions = MapDimensions(
            width=data['dimensions']['width'],
            height=data['dimensions']['height'],
            tile_size=data['dimensions']['tile_size']
        )
        
        # ゾーン情報
        zones = {}
        for zone_id, zone_data in data.get('zones', {}).items():
            zones[zone_id] = Zone(
                name=zone_data['name'],
                name_en=zone_data['name_en'],
                bounds=zone_data['bounds'],
                description=zone_data['description'],
                estimated_time=zone_data['estimated_time']
            )
        
        # NPC情報
        npcs = []
        for npc_data in data.get('npcs', []):
            npc = NPC(
                id=npc_data['id'],
                name=npc_data['name'],
                name_en=npc_data['name_en'],
                type=npc_data['type'],
                position=Position(npc_data['position']['x'], npc_data['position']['y']),
                sprite=npc_data['sprite'],
                role=npc_data['role'],
                dialogue=npc_data['dialogue'],
                items_to_give=npc_data.get('items_to_give', []),
                interaction_radius=npc_data['interaction_radius'],
                movement_pattern=npc_data['movement_pattern']
            )
            npcs.append(npc)
        
        # ペット隠れ場所
        pet_hiding_spots = []
        for spot_data in data.get('pet_hiding_spots', []):
            spot = PetHidingSpot(
                id=spot_data['id'],
                name=spot_data['name'],
                name_en=spot_data['name_en'],
                position=Position(spot_data['position']['x'], spot_data['position']['y']),
                type=spot_data['type'],
                pet_id=spot_data['pet_id'],
                discovery_difficulty=spot_data['discovery_difficulty'],
                hints=spot_data['hints'],
                required_items=spot_data['required_items'],
                interaction_radius=spot_data['interaction_radius'],
                special_requirements=spot_data.get('special_requirements')
            )
            pet_hiding_spots.append(spot)
        
        # アイテム出現場所
        items = []
        for item_data in data.get('items', []):
            item = ItemSpawn(
                id=item_data['id'],
                item_id=item_data['item_id'],
                position=Position(item_data['position']['x'], item_data['position']['y']),
                type=item_data['type'],
                respawn=item_data['respawn'],
                hint=item_data['hint']
            )
            items.append(item)
        
        # 謎解きポイント
        puzzle_points = []
        for puzzle_data in data.get('puzzle_points', []):
            puzzle = PuzzlePoint(
                id=puzzle_data['id'],
                name=puzzle_data['name'],
                name_en=puzzle_data['name_en'],
                position=Position(puzzle_data['position']['x'], puzzle_data['position']['y']),
                type=puzzle_data['type'],
                difficulty=puzzle_data['difficulty'],
                description=puzzle_data['description'],
                puzzle_data=puzzle_data['puzzle_data'],
                reward=puzzle_data['reward'],
                hints=puzzle_data['hints']
            )
            puzzle_points.append(puzzle)
        
        # インタラクティブオブジェクト
        interactive_objects = []
        for obj_data in data.get('interactive_objects', []):
            obj = InteractiveObject(
                id=obj_data['id'],
                type=obj_data['type'],
                position=Position(obj_data['position']['x'], obj_data['position']['y']),
                name=obj_data['name'],
                name_en=obj_data['name_en'],
                interactions=obj_data['interactions']
            )
            interactive_objects.append(obj)
        
        # チュートリアルシーケンス
        tutorial_sequence = []
        for step_data in data.get('tutorial_sequence', []):
            target_pos = None
            if 'target_position' in step_data:
                target_pos = Position(
                    step_data['target_position']['x'],
                    step_data['target_position']['y']
                )
            
            step = TutorialStep(
                step=step_data['step'],
                type=step_data['type'],
                instruction=step_data['instruction'],
                target_position=target_pos,
                target_npc=step_data.get('target_npc'),
                target_spot=step_data.get('target_spot'),
                completion_radius=step_data.get('completion_radius')
            )
            tutorial_sequence.append(step)
        
        return MapData(
            version=data['version'],
            map_id=data['map_id'],
            name=data['name'],
            name_en=data['name_en'],
            description=data['description'],
            estimated_playtime=data['estimated_playtime'],
            dimensions=dimensions,
            spawn_point=data['spawn_point'],
            zones=zones,
            terrain=data['terrain'],
            npcs=npcs,
            pet_hiding_spots=pet_hiding_spots,
            items=items,
            puzzle_points=puzzle_points,
            interactive_objects=interactive_objects,
            tutorial_sequence=tutorial_sequence,
            victory_conditions=data['victory_conditions'],
            metadata=data['metadata']
        )
    
    def get_current_map(self) -> Optional[MapData]:
        """現在のマップデータを取得"""
        return self.current_map
    
    def get_npc_by_id(self, npc_id: str) -> Optional[NPC]:
        """NPCをIDで取得"""
        if not self.current_map:
            return None
        
        for npc in self.current_map.npcs:
            if npc.id == npc_id:
                return npc
        return None
    
    def get_hiding_spot_by_id(self, spot_id: str) -> Optional[PetHidingSpot]:
        """隠れ場所をIDで取得"""
        if not self.current_map:
            return None
        
        for spot in self.current_map.pet_hiding_spots:
            if spot.id == spot_id:
                return spot
        return None
    
    def get_puzzle_by_id(self, puzzle_id: str) -> Optional[PuzzlePoint]:
        """謎解きをIDで取得"""
        if not self.current_map:
            return None
        
        for puzzle in self.current_map.puzzle_points:
            if puzzle.id == puzzle_id:
                return puzzle
        return None
    
    def get_objects_near_position(self, x: int, y: int, radius: float) -> Dict[str, List]:
        """指定位置周辺のオブジェクトを取得"""
        if not self.current_map:
            return {}
        
        result = {
            'npcs': [],
            'hiding_spots': [],
            'items': [],
            'puzzles': [],
            'interactive_objects': []
        }
        
        # NPCs
        for npc in self.current_map.npcs:
            distance = ((npc.position.x - x) ** 2 + (npc.position.y - y) ** 2) ** 0.5
            if distance <= radius:
                result['npcs'].append(npc)
        
        # 隠れ場所
        for spot in self.current_map.pet_hiding_spots:
            distance = ((spot.position.x - x) ** 2 + (spot.position.y - y) ** 2) ** 0.5
            if distance <= radius:
                result['hiding_spots'].append(spot)
        
        # アイテム
        for item in self.current_map.items:
            distance = ((item.position.x - x) ** 2 + (item.position.y - y) ** 2) ** 0.5
            if distance <= radius:
                result['items'].append(item)
        
        # 謎解き
        for puzzle in self.current_map.puzzle_points:
            distance = ((puzzle.position.x - x) ** 2 + (puzzle.position.y - y) ** 2) ** 0.5
            if distance <= radius:
                result['puzzles'].append(puzzle)
        
        # インタラクティブオブジェクト
        for obj in self.current_map.interactive_objects:
            distance = ((obj.position.x - x) ** 2 + (obj.position.y - y) ** 2) ** 0.5
            if distance <= radius:
                result['interactive_objects'].append(obj)
        
        return result
    
    def get_map_summary(self) -> Dict[str, Any]:
        """マップサマリーを取得"""
        if not self.current_map:
            return {}
        
        return {
            'map_id': self.current_map.map_id,
            'name': self.current_map.name,
            'size': f"{self.current_map.dimensions.width}x{self.current_map.dimensions.height}",
            'estimated_playtime': self.current_map.estimated_playtime,
            'npcs': len(self.current_map.npcs),
            'pet_hiding_spots': len(self.current_map.pet_hiding_spots),
            'items': len(self.current_map.items),
            'puzzles': len(self.current_map.puzzle_points),
            'interactive_objects': len(self.current_map.interactive_objects),
            'tutorial_steps': len(self.current_map.tutorial_sequence)
        }

# グローバルマップデータローダー
_global_map_loader = None

def get_map_data_loader() -> MapDataLoader:
    """グローバルマップデータローダーを取得"""
    global _global_map_loader
    if _global_map_loader is None:
        _global_map_loader = MapDataLoader()
    return _global_map_loader
