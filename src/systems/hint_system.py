"""
ヒントシステム
段階的なヒント表示と管理
"""

import time
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class HintType(Enum):
    """ヒントタイプ"""
    GENERAL = "general"          # 一般的なヒント
    ITEM_SPECIFIC = "item_specific"  # アイテム固有のヒント
    COMBINATION = "combination"   # 組み合わせヒント
    LOCATION = "location"        # 場所のヒント
    PROGRESSIVE = "progressive"   # 段階的ヒント

@dataclass
class HintData:
    """ヒントデータ"""
    hint_id: str
    content: str
    hint_type: HintType
    difficulty_level: int  # 1-5 (1が最も簡単)
    prerequisites: List[str]  # 前提条件
    cooldown: float = 0.0  # クールダウン時間（秒）
    usage_count: int = 0   # 使用回数
    last_used: float = 0.0 # 最後に使用した時間

class HintSystem:
    """ヒントシステム管理クラス"""
    
    def __init__(self, puzzle_system):
        self.puzzle_system = puzzle_system
        self.hint_history: Dict[str, List[str]] = {}  # puzzle_id -> hint_ids
        self.hint_cooldowns: Dict[str, float] = {}    # puzzle_id -> last_hint_time
        self.auto_hint_triggers: Dict[str, int] = {}  # puzzle_id -> failed_attempts
        
    def get_contextual_hint(self, puzzle_id: str, player_items: List[str], 
                          failed_attempts: List[List[str]]) -> Optional[str]:
        """
        コンテキストに応じたヒントを生成
        
        Args:
            puzzle_id: 謎解きID
            player_items: プレイヤーが持っているアイテム
            failed_attempts: 失敗した組み合わせ履歴
        """
        puzzle_data = self.puzzle_system.get_puzzle_data(puzzle_id)
        if not puzzle_data:
            return None
        
        progress = self.puzzle_system.active_puzzles.get(puzzle_id)
        if not progress:
            return None
        
        # 難易度設定を取得
        difficulty = puzzle_data.get('difficulty', 'normal')
        difficulty_settings = self.puzzle_system.puzzles_data.get('difficulty_settings', {}).get(difficulty, {})
        
        # クールダウンチェック
        cooldown = difficulty_settings.get('hint_cooldown', 60)
        last_hint_time = self.hint_cooldowns.get(puzzle_id, 0)
        if time.time() - last_hint_time < cooldown:
            remaining = int(cooldown - (time.time() - last_hint_time))
            return f"ヒントは{remaining}秒後に利用可能になります"
        
        # ヒント生成
        hint = self._generate_smart_hint(puzzle_id, player_items, failed_attempts, progress)
        
        if hint:
            self.hint_cooldowns[puzzle_id] = time.time()
            
            # ヒント履歴に追加
            if puzzle_id not in self.hint_history:
                self.hint_history[puzzle_id] = []
            self.hint_history[puzzle_id].append(hint)
        
        return hint
    
    def _generate_smart_hint(self, puzzle_id: str, player_items: List[str], 
                           failed_attempts: List[List[str]], progress) -> Optional[str]:
        """スマートヒント生成"""
        puzzle_data = self.puzzle_system.get_puzzle_data(puzzle_id)
        
        # 1. 現在のステージに基づくヒント
        stages = puzzle_data.get('stages', [])
        current_stage_data = None
        for stage in stages:
            if stage['stage'] == progress.current_stage:
                current_stage_data = stage
                break
        
        if current_stage_data:
            required_items = current_stage_data['required_items']
            missing_items = [item for item in required_items if item not in player_items]
            
            if missing_items:
                return f"ステージ{progress.current_stage}には次のアイテムが必要です: {', '.join(missing_items)}"
        
        # 2. 失敗した組み合わせに基づくヒント
        if failed_attempts:
            recent_attempt = failed_attempts[-1]
            hint = self._analyze_failed_attempt(puzzle_id, recent_attempt, player_items)
            if hint:
                return hint
        
        # 3. 進行状況に基づくヒント
        if progress.attempts > 5:
            return self._get_progressive_hint(puzzle_id, progress.attempts)
        
        # 4. 一般的なヒント
        hints = puzzle_data.get('hints', [])
        if progress.used_hints < len(hints):
            return hints[progress.used_hints]
        
        return "すべてのヒントを使い切りました。アイテムの組み合わせを試してみましょう"
    
    def _analyze_failed_attempt(self, puzzle_id: str, failed_items: List[str], 
                              player_items: List[str]) -> Optional[str]:
        """失敗した組み合わせを分析してヒントを生成"""
        puzzle_data = self.puzzle_system.get_puzzle_data(puzzle_id)
        combinations = puzzle_data.get('combinations', [])
        
        # 正解の組み合わせと比較
        for combination in combinations:
            correct_items = set(combination['items'])
            attempted_items = set(failed_items)
            
            # 部分的に正しい場合
            intersection = correct_items.intersection(attempted_items)
            if len(intersection) > 0:
                missing = correct_items - attempted_items
                extra = attempted_items - correct_items
                
                if missing and not extra:
                    return f"良い組み合わせです！あと{', '.join(missing)}が必要かもしれません"
                elif extra and not missing:
                    return f"{', '.join(extra)}は必要ないかもしれません"
                elif missing and extra:
                    return f"{', '.join(extra)}の代わりに{', '.join(missing)}を試してみましょう"
        
        # アイテムカテゴリーに基づくヒント
        return self._get_category_hint(puzzle_id, failed_items)
    
    def _get_category_hint(self, puzzle_id: str, items: List[str]) -> Optional[str]:
        """アイテムカテゴリーに基づくヒント"""
        puzzle_data = self.puzzle_system.get_puzzle_data(puzzle_id)
        item_categories = self.puzzle_system.puzzles_data.get('item_categories', {})
        
        # 使用したアイテムのカテゴリーを分析
        used_categories = set()
        for item in items:
            for category, category_items in item_categories.items():
                if item in category_items:
                    used_categories.add(category)
        
        # 必要なカテゴリーを確認
        required_items = puzzle_data.get('required_items', [])
        required_categories = set()
        for item in required_items:
            for category, category_items in item_categories.items():
                if item in category_items:
                    required_categories.add(category)
        
        missing_categories = required_categories - used_categories
        if missing_categories:
            category_names = {
                'tools': '道具',
                'evidence': '証拠',
                'consumables': '消耗品',
                'keys': '鍵',
                'documents': '書類'
            }
            missing_names = [category_names.get(cat, cat) for cat in missing_categories]
            return f"他のカテゴリーのアイテムも必要かもしれません: {', '.join(missing_names)}"
        
        return None
    
    def _get_progressive_hint(self, puzzle_id: str, attempt_count: int) -> str:
        """段階的ヒント"""
        if attempt_count <= 3:
            return "アイテムを2つ以上組み合わせてみましょう"
        elif attempt_count <= 6:
            return "謎解きの説明文をもう一度読んでみましょう"
        elif attempt_count <= 10:
            return "必要なアイテムがすべて揃っているか確認してみましょう"
        else:
            return "一度リセットして、最初から考え直してみるのも良いかもしれません"
    
    def should_show_auto_hint(self, puzzle_id: str) -> bool:
        """自動ヒント表示の判定"""
        puzzle_data = self.puzzle_system.get_puzzle_data(puzzle_id)
        if not puzzle_data:
            return False
        
        progress = self.puzzle_system.active_puzzles.get(puzzle_id)
        if not progress:
            return False
        
        difficulty = puzzle_data.get('difficulty', 'normal')
        difficulty_settings = self.puzzle_system.puzzles_data.get('difficulty_settings', {}).get(difficulty, {})
        auto_hint_threshold = difficulty_settings.get('auto_hint_threshold', 5)
        
        return progress.attempts >= auto_hint_threshold
    
    def get_hint_status(self, puzzle_id: str) -> Dict[str, any]:
        """ヒント使用状況を取得"""
        puzzle_data = self.puzzle_system.get_puzzle_data(puzzle_id)
        progress = self.puzzle_system.active_puzzles.get(puzzle_id)
        
        if not puzzle_data or not progress:
            return {}
        
        difficulty = puzzle_data.get('difficulty', 'normal')
        difficulty_settings = self.puzzle_system.puzzles_data.get('difficulty_settings', {}).get(difficulty, {})
        
        max_hints = difficulty_settings.get('max_hints', 3)
        cooldown = difficulty_settings.get('hint_cooldown', 60)
        last_hint_time = self.hint_cooldowns.get(puzzle_id, 0)
        remaining_cooldown = max(0, cooldown - (time.time() - last_hint_time))
        
        return {
            'used_hints': progress.used_hints,
            'max_hints': max_hints,
            'remaining_hints': max_hints - progress.used_hints,
            'cooldown_remaining': remaining_cooldown,
            'can_use_hint': remaining_cooldown == 0 and progress.used_hints < max_hints,
            'auto_hint_available': self.should_show_auto_hint(puzzle_id)
        }
    
    def get_hint_history(self, puzzle_id: str) -> List[str]:
        """ヒント履歴を取得"""
        return self.hint_history.get(puzzle_id, [])
    
    def clear_hint_history(self, puzzle_id: str):
        """ヒント履歴をクリア"""
        if puzzle_id in self.hint_history:
            del self.hint_history[puzzle_id]
        if puzzle_id in self.hint_cooldowns:
            del self.hint_cooldowns[puzzle_id]
        if puzzle_id in self.auto_hint_triggers:
            del self.auto_hint_triggers[puzzle_id]
