"""
ペット詳細表示UI
個別ペットの詳細情報を表示
"""

import pygame
import pygame_gui
from typing import Optional
from datetime import datetime

from src.systems.pet_collection import PetCollection, PetInfo, PetRescueRecord

class PetDetailUI:
    """ペット詳細UIクラス"""
    
    def __init__(self, screen: pygame.Surface, ui_manager: pygame_gui.UIManager):
        self.screen = screen
        self.ui_manager = ui_manager
        self.pet_collection = PetCollection()
        
        # UI要素
        self.container = None
        self.pet_image = None
        self.name_label = None
        self.species_label = None
        self.breed_label = None
        self.rarity_label = None
        self.description_text = None
        self.characteristics_text = None
        self.rescue_status_label = None
        self.rescue_info_text = None
        self.hints_text = None
        self.close_button = None
        
        # 状態管理
        self.is_visible = False
        self.current_pet_id: Optional[str] = None
        
        self._create_ui()
    
    def _create_ui(self) -> None:
        """UI要素を作成"""
        screen_width, screen_height = self.screen.get_size()
        
        # 詳細表示コンテナ（中央に配置）
        container_width = 600
        container_height = 500
        container_x = (screen_width - container_width) // 2
        container_y = (screen_height - container_height) // 2
        
        self.container = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(container_x, container_y, container_width, container_height),
            starting_layer_height=20,
            manager=self.ui_manager
        )
        
        # 閉じるボタン
        self.close_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(-80, 10, 60, 30),
            text='閉じる',
            manager=self.ui_manager,
            container=self.container,
            anchors={'right': 'right'}
        )
        
        # ペット画像エリア（左側）
        self.pet_image = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(20, 50, 150, 150),
            starting_layer_height=1,
            manager=self.ui_manager,
            container=self.container
        )
        
        # 基本情報（右上）
        self.name_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(190, 50, 200, 30),
            text='',
            manager=self.ui_manager,
            container=self.container
        )
        
        self.species_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(190, 80, 200, 25),
            text='',
            manager=self.ui_manager,
            container=self.container
        )
        
        self.breed_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(190, 105, 200, 25),
            text='',
            manager=self.ui_manager,
            container=self.container
        )
        
        self.rarity_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(190, 130, 200, 25),
            text='',
            manager=self.ui_manager,
            container=self.container
        )
        
        # 救助ステータス
        self.rescue_status_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(190, 160, 200, 30),
            text='',
            manager=self.ui_manager,
            container=self.container
        )
        
        # 説明文
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 220, 100, 25),
            text='説明:',
            manager=self.ui_manager,
            container=self.container
        )
        
        self.description_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(20, 245, -40, 60),
            html_text='',
            manager=self.ui_manager,
            container=self.container,
            anchors={'right': 'right'}
        )
        
        # 特徴
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 315, 100, 25),
            text='特徴:',
            manager=self.ui_manager,
            container=self.container
        )
        
        self.characteristics_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(20, 340, 270, 40),
            html_text='',
            manager=self.ui_manager,
            container=self.container
        )
        
        # 救助情報
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(310, 315, 100, 25),
            text='救助情報:',
            manager=self.ui_manager,
            container=self.container
        )
        
        self.rescue_info_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(310, 340, -40, 40),
            html_text='',
            manager=self.ui_manager,
            container=self.container,
            anchors={'right': 'right'}
        )
        
        # ヒント
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 390, 100, 25),
            text='救助のヒント:',
            manager=self.ui_manager,
            container=self.container
        )
        
        self.hints_text = pygame_gui.elements.UITextBox(
            relative_rect=pygame.Rect(20, 415, -40, 60),
            html_text='',
            manager=self.ui_manager,
            container=self.container,
            anchors={'right': 'right'}
        )
        
        # 初期状態では非表示
        self.container.visible = False
    
    def show_pet_detail(self, pet_id: str) -> None:
        """ペットの詳細を表示"""
        self.current_pet_id = pet_id
        pet_info = self.pet_collection.get_pet_info(pet_id)
        rescue_record = self.pet_collection.get_rescue_record(pet_id)
        
        if not pet_info:
            return
        
        # 基本情報を設定
        self.name_label.set_text(f"名前: {pet_info.name}")
        self.species_label.set_text(f"種類: {pet_info.species}")
        self.breed_label.set_text(f"品種: {pet_info.breed}")
        
        # レア度情報
        rarity_info = self.pet_collection.get_rarity_info(pet_info.rarity)
        self.rarity_label.set_text(f"レア度: {rarity_info['name']}")
        
        # 救助ステータス
        if rescue_record and rescue_record.rescued:
            status_text = "✓ 救助済み"
            status_color = "#4CAF50"
        else:
            status_text = "✗ 未救助"
            status_color = "#F44336"
        
        self.rescue_status_label.set_text(status_text)
        
        # 説明文
        self.description_text.set_text(pet_info.description)
        
        # 特徴
        characteristics_html = "<br>".join([f"• {char}" for char in pet_info.characteristics])
        self.characteristics_text.set_text(characteristics_html)
        
        # 救助情報
        if rescue_record and rescue_record.rescued:
            rescue_date = datetime.fromisoformat(rescue_record.rescue_date).strftime("%Y/%m/%d %H:%M")
            rescue_info_html = f"""
            <b>救助日時:</b> {rescue_date}<br>
            <b>救助場所:</b> {rescue_record.rescue_location}<br>
            <b>所要時間:</b> {rescue_record.rescue_time_spent}秒<br>
            <b>挑戦回数:</b> {rescue_record.rescue_attempts}回
            """
        else:
            rescue_info_html = """
            <b>状態:</b> 未救助<br>
            <b>発見場所:</b><br>
            """ + "<br>".join([f"• {loc}" for loc in pet_info.found_locations])
        
        self.rescue_info_text.set_text(rescue_info_html)
        
        # ヒント
        hints_html = "<br>".join([f"• {hint}" for hint in pet_info.rescue_hints])
        self.hints_text.set_text(hints_html)
        
        # 表示
        self.is_visible = True
        self.container.visible = True
    
    def hide(self) -> None:
        """詳細表示を非表示"""
        self.is_visible = False
        if self.container:
            self.container.visible = False
        self.current_pet_id = None
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """イベントを処理"""
        if not self.is_visible:
            return False
        
        if event.type == pygame_gui.UI_BUTTON_PRESSED:
            if event.ui_element == self.close_button:
                self.hide()
                return True
        
        return False
    
    def update(self, time_delta: float) -> None:
        """UIを更新"""
        pass
    
    def draw(self, surface: pygame.Surface) -> None:
        """UIを描画"""
        if self.is_visible:
            # ペット画像を描画（画像ファイルがある場合）
            if self.current_pet_id:
                pet_info = self.pet_collection.get_pet_info(self.current_pet_id)
                if pet_info and hasattr(pet_info, 'image_path'):
                    try:
                        # 画像を読み込んで描画
                        pet_image = pygame.image.load(pet_info.image_path)
                        # 画像をリサイズ
                        pet_image = pygame.transform.scale(pet_image, (140, 140))
                        
                        # 画像パネルの位置を取得
                        panel_rect = self.pet_image.relative_rect
                        container_rect = self.container.relative_rect
                        image_x = container_rect.x + panel_rect.x + 5
                        image_y = container_rect.y + panel_rect.y + 5
                        
                        surface.blit(pet_image, (image_x, image_y))
                    except (pygame.error, FileNotFoundError):
                        # 画像が読み込めない場合はプレースホルダーを描画
                        panel_rect = self.pet_image.relative_rect
                        container_rect = self.container.relative_rect
                        placeholder_rect = pygame.Rect(
                            container_rect.x + panel_rect.x + 5,
                            container_rect.y + panel_rect.y + 5,
                            140, 140
                        )
                        pygame.draw.rect(surface, (200, 200, 200), placeholder_rect)
                        pygame.draw.rect(surface, (100, 100, 100), placeholder_rect, 2)
                        
                        # "画像なし"テキストを描画
                        font = pygame.font.Font(None, 24)
                        text = font.render("画像なし", True, (100, 100, 100))
                        text_rect = text.get_rect(center=placeholder_rect.center)
                        surface.blit(text, text_rect)
