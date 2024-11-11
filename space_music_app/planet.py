import pygame
import random
import math

class Planet:
    def __init__(self, x, y, size, sound_manager, name="Planet"):
        self.x = x
        self.y = y
        self.size = size
        self.sound_manager = sound_manager
        self.name = name
        self.clicked = False
        self.showing_fact = False
        self.note = random.randint(0, 7)  # Assign a random note to each planet
        
        # Create planet colors and visuals
        self.generate_planet_theme()
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)
        
        # Educational facts
        self.facts = [
            "Mercury: The smallest planet, closest to the Sun!",
            "Venus: The hottest planet due to its thick atmosphere!",
            "Earth: Our home planet with liquid water on its surface!",
            "Mars: The Red Planet with the largest volcano in our system!",
            "Jupiter: The largest planet with a giant red storm!",
            "Saturn: Known for its beautiful ring system!",
            "Uranus: The planet that rotates on its side!",
            "Neptune: The windiest planet with supersonic storms!"
        ]
        self.fact = random.choice(self.facts)

    def generate_planet_theme(self):
        """Generate planet colors"""
        base_colors = [
            (255, 150, 50),   # Orange
            (50, 180, 255),   # Blue
            (255, 100, 255),  # Pink
            (130, 255, 100),  # Green
            (255, 200, 50),   # Yellow
            (180, 100, 255),  # Purple
        ]
        self.color = random.choice(base_colors)
        self.dark_color = tuple(max(0, c - 50) for c in self.color)
        self.light_color = tuple(min(255, c + 50) for c in self.color)

    def draw(self, screen):
        """Draw the planet"""
        # Basic planet circle
        pygame.draw.circle(screen, self.color, (self.x, self.y), self.size)
        
        # Draw outline
        pygame.draw.circle(screen, self.light_color, (self.x, self.y), self.size, 2)
        
        # Draw name
        if not self.showing_fact:
            font = pygame.font.Font(None, 24)
            text = font.render(self.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.x, self.y + self.size + 10))
            screen.blit(text, text_rect)
        
        # Draw fact when clicked
        if self.clicked and self.showing_fact:
            self.draw_fact(screen)

    def draw_fact(self, screen):
        """Draw fact bubble"""
        font = pygame.font.Font(None, 24)
        text = font.render(self.fact, True, (255, 255, 255))
        
        # Create bubble
        padding = 10
        bubble = pygame.Surface((text.get_width() + padding*2, text.get_height() + padding*2))
        bubble.fill((0, 0, 0))
        bubble.blit(text, (padding, padding))
        
        # Position above planet
        bubble_pos = (self.x - bubble.get_width()//2, self.y - self.size - bubble.get_height() - 10)
        screen.blit(bubble, bubble_pos)

    def handle_click(self):
        """Handle mouse click"""
        if not self.clicked:
            self.clicked = True
            self.showing_fact = True
            self.sound_manager.play_note(self.note)
        else:
            self.showing_fact = not self.showing_fact