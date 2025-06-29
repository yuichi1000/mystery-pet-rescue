#!/usr/bin/env python3
"""
最小限のWeb版テスト
メニューが表示されるかの緊急確認用
"""

import asyncio
import pygame

class MinimalWebTest:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Web Test - Menu Check")
        self.clock = pygame.time.Clock()
        self.running = True
        self.font = pygame.font.Font(None, 36)
        
    async def run(self):
        while self.running:
            # イベント処理
            pygame.event.pump()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        print("🎮 スペースキー押下 - ゲーム動作中")
            
            # 描画
            self.screen.fill((0, 50, 100))
            
            # メニュー表示
            title = self.font.render("Mystery Pet Rescue - Web Test", True, (255, 255, 255))
            self.screen.blit(title, (200, 200))
            
            menu = self.font.render("Press SPACE to test", True, (255, 255, 0))
            self.screen.blit(menu, (250, 300))
            
            status = self.font.render("Menu is working!", True, (0, 255, 0))
            self.screen.blit(status, (280, 400))
            
            pygame.display.flip()
            self.clock.tick(30)
            await asyncio.sleep(0)
        
        pygame.quit()

async def main():
    print("🧪 最小限Web版テスト開始")
    game = MinimalWebTest()
    await game.run()
    print("✅ テスト完了")

if __name__ == "__main__":
    asyncio.run(main())
