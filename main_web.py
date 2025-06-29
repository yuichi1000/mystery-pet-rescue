import asyncio
import pygame
import sys
import os

# Web版環境設定
os.environ['WEB_VERSION'] = '1'
os.environ['SDL_IME_SHOW_UI'] = '0'

# プロジェクトルートを追加
sys.path.insert(0, os.path.dirname(__file__))

class WebGame:
    def __init__(self):
        pygame.init()
        pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=1024)
        
        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Mystery Pet Rescue")
        
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_flow = None
    
    def initialize_game(self):
        try:
            from src.core.game_flow import GameFlowManager
            self.game_flow = GameFlowManager(self.screen)
            return True
        except Exception as e:
            print(f"ゲーム初期化エラー: {e}")
            return False
    
    async def run(self):
        if not self.initialize_game():
            await self.show_error()
            return
        
        while self.running:
            # イベント処理
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    try:
                        result = self.game_flow.handle_event(event)
                        if result == "quit":
                            self.running = False
                    except:
                        pass
            
            # 更新
            time_delta = self.clock.tick(30) / 1000.0
            try:
                result = self.game_flow.update(time_delta)
                if result == "quit":
                    self.running = False
            except:
                pass
            
            # 描画
            self.screen.fill((40, 40, 40))
            try:
                self.game_flow.draw(self.screen)
            except:
                pass
            
            pygame.display.flip()
            await asyncio.sleep(0)
    
    async def show_error(self):
        font = pygame.font.Font(None, 48)
        
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
            
            self.screen.fill((20, 30, 50))
            
            text = font.render("Mystery Pet Rescue", True, (255, 255, 255))
            text_rect = text.get_rect(center=(640, 300))
            self.screen.blit(text, text_rect)
            
            text = font.render("Web Version", True, (200, 200, 200))
            text_rect = text.get_rect(center=(640, 360))
            self.screen.blit(text, text_rect)
            
            pygame.display.flip()
            self.clock.tick(30)
            await asyncio.sleep(0)

async def main():
    game = WebGame()
    await game.run()

if __name__ == "__main__":
    asyncio.run(main())