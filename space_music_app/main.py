import pygame
import sys
from sound_manager import SoundManager
from level_manager import LevelManager
import random

class Button:
    def __init__(self, x, y, width, height, text, color, locked=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = color
        self.color = (100, 100, 100) if locked else color
        self.hover_color = (min(color[0] + 30, 255), min(color[1] + 30, 255), min(color[2] + 30, 255))
        self.is_hovered = False
        self.locked = locked

    def draw(self, screen):
        if not self.locked and self.is_hovered:
            color = self.hover_color
        else:
            color = self.color
            
        pygame.draw.rect(screen, color, self.rect, border_radius=12)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 2, border_radius=12)
        
        font = pygame.font.Font(None, 36)
        text_surface = font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
        if self.locked:
            lock_font = pygame.font.Font(None, 24)
            lock_text = lock_font.render("🔒", True, (255, 255, 255))
            lock_rect = lock_text.get_rect(topright=(self.rect.right - 5, self.rect.top + 5))
            screen.blit(lock_text, lock_rect)

    def handle_event(self, event):
        if self.locked:
            return False
        if event.type == pygame.MOUSEMOTION:
            self.is_hovered = self.rect.collidepoint(event.pos)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.is_hovered and self.rect.collidepoint(event.pos):
                return True
        return False

class Menu:
    def __init__(self, screen, sound_manager):
        self.screen = screen
        self.state = "main"
        self.max_unlocked_level = 1
        self.sound_manager = sound_manager
        
        # Initialize fonts
        self.title_font = pygame.font.Font(None, 74)
        self.subtitle_font = pygame.font.Font(None, 36)
        
        # Stars background
        self.stars = [(random.randint(0, 800), random.randint(0, 600), random.random()) 
                     for _ in range(200)]
        
        # Main menu buttons
        self.main_buttons = [
            Button(300, 250, 200, 50, "Play", (100, 100, 200)),
            Button(300, 320, 200, 50, "Levels", (100, 150, 100)),
            Button(300, 390, 200, 50, "Quit", (200, 100, 100))
        ]
        
        # Level buttons will be created in create_level_buttons
        self.level_buttons = []
        self.create_level_buttons()
        
        # Back button
        self.back_button = Button(50, 50, 100, 40, "Back", (150, 150, 150))

    def create_level_buttons(self):
        self.level_buttons = []
        button_size = 120
        start_x = 230
        start_y = 200
        spacing = 140
        
        galaxies = ["Milky Way", "Andromeda", "Triangulum"]
        for i in range(3):  # Rows (Galaxies)
            galaxy_levels = []
            for j in range(3):  # Columns (Levels per galaxy)
                level_num = i * 3 + j + 1
                x = start_x + j * spacing
                y = start_y + i * spacing
                locked = level_num > self.max_unlocked_level
                button = Button(x, y, button_size, button_size, 
                              f"Level {level_num}", 
                              (100 + i * 50, 100 + j * 30, 150),
                              locked=locked)
                galaxy_levels.append(button)
            self.level_buttons.append(galaxy_levels)

    def draw_stars(self):
        for x, y, brightness in self.stars:
            color = int(255 * brightness)
            pygame.draw.circle(self.screen, (color, color, color), (int(x), int(y)), 1)

    def draw_galaxy_labels(self):
        galaxies = ["Milky Way", "Andromeda", "Triangulum"]
        for i, galaxy in enumerate(galaxies):
            text = self.subtitle_font.render(galaxy, True, (200, 200, 255))
            text_rect = text.get_rect(midleft=(50, 260 + i * 140))
            self.screen.blit(text, text_rect)

    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                
                if self.state == "main":
                    for button in self.main_buttons:
                        if button.handle_event(event):
                            if button.text == "Play":
                                self.sound_manager.play_startup_sound()
                                pygame.time.wait(1000)  # Wait for sound to play
                                return ("start", 1)
                            elif button.text == "Levels":
                                self.state = "levels"
                            elif button.text == "Quit":
                                return "quit"
                
                elif self.state == "levels":
                    if self.back_button.handle_event(event):
                        self.state = "main"
                    for i, galaxy_levels in enumerate(self.level_buttons):
                        for j, button in enumerate(galaxy_levels):
                            if button.handle_event(event):
                                level_num = i * 3 + j + 1
                                if level_num <= self.max_unlocked_level:
                                    self.sound_manager.play_startup_sound()
                                    pygame.time.wait(1000)  # Wait for sound to play
                                    return ("start", level_num)

            self.screen.fill((0, 0, 0))
            self.draw_stars()

            title = self.title_font.render("Space Music Explorer", True, (255, 255, 255))
            title_rect = title.get_rect(center=(400, 100))
            self.screen.blit(title, title_rect)

            if self.state == "main":
                for button in self.main_buttons:
                    button.draw(self.screen)
            
            elif self.state == "levels":
                self.back_button.draw(self.screen)
                self.draw_galaxy_labels()
                for galaxy_levels in self.level_buttons:
                    for button in galaxy_levels:
                        button.draw(self.screen)

            pygame.display.flip()

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
        
        # Menu button during gameplay
        self.menu_button = Button(20, 20, 100, 40, "Menu", (150, 150, 150))
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        
        # Stars background
        self.stars = [(random.randint(0, 800), random.randint(0, 600), random.random()) 
                     for _ in range(200)]
        
        # Level completion message timer
        self.completion_message = None
        self.message_timer = 0
        
        # Game completion state
        self.game_completed = False

    def draw_stars(self):
        for x, y, brightness in self.stars:
            color = int(255 * brightness)
            pygame.draw.circle(self.screen, (color, color, color), (int(x), int(y)), 1)

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
        self.current_planets = self.level_manager.generate_level(
            self.sound_manager.notes, starting_level
        )
        
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            self.menu_button.is_hovered = self.menu_button.rect.collidepoint(mouse_pos)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return False  # Exit game
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # Check menu button first
                    if self.menu_button.is_hovered:
                        return True  # Return to menu
                    
                    # Check planet clicks
                    pos = pygame.mouse.get_pos()
                    for planet in self.current_planets:
                        if planet.rect.collidepoint(pos):
                            if not planet.clicked:
                                planet.clicked = True
                                planet.showing_fact = True
                                self.sound_manager.play_note(planet.note)
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
                    self.current_planets = self.level_manager.generate_level(
                        self.sound_manager.notes,
                        self.level_manager.current_level
                    )

            self.screen.fill(self.BLACK)
            self.draw_stars()
            
            # Draw all planets
            for planet in self.current_planets:
                planet.draw(self.screen)
            
            # Draw UI elements
            self.menu_button.draw(self.screen)
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