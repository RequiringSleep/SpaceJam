# visualizer.py
import pygame
import numpy as np
import math
from collections import deque

class Visualizer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.center = (width // 2, height // 2)
        
        self.main_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.trail_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        self.orbit_radius = min(width, height) // 3.2
        self.center_orb_radius = 65
        self.orbital_orb_size = 4
        
        self.base_speed = 0.00125  # Increased by 25%
        self.max_deviation = self.orbit_radius * 0.4
        self.spring_constant = 0.03  # Reduced for smoother movement
        self.damping = 0.99  # Increased for more gradual return
        self.attraction_strength = 0.2  # Center attraction strength
        
        # Add velocity components for smoother movement
        self.orbs = [
            {'color': color, 'angle': angle, 'deviation': 0, 
             'radial_velocity': 0, 'angular_velocity': self.base_speed,
             'x_velocity': 0, 'y_velocity': 0}
            for color, angle in [
                ((50, 150, 255), 0),
                ((255, 50, 120), 2*math.pi/5),
                ((255, 170, 50), 4*math.pi/5),
                ((170, 255, 50), 6*math.pi/5),
                ((200, 100, 255), 8*math.pi/5)
            ]
        ]
        
        self.trails = [deque(maxlen=50) for _ in range(len(self.orbs))]
        
        self.font_time = pygame.font.Font(None, 52)
        self.font_category = pygame.font.Font(None, 24)
        self.font_voice = pygame.font.Font(None, 18)
        
        self.time = 0
        self.selection_pulse = 0
        self.glow_intensity = 0
        self.fade_alpha = 255

    def update(self, audio_data, category):
        if not audio_data:
            return
            
        intensity = audio_data.get('intensity', 0)
        has_peak = audio_data.get('has_recent_peak', False)
        
        self.glow_intensity = min(1.0, self.glow_intensity + (intensity * 0.5))
        self.glow_intensity *= 0.95
        
        for i, orb in enumerate(self.orbs):
            # Base orbital motion
            orb['angle'] += orb['angular_velocity']
            
            # Calculate current position
            radius = self.orbit_radius + orb['deviation']
            current_x = self.center[0] + math.cos(orb['angle']) * radius
            current_y = self.center[1] + math.sin(orb['angle']) * radius
            
            # Center attraction when sound is detected
            if intensity > 0:
                dx = self.center[0] - current_x
                dy = self.center[1] - current_y
                dist = math.sqrt(dx*dx + dy*dy)
                attraction = self.attraction_strength * intensity
                
                orb['x_velocity'] += (dx/dist) * attraction
                orb['y_velocity'] += (dy/dist) * attraction
            
            # Update position with velocity
            current_x += orb['x_velocity']
            current_y += orb['y_velocity']
            
            # Calculate new angle and deviation from orbital path
            new_angle = math.atan2(current_y - self.center[1], current_x - self.center[0])
            new_radius = math.sqrt((current_x - self.center[0])**2 + (current_y - self.center[1])**2)
            orb['deviation'] = new_radius - self.orbit_radius
            orb['angle'] = new_angle
            
            # Apply damping
            orb['x_velocity'] *= self.damping
            orb['y_velocity'] *= self.damping
            
            # Return to orbital path
            if abs(orb['deviation']) > 0:
                return_force = -self.spring_constant * orb['deviation']
                orb['radial_velocity'] += return_force
                orb['deviation'] += orb['radial_velocity']
                orb['radial_velocity'] *= self.damping
            
            # Store trail
            self.trails[i].append((current_x, current_y, intensity))
        
        self.time += 0.016
        self.selection_pulse = (self.selection_pulse + 0.05) % (2 * math.pi)

    def draw_trails(self, surface):
        # Don't fade existing trails for permanent streaks
        for i, trail in enumerate(self.trails):
            if len(trail) < 2:
                continue
            
            for j in range(1, len(trail)):
                start_pos = trail[j-1][:2]
                end_pos = trail[j][:2]
                intensity = trail[j][2]
                
                # Dynamic trail width and opacity
                width = max(2, int(4 * intensity))
                alpha = int(200 * (0.5 + intensity * 0.5))  # Maintain visibility
                color = (*self.orbs[i]['color'], alpha)
                
                pygame.draw.line(self.trail_surface, color, start_pos, end_pos, width)
        
        # Blend trails onto main surface
        surface.blit(self.trail_surface, (0, 0))

    def draw_orb(self, surface, pos, color, size=4, intensity=1.0):
        # Enhanced glow effect
        max_radius = int(12 * (1 + intensity * 0.5))
        for r in range(max_radius, 0, -1):
            alpha = int(100 * (r/max_radius) * intensity)
            pygame.draw.circle(surface, (*color, alpha), pos, r)
        
        # Bright center with intensity scaling
        core_size = int(size * (1 + intensity * 0.3))
        pygame.draw.circle(surface, (*color, 255), pos, core_size)
        pygame.draw.circle(surface, (255, 255, 255, 255), pos, max(1, core_size-1))

    def draw_timer(self, surface, category, elapsed_time):
        # Enhanced central orb glow
        for r in range(self.center_orb_radius + 15, self.center_orb_radius - 5, -1):
            alpha = int(10 * (1 - (r - self.center_orb_radius + 5) / 20))
            alpha = int(alpha * (1 + self.glow_intensity * 0.5))
            pygame.draw.circle(surface, (40, 42, 50, alpha), self.center, r)
        
        # Main orb body
        pygame.draw.circle(surface, (25, 27, 35, 255), self.center, self.center_orb_radius)
        
        # Timer display
        minutes = int(elapsed_time.total_seconds() // 60)
        seconds = int(elapsed_time.total_seconds() % 60)
        time_text = f"{minutes:02d}:{seconds:02d}"
        
        # Render text with enhanced styling
        time_surface = self.font_time.render(time_text, True, (255, 255, 255))
        category_surface = self.font_category.render(category.upper(), True, (200, 200, 200))
        voice_surface = self.font_voice.render(f"Voice: {self.get_voice_name(category)}", True, (150, 150, 150))
        
        # Position text elements
        time_rect = time_surface.get_rect(center=(self.center[0], self.center[1] - 12))
        category_rect = category_surface.get_rect(center=(self.center[0], self.center[1] + 12))
        voice_rect = voice_surface.get_rect(center=(self.center[0], self.center[1] + 32))
        
        # Draw text
        surface.blit(time_surface, time_rect)
        surface.blit(category_surface, category_rect)
        surface.blit(voice_surface, voice_rect)

    def draw_selection(self, screen):
        screen.fill((0, 0, 0))
        spacing = self.height // 4
        pulse_scale = 1 + math.sin(self.selection_pulse) * 0.1
        
        categories = ['sleep', 'study', 'vent']
        for i, category in enumerate(categories):
            pos = (self.width // 2, spacing * (i + 1))
            
            # Enhanced selection orb glow
            glow_radius = int(30 * pulse_scale)
            for r in range(glow_radius, 0, -1):
                alpha = int(50 * (r/glow_radius))
                pygame.draw.circle(screen, (*self.orbs[i]['color'], alpha), pos, r)
            
            # Main orb
            self.draw_orb(screen, pos, self.orbs[i]['color'], size=6)
            
            # Category text with glow
            text = self.font_category.render(category.upper(), True, (255, 255, 255))
            glow_text = self.font_category.render(category.upper(), True, self.orbs[i]['color'])
            
            text_rect = text.get_rect(center=(pos[0], pos[1] + 40))
            screen.blit(glow_text, text_rect.inflate(4, 4))
            screen.blit(text, text_rect)

    def draw_conclusion(self, screen, category, progress):
        # Fade out effect
        self.fade_alpha = int(255 * (1 - progress))
        
        # Draw existing visualization with fade
        self.trail_surface.set_alpha(self.fade_alpha)
        screen.blit(self.trail_surface, (0, 0))
        
        # Draw final orb positions with fade
        for i, orb in enumerate(self.orbs):
            if len(self.trails[i]) > 0:
                pos = self.trails[i][-1][:2]
                self.draw_orb(screen, pos, self.orbs[i]['color'], 
                            intensity=1-progress)

    def draw(self, screen, category, elapsed_time):
        screen.fill((0, 0, 0))
        
        # Draw visualization elements
        self.draw_trails(screen)
        
        # Draw orbital orbs
        for i, orb in enumerate(self.orbs):
            radius = self.orbit_radius + orb['deviation']
            pos = (
                int(self.center[0] + math.cos(orb['angle']) * radius),
                int(self.center[1] + math.sin(orb['angle']) * radius)
            )
            self.draw_orb(screen, pos, self.orbs[i]['color'], 
                         intensity=1.0 + self.glow_intensity)
        
        # Draw central timer orb
        self.draw_timer(screen, category, elapsed_time)

    def get_voice_name(self, category):
        voice_names = {
            'sleep': 'Shimmer',
            'study': 'Onyx',
            'vent': 'Nova'
        }
        return voice_names.get(category, 'Nova')

    def reset(self):
        # Don't clear trails on reset to maintain the pattern
        for orb in self.orbs:
            orb['deviation'] = 0
            orb['radial_velocity'] = 0
            orb['x_velocity'] = 0
            orb['y_velocity'] = 0
        self.glow_intensity = 0
        self.fade_alpha = 255