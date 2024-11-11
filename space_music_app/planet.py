# planet.py
import pygame
import math
import random

class Planet:
    def __init__(self, x, y, size, base_color):
        self.x = x
        self.y = y
        self.size = size
        self.base_color = base_color
        self.is_playing = False
        self.pulse_phase = 0
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.5, 0.5)

    def draw_surface_details(self, screen, center_x, center_y, current_size):
        """Draw surface details"""
        # Calculate darker color for features
        darker_color = (
            int(self.base_color[0] * 0.8),
            int(self.base_color[1] * 0.8),
            int(self.base_color[2] * 0.8)
        )
        
        # Draw some surface features using the darker color
        for i in range(3):
            angle = self.rotation + (i * 2 * math.pi / 3)
            feature_x = center_x + math.cos(angle) * current_size * 0.5
            feature_y = center_y + math.sin(angle) * current_size * 0.5
            feature_size = current_size * 0.2
            pygame.draw.circle(screen, darker_color,
                             (int(feature_x), int(feature_y)), 
                             int(feature_size))

    def draw(self, screen):
        """Draw the planet"""
        # Update rotation
        self.rotation += self.rotation_speed * 0.02
        
        # Calculate current size with pulse if playing
        if self.is_playing:
            self.pulse_phase = (self.pulse_phase + 0.1) % (2 * math.pi)
            current_size = self.size + math.sin(self.pulse_phase) * 5
            
            # Draw outer glow
            glow_color = (min(self.base_color[0] + 50, 255),
                         min(self.base_color[1] + 50, 255),
                         min(self.base_color[2] + 50, 255))
            pygame.draw.circle(screen, glow_color, 
                             (int(self.x), int(self.y)), 
                             int(current_size + 5))
        else:
            current_size = self.size
        
        # Draw main planet body
        center_x, center_y = int(self.x), int(self.y)
        pygame.draw.circle(screen, self.base_color, 
                         (center_x, center_y), 
                         int(current_size))
        
        # Draw surface details
        self.draw_surface_details(screen, center_x, center_y, current_size)
        
        # Draw highlight
        highlight_pos = (int(self.x - current_size * 0.3),
                        int(self.y - current_size * 0.3))
        highlight_size = int(current_size * 0.2)
        pygame.draw.circle(screen, (255, 255, 255),
                         highlight_pos, highlight_size)

    def handle_click(self, pos):
        """Check if click position intersects with planet"""
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        distance = (dx * dx + dy * dy) ** 0.5
        return distance <= self.size