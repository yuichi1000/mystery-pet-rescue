"""
アセット管理システム
画像・音声・フォントなどのリソース管理
"""

import pygame
import os
from typing import Dict, Optional, Tuple, List
from pathlib import Path
import json

class AssetManager:
    """アセット管理クラス"""
    
    def __init__(self):
        self.images: Dict[str, pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.fonts: Dict[str, pygame.font.Font] = {}
        
        # アセットパス
        self.assets_root = Path("assets")
        self.images_path = self.assets_root / "images"
        self.sounds_path = self.assets_root / "sounds"
        self.fonts_path = self.assets_root / "fonts"
        
        # 画像スケール設定
        self.default_scale = (64, 64)
        self.tile_scale = (64, 64)
        self.character_scale = (64, 64)
        self.pet_scale = (48, 48)
        
        print("🎨 アセットマネージャー初期化完了")
    
    def load_image(self, path: str, scale: Optional[Tuple[int, int]] = None, 
                   colorkey: Optional[Tuple[int, int, int]] = None) -> Optional[pygame.Surface]:
        """画像を読み込み（透過処理済み画像用）"""
        full_path = self.images_path / path
        
        if path in self.images:
            return self.images[path]
        
        try:
            if not full_path.exists():
                print(f"⚠️ 画像ファイルが見つかりません: {full_path}")
                return self._create_placeholder_image(scale or self.default_scale)
            
            # PNG画像を透過情報付きで読み込み
            image = pygame.image.load(str(full_path))
            
            # 透過処理
            if image.get_alpha() is not None:
                # アルファチャンネル付きPNG
                image = image.convert_alpha()
            else:
                # 通常のPNG - カラーキー透過
                image = image.convert()
                if colorkey:
                    image.set_colorkey(colorkey)
                else:
                    # 左上ピクセルの色を透過色として使用
                    image.set_colorkey(image.get_at((0, 0)))
            
            # スケール調整
            if scale:
                image = pygame.transform.smoothscale(image, scale)
            
            self.images[path] = image
            return image
            
        except Exception as e:
            print(f"❌ 画像読み込みエラー {path}: {e}")
            return self._create_placeholder_image(scale or self.default_scale)
    
    def _create_placeholder_image(self, size: Tuple[int, int]) -> pygame.Surface:
        """プレースホルダー画像を作成（透過対応）"""
        surface = pygame.Surface(size, pygame.SRCALPHA)
        surface.fill((255, 0, 255))  # マゼンタ背景
        surface.set_colorkey((255, 0, 255))  # マゼンタを透過色に設定
        
        # 枠線を描画
        pygame.draw.rect(surface, (0, 0, 0), surface.get_rect(), 2)
        
        return surface
    
    def load_character_sprites(self, character_name: str) -> Dict[str, pygame.Surface]:
        """キャラクタースプライトを読み込み"""
        sprites = {}
        directions = ["front", "back", "left", "right"]
        
        for direction in directions:
            sprite_path = f"characters/{character_name}_{direction}.png"
            sprite = self.load_image(sprite_path, self.character_scale)
            if sprite:
                sprites[direction] = sprite
        
        return sprites
    
    def load_pet_sprites(self, pet_id: str) -> Dict[str, pygame.Surface]:
        """ペットスプライトを読み込み"""
        sprites = {}
        directions = ["front", "back", "left", "right"]
        
        for direction in directions:
            sprite_path = f"pets/{pet_id}_{direction}.png"
            sprite = self.load_image(sprite_path, self.pet_scale)
            if sprite:
                sprites[direction] = sprite
        
        return sprites
    
    def load_tile_set(self) -> Dict[str, pygame.Surface]:
        """タイルセットを読み込み"""
        tiles = {}
        tile_names = [
            "grass_tile",
            "ground_tile", 
            "concrete_tile",
            "rock_tile",
            "stone_wall_tile",
            "tree_tile",
            "water_tile"
        ]
        
        for tile_name in tile_names:
            tile_path = f"tiles/{tile_name}.png"
            tile = self.load_image(tile_path, self.tile_scale)
            if tile:
                tiles[tile_name.replace("_tile", "")] = tile
        
        return tiles
    
    def load_ui_images(self) -> Dict[str, pygame.Surface]:
        """UI画像を読み込み"""
        ui_images = {}
        ui_path = self.images_path / "ui"
        
        if ui_path.exists():
            for image_file in ui_path.glob("*.png"):
                image_name = image_file.stem
                image = self.load_image(f"ui/{image_file.name}")
                if image:
                    ui_images[image_name] = image
        
        return ui_images
    
    def load_background_images(self) -> Dict[str, pygame.Surface]:
        """背景画像を読み込み"""
        backgrounds = {}
        bg_names = ["building_house", "nature_bush"]
        
        for bg_name in bg_names:
            bg_path = f"backgrounds/{bg_name}.png"
            bg_image = self.load_image(bg_path)
            if bg_image:
                backgrounds[bg_name] = bg_image
        
        return backgrounds
    
    def load_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        """音声を読み込み"""
        if not pygame.mixer.get_init():
            print("⚠️ 音声システムが初期化されていません")
            return None
        
        full_path = self.sounds_path / path
        
        if path in self.sounds:
            return self.sounds[path]
        
        try:
            if not full_path.exists():
                print(f"⚠️ 音声ファイルが見つかりません: {full_path}")
                return None
            
            sound = pygame.mixer.Sound(str(full_path))
            self.sounds[path] = sound
            return sound
            
        except Exception as e:
            print(f"❌ 音声読み込みエラー {path}: {e}")
            return None
    
    def load_font(self, path: str, size: int) -> Optional[pygame.font.Font]:
        """フォントを読み込み"""
        font_key = f"{path}_{size}"
        
        if font_key in self.fonts:
            return self.fonts[font_key]
        
        try:
            full_path = self.fonts_path / path
            if full_path.exists():
                font = pygame.font.Font(str(full_path), size)
            else:
                font = pygame.font.Font(None, size)
            
            self.fonts[font_key] = font
            return font
            
        except Exception as e:
            print(f"❌ フォント読み込みエラー {path}: {e}")
            return pygame.font.Font(None, size)
    
    def preload_all_assets(self):
        """すべてのアセットを事前読み込み"""
        print("🔄 アセット事前読み込み開始...")
        
        # キャラクタースプライト
        player_sprites = self.load_character_sprites("player")
        print(f"✅ プレイヤースプライト読み込み: {len(player_sprites)}個")
        
        # ペットスプライト
        pet_sprites = {}
        pet_ids = ["pet_cat_001", "pet_dog_001"]
        for pet_id in pet_ids:
            sprites = self.load_pet_sprites(pet_id)
            pet_sprites[pet_id] = sprites
            print(f"✅ {pet_id}スプライト読み込み: {len(sprites)}個")
        
        # タイルセット
        tiles = self.load_tile_set()
        print(f"✅ タイルセット読み込み: {len(tiles)}個")
        
        # 背景画像
        backgrounds = self.load_background_images()
        print(f"✅ 背景画像読み込み: {len(backgrounds)}個")
        
        # UI画像
        ui_images = self.load_ui_images()
        print(f"✅ UI画像読み込み: {len(ui_images)}個")
        
        print("🎨 アセット事前読み込み完了")
        
        return {
            "player": player_sprites,
            "pets": pet_sprites,
            "tiles": tiles,
            "backgrounds": backgrounds,
            "ui": ui_images
        }
    
    def get_image(self, path: str) -> Optional[pygame.Surface]:
        """画像を取得（未読み込みの場合は自動読み込み）"""
        if path not in self.images:
            print(f"🔄 画像を自動読み込み: {path}")
            return self.load_image(path)
        return self.images.get(path)
    
    def get_sound(self, path: str) -> Optional[pygame.mixer.Sound]:
        """読み込み済み音声を取得"""
        return self.sounds.get(path)
    
    def get_font(self, path: str, size: int) -> Optional[pygame.font.Font]:
        """読み込み済みフォントを取得"""
        font_key = f"{path}_{size}"
        return self.fonts.get(font_key)
    
    def clear_cache(self):
        """キャッシュをクリア"""
        self.images.clear()
        self.sounds.clear()
        self.fonts.clear()
        print("🧹 アセットキャッシュクリア完了")
    
    def get_asset_info(self) -> Dict[str, int]:
        """アセット情報を取得"""
        return {
            "images": len(self.images),
            "sounds": len(self.sounds),
            "fonts": len(self.fonts)
        }

# グローバルアセットマネージャー
_asset_manager = None

def get_asset_manager() -> AssetManager:
    """アセットマネージャーのシングルトンインスタンスを取得"""
    global _asset_manager
    if _asset_manager is None:
        _asset_manager = AssetManager()
    return _asset_manager
