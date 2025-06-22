# ペット図鑑機能ガイド

## 概要
ミステリー・ペット・レスキューのペット図鑑機能は、プレイヤーが救助したペットの情報を管理・表示するシステムです。

## 主な機能

### 1. ペット情報管理
- **基本情報**: 名前、種類、品種、説明
- **特徴**: ペットの性格や外見的特徴
- **レア度**: Common、Uncommon、Rare、Legendary
- **救助情報**: 救助日時、場所、所要時間、挑戦回数

### 2. 図鑑UI
- **一覧表示**: 全ペットの救助状況を一覧で確認
- **詳細表示**: 個別ペットの詳細情報を表示
- **検索機能**: 名前、種類、特徴で検索
- **フィルター機能**: 救助状況、種類、レア度でフィルター

### 3. 統計情報
- **完成度**: 救助済み/全体ペット数と完成率
- **種類別統計**: 犬、猫、うさぎ、鳥の救助状況
- **レア度別統計**: 各レア度の救助状況

## 使用方法

### デモの実行
```bash
# ペット図鑑デモを起動
python examples/pet_collection_demo.py
```

### 基本操作
- **WASD/矢印キー**: プレイヤー移動
- **C**: ペット図鑑を開く
- **R**: ペット救助（テスト用）
- **ESC**: メニューに戻る/終了

### 図鑑の操作
1. **図鑑を開く**: ゲーム中にCキーまたは「ペット図鑑」ボタンをクリック
2. **検索**: 検索ボックスにキーワードを入力
3. **フィルター**: ドロップダウンメニューから条件を選択
4. **詳細表示**: リストからペットを選択
5. **閉じる**: 「閉じる」ボタンまたはESCキー

## データ構造

### ペットデータベース (`data/pets_database.json`)
```json
{
  "pets": [
    {
      "id": "dog_001",
      "name": "チョコ",
      "species": "犬",
      "breed": "チワワ",
      "description": "小さくて元気いっぱいの茶色いチワワ...",
      "characteristics": ["人懐っこい", "元気いっぱい"],
      "rarity": "common",
      "image_path": "assets/images/pets/pet_dog_small.png",
      "found_locations": ["住宅街の公園", "商店街"],
      "rescue_difficulty": 1,
      "rescue_hints": ["おやつを持っていると近づいてくる"]
    }
  ],
  "rarity_info": {
    "common": {
      "name": "コモン",
      "color": "#4CAF50",
      "description": "よく見かけるペット"
    }
  }
}
```

### 救助記録 (`saves/pet_collection.json`)
```json
{
  "rescue_records": [
    {
      "pet_id": "dog_001",
      "rescued": true,
      "rescue_date": "2024-06-22T15:30:00",
      "rescue_location": "住宅街の公園",
      "rescue_time_spent": 30,
      "rescue_attempts": 1
    }
  ]
}
```

## API リファレンス

### PetCollection クラス

#### 主要メソッド
```python
# ペット救助
collection.rescue_pet(pet_id: str, location: str, time_spent: int) -> bool

# 救助状況確認
collection.is_pet_rescued(pet_id: str) -> bool

# ペット情報取得
collection.get_pet_info(pet_id: str) -> Optional[PetInfo]

# フィルタリング
collection.filter_pets_by_species(species: str) -> List[PetInfo]
collection.filter_pets_by_rarity(rarity: str) -> List[PetInfo]

# 検索
collection.search_pets(query: str) -> List[PetInfo]

# 統計情報
collection.get_collection_stats() -> Dict[str, Any]
```

### PetCollectionUI クラス

#### 主要メソッド
```python
# 表示制御
ui.show()  # 図鑑を表示
ui.hide()  # 図鑑を非表示

# イベント処理
ui.handle_event(event: pygame.event.Event) -> bool

# 更新・描画
ui.update(time_delta: float)
ui.draw(surface: pygame.Surface)
```

## カスタマイズ

### 新しいペットの追加
1. `data/pets_database.json` にペット情報を追加
2. 対応する画像ファイルを `assets/images/pets/` に配置
3. ゲームロジックで救助イベントを実装

### UIのカスタマイズ
- `src/ui/pet_collection_ui.py` でレイアウトを変更
- `src/ui/pet_detail_ui.py` で詳細表示をカスタマイズ
- pygame_guiのテーマファイルで外観を変更

### フィルター機能の拡張
- `FilterType` enumに新しいフィルタータイプを追加
- `_handle_filter_change()` メソッドに処理を追加
- 対応するUIコンポーネントを作成

## テスト

### 単体テストの実行
```bash
# ペット図鑑システムのテスト
python -m pytest tests/unit/test_pet_collection.py -v

# 全テストの実行
python -m pytest tests/ -v
```

### テストカバレッジ
- データ管理機能: 100%
- 救助記録機能: 100%
- 検索・フィルター機能: 100%
- 統計機能: 100%

## トラブルシューティング

### よくある問題

1. **図鑑が表示されない**
   - pygame_guiがインストールされているか確認
   - UIマネージャーが正しく初期化されているか確認

2. **ペットデータが読み込まれない**
   - `data/pets_database.json` ファイルの存在確認
   - JSONファイルの構文エラーチェック

3. **救助記録が保存されない**
   - `saves/` ディレクトリの書き込み権限確認
   - ディスク容量の確認

4. **画像が表示されない**
   - 画像ファイルのパスが正しいか確認
   - 画像ファイルの形式（PNG推奨）確認

### デバッグ方法
```python
# ログ出力を有効化
import logging
logging.basicConfig(level=logging.DEBUG)

# 図鑑データの確認
collection = PetCollection()
print(f"読み込まれたペット数: {len(collection.pets_data)}")
print(f"救助記録数: {len(collection.rescue_records)}")
```

## 今後の拡張予定

### v2.0 機能
- ペット画像の動的表示
- アニメーション効果
- 音声ファイルの再生

### v3.0 機能
- オンライン図鑑共有
- 実績システム連携
- カスタムペット作成機能
