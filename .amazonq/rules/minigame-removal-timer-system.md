# ミニゲーム削除と時間制限システム実装指示

## 概要
開発時間短縮とゲーム性向上のため、ミニゲームを削除し、時間制限システムを実装します。

## 削除対象

### 1. ファイル削除
以下のファイルを削除してください：
- `src/systems/mini_games.py`
- `src/ui/minigame_ui.py`（存在する場合）

### 2. コード修正 - ミニゲーム削除

#### `src/scenes/game.py`（またはsrc/game_states/gameplay.py）
- ミニゲーム関連のimport文を削除
- ミニゲームの初期化処理を削除
- ペット発見時のミニゲーム起動処理を削除
- ミニゲームクリア時の処理を削除

現在の実装を確認すると、既にミニゲームは使用されておらず、パズルシステムが使用されています。

## 新機能実装：時間制限システム

### 1. タイマー機能
- **ゲーム開始時に5分のタイマーを開始**
- `self.game_time_limit = 300.0`  # 5分 = 300秒
- `self.remaining_time = self.game_time_limit`

### 2. UI表示
#### `src/ui/game_ui.py`に追加
- 画面上部にタイマー表示を追加
- 残り時間をMM:SS形式で表示
- 時間が少なくなったら色を変更（例：30秒以下で赤色）

### 3. ヒントシステム
#### 時間経過によるヒント表示
- **2分経過**：「ペットの鳴き声が聞こえます」+ 音響エフェクト
- **3分経過**：「足跡を発見しました」+ 方向指示
- **4分経過**：「ペットが近くにいます」+ より具体的な位置ヒント

#### 実装方法
```python
def update_hints(self, dt):
    elapsed_time = self.game_time_limit - self.remaining_time
    
    if elapsed_time >= 120 and not self.hint_2min_shown:  # 2分
        self.show_audio_hint()
        self.hint_2min_shown = True
    elif elapsed_time >= 180 and not self.hint_3min_shown:  # 3分
        self.show_direction_hint()
        self.hint_3min_shown = True
    elif elapsed_time >= 240 and not self.hint_4min_shown:  # 4分
        self.show_location_hint()
        self.hint_4min_shown = True
```

### 4. ゲーム終了条件
- **時間切れ**：ゲームオーバー
- **全ペット救出**：勝利（残り時間によるボーナススコア）

### 5. スコアシステム
#### タイムボーナス計算
```python
def calculate_score(self):
    base_score = len(self.pets_rescued) * 1000
    time_bonus = int(self.remaining_time * 10)  # 残り秒数 × 10
    return base_score + time_bonus
```

### 6. 音響効果
- **ヒント音**：柔らかいチャイム音
- **時間警告音**：30秒以下で緊張感のある音
- **タイムアップ音**：ゲーム終了時の音

## 実装の優先順位
1. **高優先度**：基本タイマー機能、UI表示
2. **中優先度**：時間切れ処理、スコア計算
3. **低優先度**：ヒントシステム、音響効果

## 理由
- ミニゲーム削除により開発時間を大幅短縮
- 時間制限により適度な緊張感を追加
- ヒントシステムでプレイヤーサポート
- 実装が簡単で効果的なゲーム性向上