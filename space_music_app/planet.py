# planet.py
import pygame
import math

class Planet:
    def __init__(self, x, y, size, base_color):
        self.x = x
        self.y = y
        self.size = size
        self.base_color = base_color
        self.is_playing = False
        self.pulse_phase = 0

    def draw(self, screen):
        # Calculate pulse effect
        if self.is_playing:
            self.pulse_phase = (self.pulse_phase + 0.1) % (2 * math.pi)
            pulse_size = self.size + math.sin(self.pulse_phase) * 5
            
            # Draw outer glow
            glow_color = (min(self.base_color[0] + 50, 255),
                         min(self.base_color[1] + 50, 255),
                         min(self.base_color[2] + 50, 255))
            pygame.draw.circle(screen, glow_color, 
                             (int(self.x), int(self.y)), 
                             int(pulse_size + 5))
        else:
            pulse_size = self.size
            
        # Draw main planet body
        pygame.draw.circle(screen, self.base_color, 
                         (int(self.x), int(self.y)), 
                         int(pulse_size))
                         
        # Draw highlight
        highlight_pos = (int(self.x - pulse_size * 0.3),
                        int(self.y - pulse_size * 0.3))
        highlight_size = int(pulse_size * 0.2)
        pygame.draw.circle(screen, (255, 255, 255),
                         highlight_pos, highlight_size)

    def handle_click(self, pos):
        """Check if click position intersects with planet"""
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        distance = (dx * dx + dy * dy) ** 0.5
        return distance <= self.size