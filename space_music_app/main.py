import pygame
import sys
from sound_manager import SoundManager
from level_manager import LevelManager
from menu import Menu

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Space Music Explorer")
        self.clock = pygame.time.Clock()
        
        # Initialize managers
        self.sound_manager = SoundManager()
        self.level_manager = LevelManager()
        
        # Initialize menu with sound manager
        self.menu = Menu(self.screen, self.sound_manager)
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        
        # Level completion message timer
        self.completion_message = None
        self.message_timer = 0
        
        # Game completion state
        self.game_completed = False

    def show_completion_message(self, message, duration=3000):
        self.completion_message = message
        self.message_timer = pygame.time.get_ticks()

    def draw_completion_message(self):
        if self.completion_message:
            current_time = pygame.time.get_ticks()
            if current_time - self.message_timer < 3000:
                overlay = pygame.Surface((800, 100))
                overlay.set_alpha(180)
                overlay.fill((0, 0, 0))
                self.screen.blit(overlay, (0, 250))
                
                font = pygame.font.Font(None, 48)
                text = font.render(self.completion_message, True, (255, 255, 255))
                text_rect = text.get_rect(center=(400, 300))
                self.screen.blit(text, text_rect)
            else:
                self.completion_message = None

    def draw_level_indicator(self, current_level):
        font = pygame.font.Font(None, 36)
        level_text = f"Level {current_level}"
        text = font.render(level_text, True, (255, 255, 255))
        text_rect = text.get_rect(topright=(750, 50))
        self.screen.blit(text, text_rect)

    def run_game(self, starting_level=1):
        self.level_manager.current_level = starting_level
        self.current_planets = self.level_manager.generate_level(starting_level)
        
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = pygame.mouse.get_pos()
                    for planet in self.current_planets:
                        if planet.rect.collidepoint(pos):
                            if not planet.clicked:
                                planet.clicked = True
                                planet.showing_fact = True
                                self.sound_manager.play_note(planet)
                            else:
                                planet.showing_fact = not planet.showing_fact
                        else:
                            planet.showing_fact = False
                            
            if self.level_manager.is_level_complete(self.current_planets):
                if self.level_manager.current_level >= 9:  # All levels completed
                    if not self.game_completed:
                        self.game_completed = True
                        self.show_completion_message("Congratulations! You've completed all levels!")
                        self.sound_manager.play_completion_melody()
                        pygame.time.wait(3000)  # Wait for message to display
                        return True  # Return to menu
                else:
                    self.show_completion_message(f"Level {self.level_manager.current_level} Complete!")
                    self.sound_manager.play_completion_melody()
                    self.level_manager.advance_level()
                    self.menu.max_unlocked_level = min(9, self.menu.max_unlocked_level + 1)
                    self.menu.create_level_buttons()
                    self.current_planets = self.level_manager.generate_level(self.level_manager.current_level)

            self.screen.fill(self.BLACK)
            
            # Draw all planets
            for planet in self.current_planets:
                planet.draw(self.screen)
            
            # Draw UI elements
            self.draw_level_indicator(self.level_manager.current_level)
            self.draw_completion_message()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        return False

    def run(self):
        running = True
        while running:
            result = self.menu.run()
            if isinstance(result, tuple):
                action, level = result
                if action == "start":
                    # Run the game and check if we should return to menu
                    returning_to_menu = self.run_game(level)
                    if not returning_to_menu:
                        running = False
            elif result == "quit":
                running = False
        
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()