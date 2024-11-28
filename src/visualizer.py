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
        self.blur_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        self.orbit_radius = min(width, height) // 3.2
        self.center_orb_radius = 65
        self.orbital_orb_size = 4
        
        self.base_speed = 0.00125
        self.max_deviation = self.orbit_radius * 0.4
        self.spring_constant = 0.03
        self.damping = 0.99
        self.attraction_strength = 0.2
        
        self.orbs = [
            {'color': color, 'angle': angle, 'deviation': 0, 
             'radial_velocity': 0, 'angular_velocity': self.base_speed,
             'x_velocity': 0, 'y_velocity': 0}
            for color, angle in [
                ((80, 180, 255), 0),
                ((255, 80, 150), 2*math.pi/5),
                ((255, 200, 80), 4*math.pi/5),
                ((200, 255, 80), 6*math.pi/5),
                ((230, 130, 255), 8*math.pi/5)
            ]
        ]
        
        self.trails = [deque(maxlen=75) for _ in range(len(self.orbs))]
        
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
            orb['angle'] += orb['angular_velocity']
            
            radius = self.orbit_radius + orb['deviation']
            current_x = self.center[0] + math.cos(orb['angle']) * radius
            current_y = self.center[1] + math.sin(orb['angle']) * radius
            
            if intensity > 0:
                dx = self.center[0] - current_x
                dy = self.center[1] - current_y
                dist = math.sqrt(dx*dx + dy*dy)
                attraction = self.attraction_strength * intensity
                
                orb['x_velocity'] += (dx/dist) * attraction
                orb['y_velocity'] += (dy/dist) * attraction
            
            current_x += orb['x_velocity']
            current_y += orb['y_velocity']
            
            new_angle = math.atan2(current_y - self.center[1], current_x - self.center[0])
            new_radius = math.sqrt((current_x - self.center[0])**2 + (current_y - self.center[1])**2)
            orb['deviation'] = new_radius - self.orbit_radius
            orb['angle'] = new_angle
            
            orb['x_velocity'] *= self.damping
            orb['y_velocity'] *= self.damping
            
            if abs(orb['deviation']) > 0:
                return_force = -self.spring_constant * orb['deviation']
                orb['radial_velocity'] += return_force
                orb['deviation'] += orb['radial_velocity']
                orb['radial_velocity'] *= self.damping
            
            self.trails[i].append((current_x, current_y, intensity))
        
        self.time += 0.016
        self.selection_pulse = (self.selection_pulse + 0.05) % (2 * math.pi)

    def draw_trails(self, surface):
        self.trail_surface.fill((0, 0, 0, 0))  # Clear with transparency
        
        for i, trail in enumerate(self.trails):
            if len(trail) < 2:
                continue
            
            for j in range(1, len(trail)):
                start_pos = trail[j-1][:2]
                end_pos = trail[j][:2]
                intensity = trail[j][2]
                
                width = max(2, int(4 * intensity))
                alpha = int(128 * (0.5 + intensity * 0.5))  # Reduced alpha
                color = (*self.orbs[i]['color'], alpha)
                
                pygame.draw.line(self.trail_surface, color, start_pos, end_pos, width)
        
        surface.blit(self.trail_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def draw_orb(self, surface, pos, color, size=4, intensity=1.0):
        self.glow_surface.fill((0, 0, 0, 0))  # Clear with transparency
        
        max_radius = int(12 * (1 + intensity * 0.5))
        for r in range(max_radius, 0, -1):
            alpha = int(50 * (r/max_radius) * intensity)  # Reduced alpha
            pygame.draw.circle(self.glow_surface, (*color, alpha), pos, r)
        
        core_size = int(size * (1 + intensity * 0.3))
        pygame.draw.circle(self.glow_surface, (*color, 200), pos, core_size)  # Reduced alpha
        pygame.draw.circle(self.glow_surface, (255, 255, 255, 200), pos, max(1, core_size-1))
        
        surface.blit(self.glow_surface, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)

    def draw_timer(self, surface, category, elapsed_time):
        self.glow_surface.fill((0, 0, 0, 0))  # Clear with transparency
        
        # Draw dark background for timer
        pygame.draw.circle(surface, (20, 22, 25, 255), self.center, self.center_orb_radius + 5)
        
        # Timer text
        minutes = int(elapsed_time.total_seconds() // 60)
        seconds = int(elapsed_time.total_seconds() % 60)
        time_text = f"{minutes:02d}:{seconds:02d}"
        
        time_surface = self.font_time.render(time_text, True, (255, 255, 255))
        category_surface = self.font_category.render(category.upper(), True, (200, 200, 200))
        voice_surface = self.font_voice.render(f"Voice: {self.get_voice_name(category)}", True, (150, 150, 150))
        
        time_rect = time_surface.get_rect(center=(self.center[0], self.center[1] - 12))
        category_rect = category_surface.get_rect(center=(self.center[0], self.center[1] + 12))
        voice_rect = voice_surface.get_rect(center=(self.center[0], self.center[1] + 32))
        
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
            
            glow_radius = int(30 * pulse_scale)
            for r in range(glow_radius, 0, -1):
                alpha = int(25 * (r/glow_radius))  # Reduced alpha
                pygame.draw.circle(screen, (*self.orbs[i]['color'], alpha), pos, r)
            
            self.draw_orb(screen, pos, self.orbs[i]['color'], size=6)
            
            text = self.font_category.render(category.upper(), True, (255, 255, 255))
            glow_text = self.font_category.render(category.upper(), True, self.orbs[i]['color'])
            
            text_rect = text.get_rect(center=(pos[0], pos[1] + 40))
            screen.blit(glow_text, text_rect.inflate(4, 4))
            screen.blit(text, text_rect)

    def draw_conclusion(self, screen, category, progress):
        screen.fill((0, 0, 0))
        self.fade_alpha = int(255 * (1 - progress))
        
        self.trail_surface.set_alpha(self.fade_alpha)
        screen.blit(self.trail_surface, (0, 0))
        
        for i, orb in enumerate(self.orbs):
            if len(self.trails[i]) > 0:
                pos = self.trails[i][-1][:2]
                self.draw_orb(screen, pos, self.orbs[i]['color'], 
                            intensity=1-progress)

    def draw(self, screen, category, elapsed_time):
        screen.fill((0, 0, 0))
        
        self.draw_trails(screen)
        
        for i, orb in enumerate(self.orbs):
            radius = self.orbit_radius + orb['deviation']
            pos = (
                int(self.center[0] + math.cos(orb['angle']) * radius),
                int(self.center[1] + math.sin(orb['angle']) * radius)
            )
            self.draw_orb(screen, pos, self.orbs[i]['color'], 
                         intensity=1.0 + self.glow_intensity)
        
        self.draw_timer(screen, category, elapsed_time)

    def get_voice_name(self, category):
        voice_names = {
            'sleep': 'Shimmer',
            'study': 'Onyx', 
            'vent': 'Nova'
        }
        return voice_names.get(category, 'Nova')

    def reset(self):
        for orb in self.orbs:
            orb['deviation'] = 0
            orb['radial_velocity'] = 0
            orb['x_velocity'] = 0
            orb['y_velocity'] = 0
        self.glow_intensity = 0
        self.fade_alpha = 255
        
        # Clear all surfaces
        self.trail_surface.fill((0, 0, 0, 0))
        self.glow_surface.fill((0, 0, 0, 0))
        self.blur_surface.fill((0, 0, 0, 0))

    def cleanup(self):
        pass