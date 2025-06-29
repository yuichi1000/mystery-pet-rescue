"""
メニューシーン
タイトル画面とメインメニューを管理
"""

import pygame
from typing import Optional, List
from src.core.scene import Scene
from src.utils.asset_manager import get_asset_manager
from src.utils.font_manager import get_font_manager
from src.utils.language_manager import get_language_manager, Language, get_text

class MenuItem:
    """メニューアイテムクラス"""
    def __init__(self, text: str, action: str, rect: pygame.Rect):
        self.text = text
        self.action = action
        self.rect = rect
        self.hovered = False
        self.selected = False

class LanguageSelector:
    """言語選択セレクトボックス"""
    def __init__(self, rect: pygame.Rect, on_language_change=None):
        self.rect = rect
        self.expanded = False
        self.hovered = False
        self.languages = [Language.ENGLISH, Language.JAPANESE]
        self.language_manager = get_language_manager()
        self.on_language_change = on_language_change  # コールバック関数
        
        print(f"🔧 言語選択ボックス初期化:")
        print(f"  位置: {rect}")
        print(f"  言語リスト: {[lang.value for lang in self.languages]}")
        print(f"  現在の言語: {self.language_manager.get_current_language().value}")
        
        # 各言語の表示名を確認
        for lang in self.languages:
            display_name = self.language_manager.get_language_display_name(lang)
            print(f"  {lang.value} -> '{display_name}'")
        
    def handle_click(self, pos: tuple) -> bool:
        """クリック処理"""
        if self.rect.collidepoint(pos):
            self.expanded = not self.expanded
            print(f"🔽 言語選択ボックスクリック: expanded={self.expanded}")
            return True
        
        if self.expanded:
            # 展開されている場合、各言語オプションをチェック
            for i, lang in enumerate(self.languages):
                option_rect = pygame.Rect(
                    self.rect.x, 
                    self.rect.y + (i + 1) * self.rect.height,
                    self.rect.width, 
                    self.rect.height
                )
                if option_rect.collidepoint(pos):
                    print(f"🌐 言語選択: {lang.value}")
                    old_lang = self.language_manager.get_current_language()
                    self.language_manager.set_language(lang)
                    new_lang = self.language_manager.get_current_language()
                    print(f"🔄 言語変更: {old_lang.value} → {new_lang.value}")
                    
                    # コールバック関数を呼び出し（メニューアイテムを再作成）
                    if self.on_language_change:
                        self.on_language_change()
                    self.expanded = False
                    return True
            
            # 外側をクリックした場合は閉じる
            self.expanded = False
        
        return False
    
    def update_hover(self, pos: tuple):
        """ホバー状態を更新"""
        self.hovered = self.rect.collidepoint(pos)
    
    def draw(self, screen: pygame.Surface, font: pygame.font.Font):
        """描画"""
        # メインボックス
        color = (100, 100, 100) if self.hovered else (70, 70, 70)
        pygame.draw.rect(screen, color, self.rect)
        pygame.draw.rect(screen, (200, 200, 200), self.rect, 2)
        
        # 現在の言語を表示
        current_lang = self.language_manager.get_current_language()
        current_text = self.language_manager.get_language_display_name(current_lang)
        text_surface = font.render(current_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        # ドロップダウン矢印
        arrow_points = [
            (self.rect.right - 15, self.rect.centery - 3),
            (self.rect.right - 10, self.rect.centery + 3),
            (self.rect.right - 5, self.rect.centery - 3)
        ]
        pygame.draw.polygon(screen, (255, 255, 255), arrow_points)
        
        # 展開されている場合、オプションを表示
        if self.expanded:
            print(f"🔽 言語選択展開中: {len(self.languages)}個の言語 {[lang.value for lang in self.languages]}")
            for i, lang in enumerate(self.languages):
                option_rect = pygame.Rect(
                    self.rect.x, 
                    self.rect.y + (i + 1) * self.rect.height,
                    self.rect.width, 
                    self.rect.height
                )
                
                # 背景色を決定
                if lang == current_lang:
                    option_color = (120, 120, 120)  # 現在選択中の言語
                else:
                    option_color = (90, 90, 90)     # その他の言語
                
                # 背景を描画
                pygame.draw.rect(screen, option_color, option_rect)
                pygame.draw.rect(screen, (200, 200, 200), option_rect, 1)
                
                # テキストを描画
                option_text = self.language_manager.get_language_display_name(lang)
                option_surface = font.render(option_text, True, (255, 255, 255))
                option_text_rect = option_surface.get_rect(center=option_rect.center)
                screen.blit(option_surface, option_text_rect)
                
                print(f"  📝 描画: {lang.value} -> '{option_text}' at y={option_rect.y}")

class MenuScene(Scene):
    """メニューシーン"""
    
    def __init__(self, screen: pygame.Surface):
        super().__init__(screen)
        
        # アセットマネージャー
        self.asset_manager = get_asset_manager()
        self.font_manager = get_font_manager()
        self.language_manager = get_language_manager()
        
        # 背景画像
        self.background_image = None
        self._load_background()
        
        # メニューアイテム
        self.menu_items: List[MenuItem] = []
        self.selected_index = 0
        
        # 色設定
        self.normal_color = (255, 255, 255)
        self.hover_color = (255, 255, 0)
        self.selected_color = (0, 255, 0)
        
        # 言語選択セレクトボックス
        self.language_selector = None
        
        # GameFlowManagerの参照（言語変更時のウィンドウタイトル更新用）
        self.game_flow_manager = None
        
        self._create_menu_items()
    
    def set_game_flow_manager(self, game_flow_manager):
        """GameFlowManagerの参照を設定"""
        self.game_flow_manager = game_flow_manager
    
    def _load_background(self):
        """背景画像を読み込み"""
        try:
            print("🖼️ メニュー背景画像を読み込み中...")
            self.background_image = self.asset_manager.get_image("backgrounds/menu_background.png")
            if self.background_image:
                print(f"✅ 背景画像読み込み成功: {self.background_image.get_size()}")
                # 画面サイズに合わせてスケール
                screen_size = (self.screen.get_width(), self.screen.get_height())
                self.background_image = pygame.transform.scale(self.background_image, screen_size)
                print(f"✅ 背景画像スケール完了: {screen_size}")
            else:
                print("❌ 背景画像の取得に失敗")
        except Exception as e:
            print(f"❌ 背景画像の読み込みに失敗: {e}")
            self.background_image = None
    
    def _create_menu_items(self):
        """メニューアイテムを作成"""
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()
        
        # 現在の言語を確認
        current_lang = self.language_manager.get_current_language()
        print(f"📝 メニューアイテム作成中 - 現在の言語: {current_lang.value}")
        
        # メニューアイテムのサイズと位置
        item_width = 300
        item_height = 60
        start_y = screen_height // 2
        spacing = 80
        
        # メニューアイテムを作成（言語に応じて更新）
        start_text = get_text("start_game")
        quit_text = get_text("quit_game")
        print(f"📝 翻訳テキスト: start='{start_text}', quit='{quit_text}'")
        
        menu_data = [
            (start_text, "start_game"),
            (quit_text, "quit_game")
        ]
        
        self.menu_items = []
        for i, (text, action) in enumerate(menu_data):
            x = (screen_width - item_width) // 2
            y = start_y + i * spacing
            rect = pygame.Rect(x, y, item_width, item_height)
            self.menu_items.append(MenuItem(text, action, rect))
            print(f"📝 メニューアイテム更新: {action} -> '{text}'")
        
        # 言語選択セレクトボックスを作成（既存のものがあれば展開状態を保持）
        lang_width = 200
        lang_height = 40
        lang_x = (screen_width - lang_width) // 2
        lang_y = start_y + len(menu_data) * spacing + 20
        lang_rect = pygame.Rect(lang_x, lang_y, lang_width, lang_height)
        
        # 既存の言語選択ボックスがある場合は展開状態を保持
        was_expanded = False
        if self.language_selector:
            was_expanded = self.language_selector.expanded
            print(f"🔄 既存の言語選択ボックスの展開状態を保持: {was_expanded}")
        
        self.language_selector = LanguageSelector(lang_rect, self._on_language_change)
        
        # 展開状態を復元
        if was_expanded:
            self.language_selector.expanded = True
            print(f"✅ 展開状態を復元: {self.language_selector.expanded}")
        
        # 最初のアイテムを選択
        if self.menu_items:
            self.menu_items[self.selected_index].selected = True
            self.menu_items[self.selected_index].selected = True
    
    def _on_language_change(self):
        """言語変更時のコールバック"""
        print("🌐 言語変更検出、メニューテキストを更新中...")
        self._create_menu_items()
        
        # ウィンドウタイトルも更新
        if self.game_flow_manager:
            self.game_flow_manager.update_window_title()
    
    def enter(self) -> None:
        """シーンに入る時の処理"""
        print("メニューシーンに入りました")
    
    def exit(self) -> None:
        """シーンから出る時の処理"""
        print("メニューシーンから出ます")
    
    def handle_event(self, event: pygame.event.Event) -> Optional[str]:
        """イベント処理"""
        # テキスト入力イベントを無視（日本語入力対策）
        if event.type == pygame.TEXTINPUT:
            return None
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP or event.key == pygame.K_w:
                self._move_selection(-1)
            elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                self._move_selection(1)
            elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                return self._activate_selected()
            elif event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                return "quit"
        
        elif event.type == pygame.MOUSEMOTION:
            self._handle_mouse_hover(event.pos)
            # 言語選択のホバー処理
            if self.language_selector:
                self.language_selector.update_hover(event.pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # 左クリック
                # 言語選択のクリック処理
                if self.language_selector and self.language_selector.handle_click(event.pos):
                    # 言語が変更された場合のみメニューアイテムのテキストを更新
                    print(f"🌐 言語変更検出、メニューテキストを更新中...")
                    self._update_menu_item_texts()
                    return None
                
                return self._handle_mouse_click(event.pos)
        
        return None
    
    def _update_menu_item_texts(self):
        """メニューアイテムのテキストのみを更新（位置は変更しない）"""
        if not self.menu_items:
            return
            
        # 現在の言語でテキストを更新
        texts = [get_text("start_game"), get_text("quit_game")]
        actions = ["start_game", "quit_game"]
        
        for i, (text, action) in enumerate(zip(texts, actions)):
            if i < len(self.menu_items):
                self.menu_items[i].text = text
                self.menu_items[i].action = action
                print(f"📝 メニューアイテム更新: {action} -> '{text}'")
    
    def _move_selection(self, direction: int):
        """選択を移動"""
        if not self.menu_items:
            return
        
        # 現在の選択を解除
        self.menu_items[self.selected_index].selected = False
        
        # 新しい選択インデックス
        self.selected_index = (self.selected_index + direction) % len(self.menu_items)
        
        # 新しい選択を設定
        self.menu_items[self.selected_index].selected = True
    
    def _activate_selected(self) -> str:
        """選択されたアイテムを実行"""
        if self.menu_items and 0 <= self.selected_index < len(self.menu_items):
            action = self.menu_items[self.selected_index].action
            if action == "start_game":
                return "game"
            elif action == "quit_game":
                return "quit"
        return "game"
    
    def _handle_mouse_hover(self, pos: tuple):
        """マウスホバー処理"""
        for i, item in enumerate(self.menu_items):
            if item.rect.collidepoint(pos):
                # ホバー状態を設定
                item.hovered = True
                # 選択も変更
                if i != self.selected_index:
                    self.menu_items[self.selected_index].selected = False
                    self.selected_index = i
                    item.selected = True
            else:
                item.hovered = False
    
    def _handle_mouse_click(self, pos: tuple) -> Optional[str]:
        """マウスクリック処理"""
        for item in self.menu_items:
            if item.rect.collidepoint(pos):
                action = item.action
                if action == "start_game":
                    return "game"
                elif action == "quit_game":
                    return "quit"
        return None
    
    def update(self, time_delta: float) -> Optional[str]:
        """更新処理"""
        return None
    
    def draw(self, surface: pygame.Surface) -> None:
        """描画処理"""
        # 背景描画
        if self.background_image:
            surface.blit(self.background_image, (0, 0))
        else:
            # 背景画像がない場合はグラデーション背景
            self._draw_gradient_background(surface)
        
        # メニューアイテムを描画
        self._draw_menu_items(surface)
        
        # 言語選択を描画
        if self.language_selector:
            font = self.font_manager.get_font("default", 24)
            
            # "Language" ラベル
            label_text = get_text("language")
            label_surface = font.render(label_text, True, (255, 255, 255))
            label_rect = label_surface.get_rect()
            label_rect.centerx = self.language_selector.rect.centerx
            label_rect.bottom = self.language_selector.rect.top - 10
            surface.blit(label_surface, label_rect)
            
            # 言語選択ボックス
            self.language_selector.draw(surface, font)
            print(f"🎨 言語選択ボックス描画完了: {self.language_selector.rect}")
        else:
            print("❌ 言語選択ボックスが存在しません")
    
    def _draw_menu_items(self, surface: pygame.Surface):
        """メニューアイテムを描画"""
        button_font = self.font_manager.get_font("default", 32)
        
        for item in self.menu_items:
            # 背景色を決定
            if item.selected:
                bg_color = (100, 100, 100)
                text_color = self.selected_color
            elif item.hovered:
                bg_color = (80, 80, 80)
                text_color = self.hover_color
            else:
                bg_color = (60, 60, 60)
                text_color = self.normal_color
            
            # 背景を描画
            pygame.draw.rect(surface, bg_color, item.rect)
            pygame.draw.rect(surface, text_color, item.rect, 2)
            
            # テキストを描画
            text_surface = button_font.render(item.text, True, text_color)
            text_rect = text_surface.get_rect(center=item.rect.center)
            surface.blit(text_surface, text_rect)
    
    def _draw_gradient_background(self, surface: pygame.Surface):
        """グラデーション背景を描画"""
        # 上から下へのグラデーション
        for y in range(surface.get_height()):
            ratio = y / surface.get_height()
            r = int(30 + (80 - 30) * ratio)
            g = int(50 + (120 - 50) * ratio)
            b = int(80 + (160 - 80) * ratio)
            color = (r, g, b)
            pygame.draw.line(surface, color, (0, y), (surface.get_width(), y))
