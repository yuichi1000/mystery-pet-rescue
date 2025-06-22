"""
記憶ゲーム - カード神経衰弱タイプ
ペットの絵柄カードをめくって同じペアを見つけるゲーム
"""

import pygame
import random
import math
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum

from src.core.minigame import MinigameBase, GameConfig, Difficulty
from src.core.animation import ScaleAnimation, FadeAnimation, create_success_animation

class CardState(Enum):
    """カード状態"""
    FACE_DOWN = "face_down"    # 裏向き
    FACE_UP = "face_up"        # 表向き
    MATCHED = "matched"        # マッチ済み
    FLIPPING = "flipping"      # めくり中

@dataclass
class Card:
    """カードクラス"""
    id: int
    symbol: str
    color: Tuple[int, int, int]
    x: int
    y: int
    width: int
    height: int
    state: CardState = CardState.FACE_DOWN
    flip_animation_time: float = 0.0
    matched_time: float = 0.0
    
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)
    
    def contains_point(self, pos: Tuple[int, int]) -> bool:
        return self.get_rect().collidepoint(pos)
    
    def flip(self) -> None:
        """カードをめくる"""
        if self.state == CardState.FACE_DOWN:
            self.state = CardState.FLIPPING
            self.flip_animation_time = 0.0
    
    def set_matched(self) -> None:
        """マッチ状態に設定"""
        self.state = CardState.MATCHED
        self.matched_time = 0.0
    
    def update(self, time_delta: float) -> None:
        """カード状態更新"""
        if self.state == CardState.FLIPPING:
            self.flip_animation_time += time_delta
            if self.flip_animation_time >= 0.3:  # フリップアニメーション時間
                self.state = CardState.FACE_UP
        elif self.state == CardState.MATCHED:
            self.matched_time += time_delta

