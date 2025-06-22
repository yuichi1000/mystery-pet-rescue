# API統合ガイドライン

## Beatoven.ai API 統合

### 環境設定
1. **.env ファイルの作成**
```bash
# プロジェクトルートに .env ファイルを作成
BEATOVEN_API_KEY=your_api_key_here
BEATOVEN_API_URL=https://api.beatoven.ai/v1
BEATOVEN_TIMEOUT=30
```

2. **requirements.txt への追加**
```
python-dotenv==1.0.0
requests==2.31.0
```

### 実装例
```python
# src/utils/audio_generator.py
import os
import requests
from dotenv import load_dotenv
from typing import Optional, Dict, Any

load_dotenv()

class BeatovenAudioGenerator:
    """Beatoven.ai を使用した音楽・効果音生成"""
    
    def __init__(self):
        self.api_key = os.getenv('BEATOVEN_API_KEY')
        self.api_url = os.getenv('BEATOVEN_API_URL', 'https://api.beatoven.ai/v1')
        self.timeout = int(os.getenv('BEATOVEN_TIMEOUT', '30'))
        
        if not self.api_key:
            raise ValueError("BEATOVEN_API_KEY が設定されていません。.env ファイルを確認してください。")
    
    def generate_bgm(self, scene_type: str, mood: str, duration: int = 60) -> Optional[bytes]:
        """
        シーンに応じたBGMを生成
        
        Args:
            scene_type: シーンタイプ（residential, forest, puzzle等）
            mood: 雰囲気（happy, mysterious, tense等）
            duration: 長さ（秒）
            
        Returns:
            生成された音楽データ（バイナリ）
        """
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'style': self._map_scene_to_style(scene_type),
            'mood': mood,
            'duration': duration,
            'format': 'mp3'
        }
        
        try:
            response = requests.post(
                f"{self.api_url}/generate",
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"BGM生成エラー: {e}")
            return None
    
    def _map_scene_to_style(self, scene_type: str) -> str:
        """シーンタイプを音楽スタイルにマッピング"""
        style_map = {
            'residential': 'ambient',
            'forest': 'nature',
            'puzzle': 'electronic',
            'chase': 'action',
            'victory': 'orchestral'
        }
        return style_map.get(scene_type, 'ambient')
```

### セキュリティ対策

1. **APIキーの保護**
   - 絶対にコードに直接記述しない
   - .env ファイルは必ず .gitignore に追加
   - 本番環境では環境変数で管理

2. **エラーハンドリング**
   - API呼び出し失敗時のフォールバック
   - タイムアウト設定
   - レート制限の考慮

3. **キャッシュ戦略**
```python
# 生成済み音楽のキャッシュ
class AudioCache:
    def __init__(self, cache_dir: str = "cache/audio"):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)
    
    def get_cached(self, key: str) -> Optional[bytes]:
        """キャッシュから音楽データを取得"""
        cache_path = os.path.join(self.cache_dir, f"{key}.mp3")
        if os.path.exists(cache_path):
            with open(cache_path, 'rb') as f:
                return f.read()
        return None
    
    def save_cache(self, key: str, data: bytes):
        """音楽データをキャッシュに保存"""
        cache_path = os.path.join(self.cache_dir, f"{key}.mp3")
        with open(cache_path, 'wb') as f:
            f.write(data)
```

## 開発環境での設定

### .env.example の作成
```bash
# Beatoven.ai API設定
BEATOVEN_API_KEY=your_api_key_here
BEATOVEN_API_URL=https://api.beatoven.ai/v1
BEATOVEN_TIMEOUT=30

# デバッグ設定
DEBUG_MODE=True
USE_MOCK_API=True  # 開発時はモックAPIを使用

# ゲーム設定
AUDIO_CACHE_ENABLED=True
AUDIO_CACHE_DIR=cache/audio
```

### モックAPI（開発用）
```python
class MockBeatovenAPI:
    """開発環境用のモックAPI"""
    
    def generate_bgm(self, scene_type: str, mood: str, duration: int = 60) -> bytes:
        """既存の音楽ファイルを返す"""
        mock_file = f"assets/music/mock_{scene_type}_{mood}.mp3"
        if os.path.exists(mock_file):
            with open(mock_file, 'rb') as f:
                return f.read()
        # デフォルト音楽を返す
        with open("assets/music/default.mp3", 'rb') as f:
            return f.read()
```

## テスト実装

```python
# tests/unit/test_audio_generator.py
import pytest
from unittest.mock import patch, MagicMock
from src.utils.audio_generator import BeatovenAudioGenerator

class TestBeatovenAudioGenerator:
    @patch.dict('os.environ', {'BEATOVEN_API_KEY': 'test_key'})
    def test_initialization(self):
        """初期化テスト"""
        generator = BeatovenAudioGenerator()
        assert generator.api_key == 'test_key'
    
    def test_missing_api_key(self):
        """APIキー未設定時のエラーテスト"""
        with patch.dict('os.environ', {}, clear=True):
            with pytest.raises(ValueError, match="BEATOVEN_API_KEY"):
                BeatovenAudioGenerator()
    
    @patch('requests.post')
    @patch.dict('os.environ', {'BEATOVEN_API_KEY': 'test_key'})
    def test_generate_bgm_success(self, mock_post):
        """BGM生成成功テスト"""
        mock_response = MagicMock()
        mock_response.content = b'mock_audio_data'
        mock_post.return_value = mock_response
        
        generator = BeatovenAudioGenerator()
        result = generator.generate_bgm('residential', 'happy')
        
        assert result == b'mock_audio_data'
        mock_post.assert_called_once()
```

## トラブルシューティング

### よくある問題

1. **APIキーエラー**
   - .env ファイルの存在確認
   - APIキーの正確性確認
   - 環境変数の読み込み確認

2. **接続エラー**
   - ネットワーク接続確認
   - API URLの正確性確認
   - ファイアウォール設定確認

3. **レート制限**
   - キャッシュの活用
   - リトライロジックの実装
   - API利用状況の監視