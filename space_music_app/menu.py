# menu.py
import pygame
import random

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
        self.stars = [(random.randint(0, 800), random.randint(0, 600), 
                      random.random()) for _ in range(200)]
        
        # Main menu buttons
        self.main_buttons = [
            Button(300, 250, 200, 50, "Play", (100, 100, 200)),
            Button(300, 320, 200, 50, "Levels", (100, 150, 100)),
            Button(300, 390, 200, 50, "Settings", (150, 150, 150)),
            Button(300, 460, 200, 50, "Quit", (200, 100, 100))
        ]
        
        # Level buttons
        self.level_buttons = []
        self.create_level_buttons()
        
        # Back button
        self.back_button = Button(50, 50, 100, 40, "Back", (150, 150, 150))
        
        # Volume control
        self.volume = 0.5
        self.volume_rect = pygame.Rect(300, 300, 200, 20)
        self.volume_handle = pygame.Rect(300 + (200 * self.volume) - 10, 
                                       295, 20, 30)
        self.dragging_volume = False

    def create_level_buttons(self):
        button_size = 120
        start_x = 230
        start_y = 200
        spacing = 140
        
        for i in range(3):  # 3 rows
            row = []
            for j in range(3):  # 3 columns
                level_num = i * 3 + j + 1
                x = start_x + j * spacing
                y = start_y + i * spacing
                locked = level_num > self.max_unlocked_level
                button = Button(x, y, button_size, button_size, 
                              f"Level {level_num}", 
                              (100 + i * 50, 100 + j * 30, 150),
                              locked=locked)
                row.append(button)
            self.level_buttons.append(row)

    def draw_stars(self):
        for x, y, brightness in self.stars:
            color = int(255 * brightness)
            pygame.draw.circle(self.screen, (color, color, color), 
                             (int(x), int(y)), 1)

    def draw_interface(self):
        # Draw title
        title = self.title_font.render("Space Music Explorer", 
                                     True, (255, 255, 255))
        title_rect = title.get_rect(center=(400, 100))
        self.screen.blit(title, title_rect)
        
        if self.state == "main":
            for button in self.main_buttons:
                button.draw(self.screen)
        elif self.state == "levels":
            self.back_button.draw(self.screen)
            for row in self.level_buttons:
                for button in row:
                    button.draw(self.screen)
        elif self.state == "settings":
            self.back_button.draw(self.screen)
            self.draw_settings()

    def draw_settings(self):
        # Draw volume slider
        pygame.draw.rect(self.screen, (100, 100, 100), self.volume_rect)
        pygame.draw.rect(self.screen, (150, 150, 255), 
                        (self.volume_rect.x, self.volume_rect.y, 
                         self.volume_rect.width * self.volume, 
                         self.volume_rect.height))
        pygame.draw.rect(self.screen, (200, 200, 255), self.volume_handle)
        
        # Draw volume label
        volume_label = self.subtitle_font.render(
            f"Volume: {int(self.volume * 100)}%", 
            True, (255, 255, 255))
        self.screen.blit(volume_label, (300, 250))

    def handle_settings(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.volume_handle.collidepoint(event.pos):
                self.dragging_volume = True
        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging_volume = False
        elif event.type == pygame.MOUSEMOTION and self.dragging_volume:
            x = max(self.volume_rect.left, 
                   min(event.pos[0], self.volume_rect.right))
            self.volume = (x - self.volume_rect.left) / self.volume_rect.width
            self.volume_handle.centerx = x
            self.sound_manager.set_volume(self.volume)

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
                                pygame.time.wait(1000)
                                return ("start", 1)
                            elif button.text == "Levels":
                                self.state = "levels"
                            elif button.text == "Settings":
                                self.state = "settings"
                            elif button.text == "Quit":
                                return "quit"
                
                elif self.state == "levels":
                    if self.back_button.handle_event(event):
                        self.state = "main"
                    for i, row in enumerate(self.level_buttons):
                        for j, button in enumerate(row):
                            if button.handle_event(event):
                                level_num = i * 3 + j + 1
                                if level_num <= self.max_unlocked_level:
                                    self.sound_manager.play_startup_sound()
                                    pygame.time.wait(1000)
                                    return ("start", level_num)
                
                elif self.state == "settings":
                    if self.back_button.handle_event(event):
                        self.state = "main"
                    self.handle_settings(event)
            
            self.screen.fill((0, 0, 20))  # Dark blue background
            self.draw_stars()
            self.draw_interface()
            pygame.display.flip()


class Button:
    def __init__(self, x, y, width, height, text, color, locked=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.base_color = color
        self.color = (100, 100, 100) if locked else color
        self.hover_color = (min(color[0] + 30, 255), 
                          min(color[1] + 30, 255), 
                          min(color[2] + 30, 255))
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
            lock_rect = lock_text.get_rect(
                topright=(self.rect.right - 5, self.rect.top + 5))
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