class MemoryGame(MinigameBase):
    """記憶ゲーム実装"""
    
    def __init__(self, screen: pygame.Surface, config: GameConfig = None):
        # ゲーム設定を先に初期化
        self.cards: List[Card] = []
        self.flipped_cards: List[Card] = []
        self.matched_pairs = 0
        self.total_pairs = 0
        
        # カード設定
        self.card_width = 80
        self.card_height = 100
        self.card_margin = 10
        
        # 難易度設定
        self.difficulty_settings = {
            Difficulty.EASY: {
                'grid_size': (3, 4),  # 3x4 = 12枚（6ペア）
                'flip_time': 2.0      # カードを見せる時間
            },
            Difficulty.NORMAL: {
                'grid_size': (4, 4),  # 4x4 = 16枚（8ペア）
                'flip_time': 1.5
            },
            Difficulty.HARD: {
                'grid_size': (4, 5),  # 4x5 = 20枚（10ペア）
                'flip_time': 1.0
            }
        }
        
        # カードめくり制御
        self.can_flip = True
        self.flip_timer = 0.0
        self.wrong_pair_timer = 0.0
        
        # ペット絵柄定義
        self.pet_symbols = [
            ("🐶", (139, 69, 19)),   # 犬 - 茶色
            ("🐱", (255, 87, 34)),   # 猫 - オレンジ
            ("🐰", (233, 30, 99)),   # うさぎ - ピンク
            ("🐦", (33, 150, 243)),  # 鳥 - 青
            ("🐹", (255, 193, 7)),   # ハムスター - 黄色
            ("🐢", (76, 175, 80)),   # 亀 - 緑
            ("🐠", (0, 188, 212)),   # 魚 - シアン
            ("🦔", (121, 85, 72)),   # ハリネズミ - 茶色
            ("🐸", (139, 195, 74)),  # カエル - ライトグリーン
            ("🦋", (156, 39, 176))   # 蝶 - 紫
        ]
        
        # 効果音（仮想）
        self.sounds = {
            'flip': None,
            'match': None,
            'wrong': None,
            'complete': None
        }
        
        # 親クラス初期化（最後に実行）
        super().__init__(screen, config)
        
        # 現在の設定
        current_settings = self.difficulty_settings[self.config.difficulty]
        self.grid_cols, self.grid_rows = current_settings['grid_size']
        self.flip_time = current_settings['flip_time']
        self.total_pairs = (self.grid_cols * self.grid_rows) // 2
    
    def _initialize_game(self) -> None:
        """ゲーム初期化"""
        self.cards.clear()
        self.flipped_cards.clear()
        self.matched_pairs = 0
        self.can_flip = True
        self.flip_timer = 0.0
        self.wrong_pair_timer = 0.0
        
        # カード生成
        self._create_cards()
        
        # カードシャッフル
        random.shuffle(self.cards)
        
        # カード位置設定
        self._position_cards()
    
    def _create_cards(self) -> None:
        """カード作成"""
        total_cards = self.grid_cols * self.grid_rows
        pairs_needed = total_cards // 2
        
        # ペアカード作成
        for i in range(pairs_needed):
            symbol, color = self.pet_symbols[i % len(self.pet_symbols)]
            
            # 1枚目
            card1 = Card(
                id=i,
                symbol=symbol,
                color=color,
                x=0, y=0,  # 後で設定
                width=self.card_width,
                height=self.card_height
            )
            
            # 2枚目（ペア）
            card2 = Card(
                id=i,
                symbol=symbol,
                color=color,
                x=0, y=0,  # 後で設定
                width=self.card_width,
                height=self.card_height
            )
            
            self.cards.extend([card1, card2])
    
    def _position_cards(self) -> None:
        """カード位置設定"""
        # グリッド全体のサイズ計算
        total_width = self.grid_cols * self.card_width + (self.grid_cols - 1) * self.card_margin
        total_height = self.grid_rows * self.card_height + (self.grid_rows - 1) * self.card_margin
        
        # 開始位置（中央揃え）
        start_x = (self.screen.get_width() - total_width) // 2
        start_y = (self.screen.get_height() - total_height) // 2
        
        # カード配置
        for i, card in enumerate(self.cards):
            row = i // self.grid_cols
            col = i % self.grid_cols
            
            card.x = start_x + col * (self.card_width + self.card_margin)
            card.y = start_y + row * (self.card_height + self.card_margin)
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベント処理"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and self.state.value == "ready":
                self.start_game()
                return True
            elif event.key == pygame.K_r and self.state.value in ["success", "failure", "timeout"]:
                self.reset_game()
                return True
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.state.value == "playing":  # 左クリック
                return self._handle_card_click(event.pos)
        
        return False
    
    def _handle_card_click(self, pos: Tuple[int, int]) -> bool:
        """カードクリック処理"""
        if not self.can_flip:
            return False
        
        # クリックされたカードを検索
        for card in self.cards:
            if (card.contains_point(pos) and 
                card.state == CardState.FACE_DOWN):
                
                # カードをめくる
                card.flip()
                self.flipped_cards.append(card)
                
                # フリップアニメーション
                card_surface = self._create_card_surface(card, True)
                flip_anim = ScaleAnimation(
                    card_surface, 
                    (card.x + card.width // 2, card.y + card.height // 2),
                    0.3, 0.1, 1.0
                )
                self.add_animation(flip_anim)
                
                # 2枚めくった場合の処理
                if len(self.flipped_cards) == 2:
                    self.can_flip = False
                    self.flip_timer = 0.0
                
                return True
        
        return False
    
    def update_game_logic(self, time_delta: float) -> None:
        """ゲームロジック更新"""
        # カード状態更新
        for card in self.cards:
            card.update(time_delta)
        
        # 2枚めくった後の処理
        if len(self.flipped_cards) == 2 and not self.can_flip:
            self.flip_timer += time_delta
            
            if self.flip_timer >= self.flip_time:
                self._check_card_match()
                self.can_flip = True
        
        # 間違ったペアの処理
        if self.wrong_pair_timer > 0:
            self.wrong_pair_timer -= time_delta
            if self.wrong_pair_timer <= 0:
                self._hide_wrong_cards()
    
    def _check_card_match(self) -> None:
        """カードマッチ判定"""
        if len(self.flipped_cards) != 2:
            return
        
        card1, card2 = self.flipped_cards
        
        if card1.id == card2.id:  # マッチ
            # マッチしたカードを設定
            card1.set_matched()
            card2.set_matched()
            self.matched_pairs += 1
            self.score.points += 50
            
            # マッチアニメーション
            for card in [card1, card2]:
                card_center = (card.x + card.width // 2, card.y + card.height // 2)
                success_animations = create_success_animation(card_center)
                for anim in success_animations:
                    self.add_animation(anim)
            
        else:  # 不一致
            # スコア減点
            self.score.points = max(0, self.score.points - 10)
            
            # 間違ったペアのタイマー開始
            self.wrong_pair_timer = 1.0
        
        # フリップカードリストをクリア
        self.flipped_cards.clear()
    
    def _hide_wrong_cards(self) -> None:
        """間違ったカードを裏返す"""
        for card in self.cards:
            if card.state == CardState.FACE_UP:
                card.state = CardState.FACE_DOWN
                
                # 裏返しアニメーション
                card_surface = self._create_card_surface(card, False)
                flip_anim = ScaleAnimation(
                    card_surface,
                    (card.x + card.width // 2, card.y + card.height // 2),
                    0.3, 1.0, 0.1
                )
                self.add_animation(flip_anim)
    
    def _create_card_surface(self, card: Card, face_up: bool) -> pygame.Surface:
        """カード表面作成"""
        surface = pygame.Surface((card.width, card.height))
        
        if face_up and card.state != CardState.FACE_DOWN:
            # 表面（ペット絵柄）
            surface.fill(card.color)
            
            # シンボル描画
            font = pygame.font.Font(None, 48)
            text_surface = font.render(card.symbol, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=(card.width // 2, card.height // 2))
            surface.blit(text_surface, text_rect)
            
        else:
            # 裏面
            surface.fill((100, 100, 100))
            
            # パターン描画
            for i in range(0, card.width, 10):
                for j in range(0, card.height, 10):
                    if (i + j) % 20 == 0:
                        pygame.draw.rect(surface, (120, 120, 120), (i, j, 8, 8))
        
        # 枠線
        pygame.draw.rect(surface, (255, 255, 255), surface.get_rect(), 2)
        
        return surface
    
    def draw_game_content(self, surface: pygame.Surface) -> None:
        """ゲーム内容描画"""
        # カード描画
        for card in self.cards:
            # カード表面作成
            face_up = (card.state in [CardState.FACE_UP, CardState.MATCHED, CardState.FLIPPING])
            card_surface = self._create_card_surface(card, face_up)
            
            # マッチしたカードは少し透明に
            if card.state == CardState.MATCHED:
                alpha = int(255 * (0.7 + 0.3 * math.sin(card.matched_time * 3)))
                card_surface.set_alpha(alpha)
            
            surface.blit(card_surface, (card.x, card.y))
        
        # 進捗表示
        progress_text = f"マッチしたペア: {self.matched_pairs}/{self.total_pairs}"
        text_surface = self.fonts['medium'].render(progress_text, True, self.colors['text'])
        text_rect = text_surface.get_rect(center=(surface.get_width() // 2, 50))
        surface.blit(text_surface, text_rect)
        
        # 操作説明
        if self.state.value == "ready":
            instructions = [
                "同じペットのカードを2枚めくってペアを作ろう！",
                "全てのペアを見つけるとクリア",
                "SPACE: ゲーム開始"
            ]
            
            y_offset = surface.get_height() - 100
            for instruction in instructions:
                text_surface = self.fonts['small'].render(instruction, True, self.colors['text'])
                text_rect = text_surface.get_rect(center=(surface.get_width() // 2, y_offset))
                surface.blit(text_surface, text_rect)
                y_offset += 25
        
        # フリップ制限中の表示
        if not self.can_flip and len(self.flipped_cards) == 2:
            remaining_time = max(0, self.flip_time - self.flip_timer)
            wait_text = f"確認中... {remaining_time:.1f}秒"
            text_surface = self.fonts['small'].render(wait_text, True, self.colors['warning'])
            text_rect = text_surface.get_rect(center=(surface.get_width() // 2, surface.get_height() - 30))
            surface.blit(text_surface, text_rect)
    
    def check_win_condition(self) -> bool:
        """勝利条件チェック"""
        return self.matched_pairs >= self.total_pairs
    
    def check_lose_condition(self) -> bool:
        """敗北条件チェック"""
        # このゲームでは時間切れのみが敗北条件
        return False
