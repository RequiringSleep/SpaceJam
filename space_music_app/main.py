# main.py
import pygame
import sys
from menu import Menu
from game import Game  # Add this import
from sound_manager import SoundManager

class SpaceMusicExplorer:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Space Music Explorer")
        
        # Initialize sound system
        self.sound_manager = SoundManager()
        
        # Initialize states
        self.menu = Menu(self.screen, self.sound_manager)
        self.game = None
        self.state = "menu"
        
        # FPS control
        self.clock = pygame.time.Clock()
        
    def run(self):
        while True:
            if self.state == "menu":
                result = self.menu.run()
                if result == "quit":
                    break
                elif isinstance(result, tuple) and result[0] == "start":
                    self.game = Game(self.screen, self.sound_manager, result[1])
                    self.state = "game"
                    
            elif self.state == "game":
                result = self.game.run()
                if result == "quit":
                    break
                elif result == "menu":
                    self.state = "menu"
                    self.sound_manager.stop_all_sounds()
                elif isinstance(result, tuple) and result[0] == "level_complete":
                    self.menu.max_unlocked_level = max(
                        self.menu.max_unlocked_level, 
                        result[1] + 1
                    )
                    self.state = "menu"
                    
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = SpaceMusicExplorer()
    game.run()