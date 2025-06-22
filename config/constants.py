"""
ゲーム定数定義

ゲーム全体で使用する定数を定義
"""

# ゲーム基本情報
GAME_TITLE = "ミステリー・ペット・レスキュー"
GAME_VERSION = "1.0.0"
GAME_AUTHOR = "Pet Rescue Team"

# 画面設定
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
MIN_SCREEN_WIDTH = 800
MIN_SCREEN_HEIGHT = 600
TARGET_FPS = 60
MIN_FPS = 30
MAX_FPS = 120

# 色定義 (RGB)
COLOR_WHITE = (255, 255, 255)
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)
COLOR_GREEN = (0, 255, 0)
COLOR_BLUE = (0, 0, 255)
COLOR_YELLOW = (255, 255, 0)
COLOR_GRAY = (128, 128, 128)
COLOR_LIGHT_GRAY = (192, 192, 192)
COLOR_DARK_GRAY = (64, 64, 64)

# UI色
UI_BACKGROUND = (240, 240, 240)
UI_BORDER = (100, 100, 100)
UI_TEXT = (50, 50, 50)
UI_HIGHLIGHT = (100, 150, 255)
UI_BUTTON = (200, 200, 200)
UI_BUTTON_HOVER = (220, 220, 220)
UI_BUTTON_PRESSED = (180, 180, 180)

# ゲームプレイ定数
PLAYER_SPEED = 300  # ピクセル/秒（適切な移動速度）
PET_SPEED = 150     # ピクセル/秒
NPC_SPEED = 100     # ピクセル/秒

# マップ設定
TILE_SIZE = 32
MAP_WIDTH = 32
MAP_HEIGHT = 24

# ペット種類
PET_TYPES = [
    "dog",      # 犬
    "cat",      # 猫
    "rabbit",   # うさぎ
    "hamster",  # ハムスター
    "bird",     # 鳥
    "fish",     # 魚
    "turtle",   # カメ
    "ferret"    # フェレット
]

# ペット状態
PET_STATE_LOST = "lost"         # 迷子
PET_STATE_FOUND = "found"       # 発見済み
PET_STATE_RESCUED = "rescued"   # 救助済み
PET_STATE_RETURNED = "returned" # 返却済み

# ゲーム状態
GAME_STATE_MENU = "menu"
GAME_STATE_PLAYING = "playing"
GAME_STATE_PAUSED = "paused"
GAME_STATE_INVENTORY = "inventory"
GAME_STATE_COLLECTION = "collection"
GAME_STATE_SETTINGS = "settings"
GAME_STATE_QUIT = "quit"

# シーン定数
SCENE_TITLE = "title"
SCENE_MAIN_MENU = "main_menu"
SCENE_GAME_WORLD = "game_world"
SCENE_MINI_GAME = "mini_game"
SCENE_COLLECTION = "collection"
SCENE_SETTINGS = "settings"

# 入力キー
KEY_UP = "up"
KEY_DOWN = "down"
KEY_LEFT = "left"
KEY_RIGHT = "right"
KEY_ACTION = "action"
KEY_CANCEL = "cancel"
KEY_MENU = "menu"
KEY_INVENTORY = "inventory"

# ファイルパス
FONT_JAPANESE = "assets/fonts/japanese.ttf"
FONT_ENGLISH = "assets/fonts/english.ttf"

# 音声設定
AUDIO_FREQUENCY = 44100
AUDIO_SIZE = -16
AUDIO_CHANNELS = 2
AUDIO_BUFFER = 512

# デバッグ設定
DEBUG_SHOW_FPS = True
DEBUG_SHOW_COORDINATES = False
DEBUG_SHOW_COLLISION = False
