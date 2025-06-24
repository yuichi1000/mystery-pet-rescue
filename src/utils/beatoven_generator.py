"""
Beatoven.ai API を使用した音楽・効果音生成システム
"""

import os
import requests
import json
import time
import hashlib
from typing import Optional, Dict, Any, List
from pathlib import Path
from dotenv import load_dotenv
import logging

# 環境変数読み込み
load_dotenv()

logger = logging.getLogger(__name__)

class BeatovenGenerator:
    """Beatoven.ai を使用した音楽・効果音生成クラス"""
    
    def __init__(self):
        self.api_key = os.getenv('BEATOVEN_API_KEY')
        self.api_url = os.getenv('BEATOVEN_API_URL', 'https://api.beatoven.ai/v1')
        self.timeout = int(os.getenv('BEATOVEN_TIMEOUT', '60'))
        
        # キャッシュディレクトリ
        self.cache_dir = Path("cache/audio")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        
        # 生成履歴
        self.generation_history = []
        
        if not self.api_key:
            logger.warning("BEATOVEN_API_KEY が設定されていません。.env ファイルを確認してください。")
    
    def generate_bgm(self, 
                     scene_type: str, 
                     mood: str, 
                     duration: int = 60,
                     style: Optional[str] = None,
                     tempo: Optional[str] = None,
                     instruments: Optional[List[str]] = None) -> Optional[bytes]:
        """
        シーンに応じたBGMを生成
        
        Args:
            scene_type: シーンタイプ（residential, forest, puzzle等）
            mood: 雰囲気（happy, mysterious, tense, calm等）
            duration: 長さ（秒）
            style: 音楽スタイル（ambient, orchestral, electronic等）
            tempo: テンポ（slow, medium, fast）
            instruments: 使用楽器のリスト
            
        Returns:
            生成された音楽データ（バイナリ）
        """
        if not self.api_key:
            logger.error("API キーが設定されていません")
            return None
        
        # パラメータの準備
        params = {
            'scene_type': scene_type,
            'mood': mood,
            'duration': duration,
            'style': style or self._map_scene_to_style(scene_type),
            'tempo': tempo or self._map_mood_to_tempo(mood),
            'instruments': instruments or self._get_default_instruments(scene_type)
        }
        
        # キャッシュチェック
        cache_key = self._generate_cache_key(params)
        cached_audio = self._get_cached_audio(cache_key)
        if cached_audio:
            logger.info(f"キャッシュから音楽を取得: {scene_type}_{mood}")
            return cached_audio
        
        try:
            # API リクエスト
            audio_data = self._make_api_request('generate/music', params)
            
            if audio_data:
                # キャッシュに保存
                self._save_to_cache(cache_key, audio_data, params)
                logger.info(f"BGM生成完了: {scene_type}_{mood} ({duration}秒)")
                return audio_data
            
        except Exception as e:
            logger.error(f"BGM生成エラー: {e}")
        
        return None
    
    def generate_sfx(self, 
                     effect_type: str,
                     intensity: str = "medium",
                     duration: float = 2.0,
                     style: Optional[str] = None) -> Optional[bytes]:
        """
        効果音を生成
        
        Args:
            effect_type: 効果音タイプ（pet_found, button_click, footstep等）
            intensity: 強度（soft, medium, strong）
            duration: 長さ（秒）
            style: スタイル（realistic, cartoon, electronic等）
            
        Returns:
            生成された効果音データ（バイナリ）
        """
        if not self.api_key:
            logger.error("API キーが設定されていません")
            return None
        
        params = {
            'effect_type': effect_type,
            'intensity': intensity,
            'duration': duration,
            'style': style or self._map_effect_to_style(effect_type)
        }
        
        # キャッシュチェック
        cache_key = self._generate_cache_key(params)
        cached_audio = self._get_cached_audio(cache_key)
        if cached_audio:
            logger.info(f"キャッシュから効果音を取得: {effect_type}")
            return cached_audio
        
        try:
            # API リクエスト
            audio_data = self._make_api_request('generate/sfx', params)
            
            if audio_data:
                # キャッシュに保存
                self._save_to_cache(cache_key, audio_data, params)
                logger.info(f"効果音生成完了: {effect_type}")
                return audio_data
            
        except Exception as e:
            logger.error(f"効果音生成エラー: {e}")
        
        return None
    
    def _make_api_request(self, endpoint: str, params: Dict[str, Any]) -> Optional[bytes]:
        """API リクエストを実行"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        url = f"{self.api_url}/{endpoint}"
        
        logger.info(f"API リクエスト開始: {endpoint}")
        logger.debug(f"パラメータ: {params}")
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=params,
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # レスポンスがJSONの場合（非同期処理）
            if response.headers.get('content-type', '').startswith('application/json'):
                result = response.json()
                if 'job_id' in result:
                    return self._wait_for_completion(result['job_id'])
            
            # 直接音声データが返される場合
            return response.content
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API リクエストエラー: {e}")
            return None
    
    def _wait_for_completion(self, job_id: str, max_wait: int = 300) -> Optional[bytes]:
        """非同期ジョブの完了を待機"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
        }
        
        status_url = f"{self.api_url}/jobs/{job_id}/status"
        download_url = f"{self.api_url}/jobs/{job_id}/download"
        
        start_time = time.time()
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(status_url, headers=headers, timeout=10)
                response.raise_for_status()
                
                status_data = response.json()
                status = status_data.get('status')
                
                if status == 'completed':
                    # 音声データをダウンロード
                    download_response = requests.get(download_url, headers=headers, timeout=30)
                    download_response.raise_for_status()
                    return download_response.content
                
                elif status == 'failed':
                    logger.error(f"音声生成失敗: {status_data.get('error', 'Unknown error')}")
                    return None
                
                elif status in ['pending', 'processing']:
                    logger.info(f"生成中... ({status})")
                    time.sleep(5)
                
                else:
                    logger.warning(f"不明なステータス: {status}")
                    time.sleep(5)
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"ステータス確認エラー: {e}")
                time.sleep(5)
        
        logger.error("音声生成がタイムアウトしました")
        return None
    
    def _map_scene_to_style(self, scene_type: str) -> str:
        """シーンタイプを音楽スタイルにマッピング"""
        style_map = {
            'menu': 'ambient',
            'residential': 'acoustic',
            'forest': 'nature',
            'puzzle': 'electronic',
            'chase': 'action',
            'victory': 'orchestral',
            'game_over': 'dramatic'
        }
        return style_map.get(scene_type, 'ambient')
    
    def _map_mood_to_tempo(self, mood: str) -> str:
        """ムードをテンポにマッピング"""
        tempo_map = {
            'calm': 'slow',
            'peaceful': 'slow',
            'happy': 'medium',
            'cheerful': 'medium',
            'mysterious': 'medium',
            'tense': 'fast',
            'exciting': 'fast',
            'dramatic': 'fast'
        }
        return tempo_map.get(mood, 'medium')
    
    def _get_default_instruments(self, scene_type: str) -> List[str]:
        """シーンタイプのデフォルト楽器を取得"""
        instrument_map = {
            'menu': ['piano', 'strings', 'ambient_pad'],
            'residential': ['acoustic_guitar', 'piano', 'light_percussion'],
            'forest': ['flute', 'strings', 'nature_sounds'],
            'puzzle': ['synthesizer', 'electronic_beats', 'ambient_pad'],
            'victory': ['orchestra', 'brass', 'timpani'],
            'game_over': ['strings', 'piano', 'dark_ambient']
        }
        return instrument_map.get(scene_type, ['piano', 'strings'])
    
    def _map_effect_to_style(self, effect_type: str) -> str:
        """効果音タイプをスタイルにマッピング"""
        style_map = {
            'pet_found': 'cheerful',
            'pet_rescued': 'triumphant',
            'button_click': 'clean',
            'footstep': 'realistic',
            'notification': 'pleasant',
            'error': 'attention',
            'puzzle_solve': 'satisfying'
        }
        return style_map.get(effect_type, 'realistic')
    
    def _generate_cache_key(self, params: Dict[str, Any]) -> str:
        """パラメータからキャッシュキーを生成"""
        # パラメータをソートして一意のキーを生成
        sorted_params = json.dumps(params, sort_keys=True)
        return hashlib.md5(sorted_params.encode()).hexdigest()
    
    def _get_cached_audio(self, cache_key: str) -> Optional[bytes]:
        """キャッシュから音声データを取得"""
        cache_file = self.cache_dir / f"{cache_key}.mp3"
        if cache_file.exists():
            try:
                with open(cache_file, 'rb') as f:
                    return f.read()
            except IOError as e:
                logger.error(f"キャッシュ読み込みエラー: {e}")
        return None
    
    def _save_to_cache(self, cache_key: str, audio_data: bytes, params: Dict[str, Any]):
        """音声データをキャッシュに保存"""
        try:
            # 音声ファイルを保存
            cache_file = self.cache_dir / f"{cache_key}.mp3"
            with open(cache_file, 'wb') as f:
                f.write(audio_data)
            
            # メタデータを保存
            meta_file = self.cache_dir / f"{cache_key}.json"
            metadata = {
                'params': params,
                'generated_at': time.time(),
                'file_size': len(audio_data)
            }
            with open(meta_file, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"キャッシュに保存: {cache_key}")
            
        except IOError as e:
            logger.error(f"キャッシュ保存エラー: {e}")
    
    def generate_game_audio_set(self) -> Dict[str, bool]:
        """ゲームに必要な全音声を生成"""
        results = {}
        
        # BGM生成
        bgm_configs = [
            {'scene_type': 'menu', 'mood': 'calm', 'duration': 90},
            {'scene_type': 'residential', 'mood': 'peaceful', 'duration': 120},
            {'scene_type': 'forest', 'mood': 'mysterious', 'duration': 120},
            {'scene_type': 'puzzle', 'mood': 'focused', 'duration': 60},
            {'scene_type': 'victory', 'mood': 'triumphant', 'duration': 30},
            {'scene_type': 'game_over', 'mood': 'dramatic', 'duration': 20}
        ]
        
        for config in bgm_configs:
            name = f"{config['scene_type']}_bgm"
            logger.info(f"BGM生成開始: {name}")
            audio_data = self.generate_bgm(**config)
            results[name] = audio_data is not None
            
            if audio_data:
                # assetsディレクトリに保存
                self._save_to_assets(name + '.mp3', audio_data)
        
        # 効果音生成
        sfx_configs = [
            {'effect_type': 'pet_found', 'intensity': 'medium', 'duration': 1.5},
            {'effect_type': 'pet_rescued', 'intensity': 'strong', 'duration': 2.0},
            {'effect_type': 'button_click', 'intensity': 'soft', 'duration': 0.3},
            {'effect_type': 'footstep', 'intensity': 'soft', 'duration': 0.5},
            {'effect_type': 'notification', 'intensity': 'medium', 'duration': 1.0},
            {'effect_type': 'error', 'intensity': 'medium', 'duration': 0.8},
            {'effect_type': 'puzzle_solve', 'intensity': 'strong', 'duration': 2.5}
        ]
        
        for config in sfx_configs:
            name = config['effect_type']
            logger.info(f"効果音生成開始: {name}")
            audio_data = self.generate_sfx(**config)
            results[name] = audio_data is not None
            
            if audio_data:
                # assetsディレクトリに保存
                self._save_to_assets(name + '.wav', audio_data)
        
        return results
    
    def _save_to_assets(self, filename: str, audio_data: bytes):
        """音声データをassetsディレクトリに保存"""
        if filename.endswith('.mp3'):
            asset_path = Path("assets/music") / filename
        else:
            asset_path = Path("assets/sounds") / filename
        
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(asset_path, 'wb') as f:
                f.write(audio_data)
            logger.info(f"アセットに保存: {asset_path}")
        except IOError as e:
            logger.error(f"アセット保存エラー: {e}")
    
    def clear_cache(self):
        """キャッシュをクリア"""
        try:
            for file in self.cache_dir.glob("*"):
                file.unlink()
            logger.info("キャッシュをクリアしました")
        except Exception as e:
            logger.error(f"キャッシュクリアエラー: {e}")
    
    def get_cache_info(self) -> Dict[str, Any]:
        """キャッシュ情報を取得"""
        cache_files = list(self.cache_dir.glob("*.mp3"))
        total_size = sum(f.stat().st_size for f in cache_files)
        
        return {
            'cache_count': len(cache_files),
            'total_size_mb': total_size / (1024 * 1024),
            'cache_dir': str(self.cache_dir)
        }


# グローバルインスタンス
_beatoven_generator: Optional[BeatovenGenerator] = None

def get_beatoven_generator() -> BeatovenGenerator:
    """BeatovenGeneratorのシングルトンインスタンスを取得"""
    global _beatoven_generator
    if _beatoven_generator is None:
        _beatoven_generator = BeatovenGenerator()
    return _beatoven_generator
