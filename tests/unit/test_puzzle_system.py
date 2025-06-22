"""
謎解きシステムのテスト
"""

import pytest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock

from src.systems.puzzle_system import PuzzleSystem, PuzzleState, PuzzleProgress
from src.systems.hint_system import HintSystem

class TestPuzzleSystem:
    """謎解きシステムのテスト"""
    
    @pytest.fixture
    def sample_puzzle_data(self):
        """サンプル謎解きデータ"""
        return {
            "puzzles": {
                "test_puzzle": {
                    "id": "test_puzzle",
                    "title": "テスト謎解き",
                    "description": "テスト用の謎解きです",
                    "difficulty": "easy",
                    "required_items": ["item1", "item2"],
                    "stages": [
                        {
                            "stage": 1,
                            "description": "ステージ1",
                            "required_items": ["item1"],
                            "hint": "アイテム1が必要です",
                            "completed": False
                        }
                    ],
                    "combinations": [
                        {
                            "items": ["item1", "item2"],
                            "result": "test_result",
                            "description": "テスト結果",
                            "success_message": "成功しました！"
                        }
                    ],
                    "hints": ["ヒント1", "ヒント2"],
                    "success_condition": {
                        "type": "all_stages_complete",
                        "required_combinations": ["test_result"]
                    }
                }
            },
            "difficulty_settings": {
                "easy": {
                    "max_hints": 3,
                    "hint_cooldown": 30
                }
            }
        }
    
    @pytest.fixture
    def temp_puzzle_file(self, sample_puzzle_data):
        """一時的な謎解きファイル"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(sample_puzzle_data, f)
            temp_file = f.name
        
        yield temp_file
        
        # クリーンアップ
        os.unlink(temp_file)
    
    @pytest.fixture
    def puzzle_system(self, temp_puzzle_file):
        """謎解きシステムインスタンス"""
        return PuzzleSystem(temp_puzzle_file)
    
    def test_load_puzzles_data(self, puzzle_system):
        """謎解きデータ読み込みテスト"""
        assert len(puzzle_system.puzzles_data['puzzles']) == 1
        assert 'test_puzzle' in puzzle_system.puzzles_data['puzzles']
    
    def test_start_puzzle(self, puzzle_system):
        """謎解き開始テスト"""
        result = puzzle_system.start_puzzle('test_puzzle')
        assert result is True
        assert 'test_puzzle' in puzzle_system.active_puzzles
        assert puzzle_system.active_puzzles['test_puzzle'].state == PuzzleState.IN_PROGRESS
    
    def test_start_nonexistent_puzzle(self, puzzle_system):
        """存在しない謎解き開始テスト"""
        result = puzzle_system.start_puzzle('nonexistent')
        assert result is False
        assert 'nonexistent' not in puzzle_system.active_puzzles
    
    def test_check_item_combination_success(self, puzzle_system):
        """アイテム組み合わせ成功テスト"""
        puzzle_system.start_puzzle('test_puzzle')
        
        success, result, message = puzzle_system.check_item_combination('test_puzzle', ['item1', 'item2'])
        assert success is True
        assert result == 'test_result'
        assert 'test_result' in puzzle_system.active_puzzles['test_puzzle'].discovered_combinations
    
    def test_check_item_combination_failure(self, puzzle_system):
        """アイテム組み合わせ失敗テスト"""
        puzzle_system.start_puzzle('test_puzzle')
        
        success, result, message = puzzle_system.check_item_combination('test_puzzle', ['wrong1', 'wrong2'])
        assert success is False
        assert result == ''
        assert ['wrong1', 'wrong2'] in puzzle_system.active_puzzles['test_puzzle'].failed_attempts
    
    def test_get_hint(self, puzzle_system):
        """ヒント取得テスト"""
        puzzle_system.start_puzzle('test_puzzle')
        
        hint = puzzle_system.get_hint('test_puzzle')
        assert hint == 'ヒント1'
        assert puzzle_system.active_puzzles['test_puzzle'].used_hints == 1
        
        # 2回目のヒント
        hint2 = puzzle_system.get_hint('test_puzzle')
        assert hint2 == 'ヒント2'
        assert puzzle_system.active_puzzles['test_puzzle'].used_hints == 2
    
    def test_puzzle_status(self, puzzle_system):
        """謎解き状況取得テスト"""
        puzzle_system.start_puzzle('test_puzzle')
        
        status = puzzle_system.get_puzzle_status('test_puzzle')
        assert status['puzzle_id'] == 'test_puzzle'
        assert status['title'] == 'テスト謎解き'
        assert status['state'] == 'in_progress'
        assert status['current_stage'] == 1
    
    def test_reset_puzzle(self, puzzle_system):
        """謎解きリセットテスト"""
        puzzle_system.start_puzzle('test_puzzle')
        assert 'test_puzzle' in puzzle_system.active_puzzles
        
        result = puzzle_system.reset_puzzle('test_puzzle')
        assert result is True
        assert 'test_puzzle' not in puzzle_system.active_puzzles

class TestHintSystem:
    """ヒントシステムのテスト"""
    
    @pytest.fixture
    def puzzle_system_mock(self):
        """モックされた謎解きシステム"""
        mock_system = MagicMock()
        mock_system.puzzles_data = {
            'difficulty_settings': {
                'easy': {
                    'hint_cooldown': 0,  # テスト用にクールダウンなし
                    'max_hints': 3
                }
            }
        }
        mock_system.get_puzzle_data.return_value = {
            'difficulty': 'easy',
            'hints': ['ヒント1', 'ヒント2'],
            'required_items': ['item1', 'item2'],
            'combinations': [
                {
                    'items': ['item1', 'item2'],
                    'result': 'test_result'
                }
            ]
        }
        
        # モックプログレス
        mock_progress = MagicMock()
        mock_progress.used_hints = 0
        mock_progress.attempts = 1
        mock_system.active_puzzles = {'test_puzzle': mock_progress}
        
        return mock_system
    
    @pytest.fixture
    def hint_system(self, puzzle_system_mock):
        """ヒントシステムインスタンス"""
        return HintSystem(puzzle_system_mock)
    
    def test_get_contextual_hint(self, hint_system, puzzle_system_mock):
        """コンテキストヒント取得テスト"""
        hint = hint_system.get_contextual_hint('test_puzzle', ['item1'], [])
        assert hint is not None
        assert isinstance(hint, str)
    
    def test_hint_cooldown(self, hint_system, puzzle_system_mock):
        """ヒントクールダウンテスト"""
        # クールダウンを設定
        puzzle_system_mock.puzzles_data['difficulty_settings']['easy']['hint_cooldown'] = 60
        
        # 最初のヒント
        hint1 = hint_system.get_contextual_hint('test_puzzle', ['item1'], [])
        assert hint1 is not None
        
        # すぐに2回目のヒント（クールダウン中）
        hint2 = hint_system.get_contextual_hint('test_puzzle', ['item1'], [])
        assert 'ヒントは' in hint2 and '秒後に利用可能' in hint2
    
    def test_should_show_auto_hint(self, hint_system, puzzle_system_mock):
        """自動ヒント表示判定テスト"""
        # 試行回数が少ない場合
        puzzle_system_mock.active_puzzles['test_puzzle'].attempts = 3
        assert hint_system.should_show_auto_hint('test_puzzle') is False
        
        # 試行回数が多い場合
        puzzle_system_mock.active_puzzles['test_puzzle'].attempts = 10
        assert hint_system.should_show_auto_hint('test_puzzle') is True

def test_puzzle_integration():
    """謎解きシステム統合テスト"""
    # 実際のデータファイルを使用した統合テスト
    puzzle_system = PuzzleSystem("data/puzzles_database.json")
    
    # データが正常に読み込まれているかチェック
    puzzles = puzzle_system.get_available_puzzles()
    assert len(puzzles) > 0
    
    # 最初の謎解きを開始
    first_puzzle = puzzles[0]
    result = puzzle_system.start_puzzle(first_puzzle['id'])
    assert result is True
    
    # 状況確認
    status = puzzle_system.get_puzzle_status(first_puzzle['id'])
    assert status['state'] == 'in_progress'
