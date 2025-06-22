"""
謎解きシステム
アイテム組み合わせによる謎解きゲームの管理
"""

import json
import time
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

class PuzzleDifficulty(Enum):
    """謎解き難易度"""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"

class PuzzleState(Enum):
    """謎解き状態"""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

@dataclass
class PuzzleStage:
    """謎解きステージ"""
    stage: int
    description: str
    required_items: List[str]
    hint: str
    completed: bool = False

@dataclass
class ItemCombination:
    """アイテム組み合わせ"""
    items: List[str]
    result: str
    description: str
    success_message: str

@dataclass
class PuzzleProgress:
    """謎解き進行状況"""
    puzzle_id: str
    state: PuzzleState = PuzzleState.NOT_STARTED
    current_stage: int = 1
    completed_stages: List[int] = field(default_factory=list)
    used_hints: int = 0
    attempts: int = 0
    start_time: float = 0.0
    completion_time: Optional[float] = None
    discovered_combinations: List[str] = field(default_factory=list)
    failed_attempts: List[List[str]] = field(default_factory=list)

class PuzzleSystem:
    """謎解きシステム管理クラス"""
    
    def __init__(self, data_file: str = "data/puzzles_database.json"):
        self.data_file = data_file
        self.puzzles_data: Dict = {}
        self.active_puzzles: Dict[str, PuzzleProgress] = {}
        self.load_puzzles_data()
    
    def load_puzzles_data(self) -> bool:
        """謎解きデータを読み込み"""
        try:
            with open(self.data_file, 'r', encoding='utf-8') as f:
                self.puzzles_data = json.load(f)
            print(f"✅ 謎解きデータ読み込み完了: {len(self.puzzles_data.get('puzzles', {}))}個")
            return True
        except FileNotFoundError:
            print(f"❌ 謎解きデータファイルが見つかりません: {self.data_file}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ 謎解きデータの解析エラー: {e}")
            return False
    
    def get_puzzle_data(self, puzzle_id: str) -> Optional[Dict]:
        """謎解きデータを取得"""
        return self.puzzles_data.get('puzzles', {}).get(puzzle_id)
    
    def start_puzzle(self, puzzle_id: str) -> bool:
        """謎解きを開始"""
        puzzle_data = self.get_puzzle_data(puzzle_id)
        if not puzzle_data:
            print(f"❌ 謎解きが見つかりません: {puzzle_id}")
            return False
        
        if puzzle_id in self.active_puzzles:
            print(f"⚠️ 謎解きは既に開始されています: {puzzle_id}")
            return False
        
        progress = PuzzleProgress(
            puzzle_id=puzzle_id,
            state=PuzzleState.IN_PROGRESS,
            start_time=time.time()
        )
        
        self.active_puzzles[puzzle_id] = progress
        print(f"🧩 謎解き開始: {puzzle_data['title']}")
        return True
    
    def check_item_combination(self, puzzle_id: str, items: List[str]) -> Tuple[bool, str, str]:
        """
        アイテム組み合わせをチェック
        
        Returns:
            (成功フラグ, 結果名, メッセージ)
        """
        puzzle_data = self.get_puzzle_data(puzzle_id)
        if not puzzle_data:
            return False, "", "謎解きデータが見つかりません"
        
        progress = self.active_puzzles.get(puzzle_id)
        if not progress:
            return False, "", "謎解きが開始されていません"
        
        progress.attempts += 1
        
        # アイテムをソートして比較
        sorted_items = sorted(items)
        
        # 組み合わせをチェック
        for combination in puzzle_data.get('combinations', []):
            if sorted(combination['items']) == sorted_items:
                result_name = combination['result']
                
                # 既に発見済みかチェック
                if result_name not in progress.discovered_combinations:
                    progress.discovered_combinations.append(result_name)
                    print(f"✅ 新しい組み合わせ発見: {result_name}")
                    return True, result_name, combination['success_message']
                else:
                    return True, result_name, "この組み合わせは既に発見済みです"
        
        # 失敗した組み合わせを記録
        progress.failed_attempts.append(items.copy())
        return False, "", "この組み合わせでは何も起こりませんでした"
    
    def check_stage_completion(self, puzzle_id: str, available_items: List[str]) -> bool:
        """ステージ完了条件をチェック"""
        puzzle_data = self.get_puzzle_data(puzzle_id)
        progress = self.active_puzzles.get(puzzle_id)
        
        if not puzzle_data or not progress:
            return False
        
        stages = puzzle_data.get('stages', [])
        current_stage_data = None
        
        for stage in stages:
            if stage['stage'] == progress.current_stage:
                current_stage_data = stage
                break
        
        if not current_stage_data:
            return False
        
        # 必要アイテムがすべて揃っているかチェック
        required_items = current_stage_data['required_items']
        if all(item in available_items for item in required_items):
            # ステージ完了
            if progress.current_stage not in progress.completed_stages:
                progress.completed_stages.append(progress.current_stage)
                print(f"🎯 ステージ{progress.current_stage}完了!")
            
            # 次のステージに進む
            if progress.current_stage < len(stages):
                progress.current_stage += 1
            
            return True
        
        return False
    
    def check_puzzle_completion(self, puzzle_id: str) -> bool:
        """謎解き完了条件をチェック"""
        puzzle_data = self.get_puzzle_data(puzzle_id)
        progress = self.active_puzzles.get(puzzle_id)
        
        if not puzzle_data or not progress:
            return False
        
        success_condition = puzzle_data.get('success_condition', {})
        condition_type = success_condition.get('type')
        
        if condition_type == 'all_stages_complete':
            # すべてのステージが完了している
            total_stages = len(puzzle_data.get('stages', []))
            stages_completed = len(progress.completed_stages) >= total_stages
            
            # 必要な組み合わせも発見している
            required_combinations = success_condition.get('required_combinations', [])
            combinations_found = all(
                combo in progress.discovered_combinations 
                for combo in required_combinations
            )
            
            if stages_completed and combinations_found:
                self._complete_puzzle(puzzle_id)
                return True
        
        elif condition_type == 'specific_combination':
            # 特定の組み合わせが発見されている
            required_combinations = success_condition.get('required_combinations', [])
            if all(combo in progress.discovered_combinations for combo in required_combinations):
                self._complete_puzzle(puzzle_id)
                return True
        
        return False
    
    def _complete_puzzle(self, puzzle_id: str):
        """謎解き完了処理"""
        progress = self.active_puzzles.get(puzzle_id)
        if progress:
            progress.state = PuzzleState.COMPLETED
            progress.completion_time = time.time()
            
            puzzle_data = self.get_puzzle_data(puzzle_id)
            if puzzle_data:
                print(f"🎉 謎解き完了: {puzzle_data['title']}")
                
                # 報酬情報を表示
                rewards = puzzle_data.get('rewards', {})
                if rewards.get('experience'):
                    print(f"💫 経験値: {rewards['experience']}")
                if rewards.get('items'):
                    print(f"🎁 獲得アイテム: {', '.join(rewards['items'])}")
    
    def get_hint(self, puzzle_id: str) -> Optional[str]:
        """ヒントを取得"""
        puzzle_data = self.get_puzzle_data(puzzle_id)
        progress = self.active_puzzles.get(puzzle_id)
        
        if not puzzle_data or not progress:
            return None
        
        # 難易度設定を確認
        difficulty = puzzle_data.get('difficulty', 'normal')
        difficulty_settings = self.puzzles_data.get('difficulty_settings', {}).get(difficulty, {})
        max_hints = difficulty_settings.get('max_hints', 3)
        
        if progress.used_hints >= max_hints:
            return "これ以上ヒントは使用できません"
        
        hints = puzzle_data.get('hints', [])
        if progress.used_hints < len(hints):
            hint = hints[progress.used_hints]
            progress.used_hints += 1
            print(f"💡 ヒント{progress.used_hints}: {hint}")
            return hint
        
        return "利用可能なヒントがありません"
    
    def get_puzzle_status(self, puzzle_id: str) -> Dict[str, Any]:
        """謎解き状況を取得"""
        puzzle_data = self.get_puzzle_data(puzzle_id)
        progress = self.active_puzzles.get(puzzle_id)
        
        if not puzzle_data:
            return {"error": "謎解きが見つかりません"}
        
        status = {
            "puzzle_id": puzzle_id,
            "title": puzzle_data['title'],
            "description": puzzle_data['description'],
            "difficulty": puzzle_data['difficulty'],
            "state": progress.state.value if progress else PuzzleState.NOT_STARTED.value,
        }
        
        if progress:
            status.update({
                "current_stage": progress.current_stage,
                "completed_stages": progress.completed_stages,
                "used_hints": progress.used_hints,
                "attempts": progress.attempts,
                "discovered_combinations": progress.discovered_combinations,
                "elapsed_time": time.time() - progress.start_time if progress.start_time else 0
            })
        
        return status
    
    def get_available_puzzles(self) -> List[Dict[str, str]]:
        """利用可能な謎解き一覧を取得"""
        puzzles = []
        for puzzle_id, puzzle_data in self.puzzles_data.get('puzzles', {}).items():
            puzzles.append({
                "id": puzzle_id,
                "title": puzzle_data['title'],
                "description": puzzle_data['description'],
                "difficulty": puzzle_data['difficulty'],
                "category": puzzle_data.get('category', 'general')
            })
        return puzzles
    
    def reset_puzzle(self, puzzle_id: str) -> bool:
        """謎解きをリセット"""
        if puzzle_id in self.active_puzzles:
            del self.active_puzzles[puzzle_id]
            print(f"🔄 謎解きリセット: {puzzle_id}")
            return True
        return False
    
    def save_progress(self, save_file: str = "saves/puzzle_progress.json") -> bool:
        """進行状況を保存"""
        try:
            # PuzzleProgressをシリアライズ可能な形式に変換
            serializable_progress = {}
            for puzzle_id, progress in self.active_puzzles.items():
                serializable_progress[puzzle_id] = {
                    "puzzle_id": progress.puzzle_id,
                    "state": progress.state.value,
                    "current_stage": progress.current_stage,
                    "completed_stages": progress.completed_stages,
                    "used_hints": progress.used_hints,
                    "attempts": progress.attempts,
                    "start_time": progress.start_time,
                    "completion_time": progress.completion_time,
                    "discovered_combinations": progress.discovered_combinations,
                    "failed_attempts": progress.failed_attempts
                }
            
            # ディレクトリ作成
            Path(save_file).parent.mkdir(parents=True, exist_ok=True)
            
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_progress, f, ensure_ascii=False, indent=2)
            
            print(f"💾 謎解き進行状況保存完了: {save_file}")
            return True
        except Exception as e:
            print(f"❌ 保存エラー: {e}")
            return False
    
    def load_progress(self, save_file: str = "saves/puzzle_progress.json") -> bool:
        """進行状況を読み込み"""
        try:
            with open(save_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # データをPuzzleProgressオブジェクトに変換
            self.active_puzzles = {}
            for puzzle_id, progress_data in data.items():
                progress = PuzzleProgress(
                    puzzle_id=progress_data['puzzle_id'],
                    state=PuzzleState(progress_data['state']),
                    current_stage=progress_data['current_stage'],
                    completed_stages=progress_data['completed_stages'],
                    used_hints=progress_data['used_hints'],
                    attempts=progress_data['attempts'],
                    start_time=progress_data['start_time'],
                    completion_time=progress_data.get('completion_time'),
                    discovered_combinations=progress_data['discovered_combinations'],
                    failed_attempts=progress_data['failed_attempts']
                )
                self.active_puzzles[puzzle_id] = progress
            
            print(f"📂 謎解き進行状況読み込み完了: {len(self.active_puzzles)}個")
            return True
        except FileNotFoundError:
            print("💾 保存ファイルが見つかりません（新規開始）")
            return True
        except Exception as e:
            print(f"❌ 読み込みエラー: {e}")
            return False
