#!/usr/bin/env python3
"""
ペット救出効果音生成スクリプト
Beatoven.aiを使って1秒の短い効果音を生成
"""

import os
import requests
import json
from pathlib import Path
from dotenv import load_dotenv

# 環境変数読み込み
load_dotenv()

def generate_pet_rescue_sound():
    """ペット救出用の短い効果音を生成"""
    
    api_key = os.getenv('BEATOVEN_API_KEY')
    if not api_key:
        print("❌ BEATOVEN_API_KEY が設定されていません")
        return False
    
    # API設定
    api_url = "https://public-api.beatoven.ai/api/v1/generate"
    
    # 効果音生成パラメータ
    payload = {
        "type": "sfx",
        "description": "Happy pet rescue success sound effect",
        "duration": 1.0,  # 1秒
        "style": "cheerful",
        "mood": "joyful",
        "intensity": "medium",
        "format": "wav",
        "sample_rate": 44100
    }
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        print("🎵 ペット救出効果音を生成中...")
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            # 音声データを保存
            output_path = Path("assets/sounds/pet_rescued.wav")
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ 効果音生成完了: {output_path}")
            print(f"📊 ファイルサイズ: {len(response.content)} bytes")
            return True
        else:
            print(f"❌ API エラー: {response.status_code}")
            print(f"レスポンス: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ エラー: {e}")
        return False

if __name__ == "__main__":
    success = generate_pet_rescue_sound()
    if success:
        print("🎉 ペット救出効果音の生成が完了しました！")
    else:
        print("💔 効果音生成に失敗しました")
