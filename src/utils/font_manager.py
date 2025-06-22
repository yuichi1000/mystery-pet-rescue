"""
フォント管理システム
日本語対応フォントの管理
"""

import pygame
import os
from typing import Optional, Dict, List

class FontManager:
    """フォント管理クラス"""
    
    def __init__(self):
        self.fonts: Dict[str, pygame.font.Font] = {}
        self.japanese_font_path = None
        self._find_japanese_font()
    
    def _find_japanese_font(self):
        """日本語フォントを検索"""
        # macOS用の日本語フォントパス
        macos_fonts = [
            "/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc",
            "/System/Library/Fonts/Hiragino Sans GB.ttc",
            "/Library/Fonts/ヒラギノ角ゴ ProN W3.otf",
            "/System/Library/Fonts/Arial Unicode MS.ttf"
        ]
        
        # Linux用の日本語フォントパス
        linux_fonts = [
            "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
        ]
        
        # Windows用の日本語フォントパス
        windows_fonts = [
            "C:/Windows/Fonts/msgothic.ttc",
            "C:/Windows/Fonts/meiryo.ttc",
            "C:/Windows/Fonts/YuGothM.ttc"
        ]
        
        all_fonts = macos_fonts + linux_fonts + windows_fonts
        
        for font_path in all_fonts:
            if os.path.exists(font_path):
                self.japanese_font_path = font_path
                print(f"✅ 日本語フォント発見: {font_path}")
                return
        
        print("⚠️ 日本語フォントが見つかりません。デフォルトフォントを使用します。")
    
    def get_font(self, size: int, bold: bool = False) -> pygame.font.Font:
        """フォントを取得"""
        font_key = f"{size}_{bold}"
        
        if font_key not in self.fonts:
            if self.japanese_font_path:
                try:
                    self.fonts[font_key] = pygame.font.Font(self.japanese_font_path, size)
                except:
                    print(f"⚠️ 日本語フォント読み込み失敗: {self.japanese_font_path}")
                    self.fonts[font_key] = pygame.font.Font(None, size)
            else:
                self.fonts[font_key] = pygame.font.Font(None, size)
        
        return self.fonts[font_key]
    
    def render_text(self, text: str, size: int, color: tuple, bold: bool = False) -> pygame.Surface:
        """テキストをレンダリング"""
        font = self.get_font(size, bold)
        return font.render(text, True, color)
    
    def render_multiline_text(self, text: str, size: int, color: tuple, 
                            max_width: int = None, line_spacing: int = 5) -> List[pygame.Surface]:
        """複数行テキストをレンダリング（行間調整付き）"""
        font = self.get_font(size)
        lines = text.split('\n')
        surfaces = []
        
        for line in lines:
            if max_width and font.size(line)[0] > max_width:
                # 長い行を分割
                words = line.split(' ')
                current_line = ""
                
                for word in words:
                    test_line = current_line + (" " if current_line else "") + word
                    if font.size(test_line)[0] <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            surfaces.append(font.render(current_line, True, color))
                        current_line = word
                
                if current_line:
                    surfaces.append(font.render(current_line, True, color))
            else:
                surfaces.append(font.render(line, True, color))
        
        return surfaces
    
    def get_text_size(self, text: str, size: int, bold: bool = False) -> tuple:
        """テキストサイズを取得"""
        font = self.get_font(size, bold)
        return font.size(text)
    
    def get_multiline_text_height(self, text: str, size: int, line_spacing: int = 5) -> int:
        """複数行テキストの高さを取得"""
        lines = text.split('\n')
        font = self.get_font(size)
        line_height = font.get_height()
        return len(lines) * line_height + (len(lines) - 1) * line_spacing

# グローバルフォントマネージャー
_font_manager = None

def get_font_manager() -> FontManager:
    """フォントマネージャーのシングルトンインスタンスを取得"""
    global _font_manager
    if _font_manager is None:
        _font_manager = FontManager()
    return _font_manager
