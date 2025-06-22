"""
NPCクラス

ノンプレイヤーキャラクター（住民、飼い主など）を管理
"""

import pygame
import random
from typing import List, Dict, Optional, Tuple
from config.constants import *


class NPC:
    """NPCクラス"""
    
    def __init__(self, npc_type: str, x: int, y: int, name: str = None):
        """
        NPCを初期化
        
        Args:
            npc_type: NPCの種類 (resident, owner, shopkeeper, etc.)
            x: 初期X座標
            y: 初期Y座標
            name: NPC名（省略時は自動生成）
        """
        self.npc_type = npc_type
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.name = name or self._generate_name()
        
        # 移動
        self.speed = NPC_SPEED
        self.direction = "down"
        self.moving = False
        self.move_pattern = "stationary"  # stationary, patrol, random
        
        # パトロール用
        self.patrol_points = []
        self.current_patrol_index = 0
        self.patrol_wait_time = 0
        self.patrol_wait_duration = 120  # フレーム数
        
        # 当たり判定
        self.rect = pygame.Rect(x, y, self.width, self.height)
        
        # 対話
        self.dialogue_lines = self._generate_dialogue()
        self.current_dialogue_index = 0
        self.can_talk = True
        self.talk_cooldown = 0
        
        # 状態
        self.mood = "neutral"  # happy, sad, worried, angry, neutral
        self.busy = False
        self.quest_giver = False
        
        # アニメーション
        self.animation_frame = 0
        self.animation_timer = 0
        self.animation_speed = 20
        
        # ペット関連
        self.owned_pets = []  # 飼っているペットのID
        self.lost_pets = []   # 迷子になったペットのID
        self.looking_for_pet = False
        
        # 個性
        self.personality_traits = self._generate_personality()
    
    def _generate_name(self) -> str:
        """NPC名を生成"""
        first_names = [
            "太郎", "花子", "次郎", "美咲", "健太", "由美",
            "大輔", "恵子", "翔太", "真理", "和也", "智子"
        ]
        last_names = [
            "田中", "佐藤", "鈴木", "高橋", "渡辺", "伊藤",
            "山田", "中村", "小林", "加藤", "吉田", "山本"
        ]
        
        if self.npc_type == "child":
            return random.choice(first_names)
        else:
            return f"{random.choice(last_names)}{random.choice(first_names)}"
    
    def _generate_dialogue(self) -> List[str]:
        """対話内容を生成"""
        dialogues = {
            "resident": [
                "こんにちは！今日はいい天気ですね。",
                "最近、迷子のペットが多くて心配です。",
                "あなたはペット探しをしているんですか？",
                "頑張ってくださいね！"
            ],
            "owner": [
                "うちの子が迷子になってしまって...",
                "もし見かけたら教えてください！",
                "とても心配で眠れません。",
                "お願いします、見つけてください！"
            ],
            "child": [
                "わーい！お兄さん/お姉さんだ！",
                "ペット探しって楽しそう！",
                "僕/私も手伝いたいな！",
                "頑張って！"
            ],
            "elderly": [
                "最近の若い人は優しいねぇ。",
                "昔はこんなに迷子のペットはいなかったよ。",
                "気をつけて歩きなさいよ。",
                "ありがたいことじゃ。"
            ],
            "shopkeeper": [
                "いらっしゃいませ！",
                "ペット用品もありますよ。",
                "迷子のペットの情報があれば教えますね。",
                "またお越しください！"
            ]
        }
        
        return dialogues.get(self.npc_type, ["こんにちは。", "元気ですか？"])
    
    def _generate_personality(self) -> Dict[str, int]:
        """個性を生成"""
        traits = ["friendly", "helpful", "talkative", "worried", "cheerful"]
        personality = {}
        
        for trait in traits:
            personality[trait] = random.randint(20, 80)
        
        # NPCタイプに応じた調整
        if self.npc_type == "owner":
            personality["worried"] += 30
            personality["helpful"] += 20
        elif self.npc_type == "child":
            personality["cheerful"] += 40
            personality["talkative"] += 30
        elif self.npc_type == "elderly":
            personality["helpful"] += 20
            personality["talkative"] += 10
        
        # 値の範囲制限
        for trait in personality:
            personality[trait] = max(0, min(100, personality[trait]))
        
        return personality
    
    def update(self, player_pos: Tuple[int, int]):
        """NPCを更新"""
        # 移動処理
        self._update_movement()
        
        # アニメーション更新
        self._update_animation()
        
        # 対話クールダウン
        if self.talk_cooldown > 0:
            self.talk_cooldown -= 1
        
        # 当たり判定更新
        self.rect.x = self.x
        self.rect.y = self.y
        
        # プレイヤーとの距離チェック
        distance = self._calculate_distance(player_pos)
        if distance < 50:  # 近くにいる場合
            self._react_to_player()
    
    def _calculate_distance(self, target_pos: Tuple[int, int]) -> float:
        """指定位置との距離を計算"""
        dx = self.x - target_pos[0]
        dy = self.y - target_pos[1]
        return (dx * dx + dy * dy) ** 0.5
    
    def _update_movement(self):
        """移動処理"""
        if self.move_pattern == "stationary":
            return
        
        elif self.move_pattern == "patrol":
            self._update_patrol()
        
        elif self.move_pattern == "random":
            self._update_random_movement()
    
    def _update_patrol(self):
        """パトロール移動を更新"""
        if not self.patrol_points:
            return
        
        target = self.patrol_points[self.current_patrol_index]
        dx = target[0] - self.x
        dy = target[1] - self.y
        distance = (dx * dx + dy * dy) ** 0.5
        
        if distance < self.speed:
            # 目標地点に到達
            self.x, self.y = target
            self.moving = False
            
            # 待機時間
            if self.patrol_wait_time < self.patrol_wait_duration:
                self.patrol_wait_time += 1
            else:
                self.patrol_wait_time = 0
                self.current_patrol_index = (self.current_patrol_index + 1) % len(self.patrol_points)
        else:
            # 目標地点に向かって移動
            self.moving = True
            self.x += (dx / distance) * self.speed
            self.y += (dy / distance) * self.speed
            
            # 方向を更新
            if abs(dx) > abs(dy):
                self.direction = "right" if dx > 0 else "left"
            else:
                self.direction = "down" if dy > 0 else "up"
    
    def _update_random_movement(self):
        """ランダム移動を更新"""
        # 簡単なランダム移動（実装は省略）
        pass
    
    def _update_animation(self):
        """アニメーション更新"""
        if self.moving:
            self.animation_timer += 1
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                self.animation_frame = (self.animation_frame + 1) % 4
        else:
            self.animation_frame = 0
    
    def _react_to_player(self):
        """プレイヤーに対する反応"""
        if self.personality_traits.get("friendly", 50) > 60:
            # フレンドリーなNPCは向きを変える
            # （実装は省略）
            pass
    
    def render(self, screen: pygame.Surface):
        """NPCを描画"""
        # NPCタイプに応じた色
        colors = {
            "resident": COLOR_GREEN,
            "owner": COLOR_RED,
            "child": COLOR_YELLOW,
            "elderly": COLOR_GRAY,
            "shopkeeper": COLOR_BLUE
        }
        
        color = colors.get(self.npc_type, COLOR_WHITE)
        
        # 気分に応じて色を調整
        if self.mood == "worried":
            color = tuple(max(0, c - 30) for c in color)
        elif self.mood == "happy":
            color = tuple(min(255, c + 30) for c in color)
        
        # NPCを描画
        pygame.draw.rect(screen, color, self.rect)
        
        # 名前を表示（デバッグ用）
        if hasattr(pygame, 'font') and pygame.font.get_init():
            font = pygame.font.Font(None, 24)
            name_text = font.render(self.name, True, COLOR_WHITE)
            screen.blit(name_text, (self.x, self.y - 25))
        
        # 迷子ペットを探している場合のインジケーター
        if self.looking_for_pet:
            pygame.draw.circle(screen, COLOR_RED, (self.x + self.width - 5, self.y + 5), 3)
    
    def talk(self) -> Optional[str]:
        """対話を開始"""
        if not self.can_talk or self.talk_cooldown > 0:
            return None
        
        if self.current_dialogue_index < len(self.dialogue_lines):
            dialogue = self.dialogue_lines[self.current_dialogue_index]
            self.current_dialogue_index += 1
            self.talk_cooldown = 60  # 1秒のクールダウン
            return dialogue
        else:
            # 対話終了
            self.current_dialogue_index = 0
            return None
    
    def set_patrol_route(self, points: List[Tuple[int, int]]):
        """パトロールルートを設定"""
        self.patrol_points = points
        self.move_pattern = "patrol"
        self.current_patrol_index = 0
    
    def add_owned_pet(self, pet_id: str):
        """飼っているペットを追加"""
        if pet_id not in self.owned_pets:
            self.owned_pets.append(pet_id)
    
    def lose_pet(self, pet_id: str):
        """ペットを迷子にする"""
        if pet_id in self.owned_pets and pet_id not in self.lost_pets:
            self.lost_pets.append(pet_id)
            self.looking_for_pet = True
            self.mood = "worried"
            
            # 対話内容を更新
            self.dialogue_lines = [
                f"うちの{pet_id}が迷子になってしまって...",
                "どこかで見かけませんでしたか？",
                "とても心配です。",
                "見つけたら教えてください！"
            ]
    
    def reunite_with_pet(self, pet_id: str):
        """ペットと再会"""
        if pet_id in self.lost_pets:
            self.lost_pets.remove(pet_id)
            if not self.lost_pets:
                self.looking_for_pet = False
                self.mood = "happy"
                
                # 対話内容を更新
                self.dialogue_lines = [
                    "ありがとうございます！",
                    "うちの子を見つけてくれて！",
                    "本当に感謝しています。",
                    "これはお礼です。"
                ]
    
    def get_info(self) -> Dict:
        """NPC情報を取得"""
        return {
            "name": self.name,
            "type": self.npc_type,
            "mood": self.mood,
            "owned_pets": self.owned_pets,
            "lost_pets": self.lost_pets,
            "looking_for_pet": self.looking_for_pet,
            "personality": self.personality_traits,
            "can_talk": self.can_talk
        }
