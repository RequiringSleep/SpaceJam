import pygame
import random
import math

class Planet:
    def __init__(self, x, y, size, note, name="Planet"):
        self.x = x
        self.y = y
        self.size = size
        self.note = note
        self.name = name
        self.clicked = False
        self.showing_fact = False
        
        # Create vibrant base colors for each planet
        self.generate_planet_theme()
        
        # Initialize surface for glow effect
        self.glow_surface = None
        self.create_glow_effect()
        
        # Rectangle for collision detection
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)
        
        # Planet features
        self.has_rings = random.random() < 0.4
        self.has_moons = random.random() < 0.3
        self.moon_count = random.randint(1, 3) if self.has_moons else 0
        self.ring_color = self.generate_complementary_color(self.base_color)
        
        # Animation properties
        self.rotation = 0
        self.moon_rotation = 0
        self.pulse_scale = 1.0
        self.pulse_growing = True
        
        # Educational facts about space for kids
        self.facts = {
            '0': "Mercury: The smallest planet, closest to the Sun!",
            '1': "Venus: The hottest planet due to its thick atmosphere!",
            '2': "Earth: Our home planet with liquid water on its surface!",
            '3': "Mars: The Red Planet with the largest volcano in our system!",
            '4': "Jupiter: The largest planet with a giant red storm!",
            '5': "Saturn: Known for its beautiful ring system!",
            '6': "Uranus: The planet that rotates on its side!",
            '7': "Neptune: The windiest planet with supersonic storms!",
            '8': "Pluto: A dwarf planet with a heart-shaped region!"
        }
        self.fact = self.facts[str(random.randint(0, 8))]
        self.fact_surface = None

    def generate_planet_theme(self):
        """Generate vibrant, playful color schemes for the planet"""
        # Base colors - bright and cheerful
        base_colors = [
            (255, 150, 50),   # Bright orange
            (50, 180, 255),   # Sky blue
            (255, 100, 255),  # Pink
            (130, 255, 100),  # Lime green
            (255, 200, 50),   # Golden yellow
            (180, 100, 255),  # Purple
            (255, 100, 100),  # Coral red
            (100, 255, 200),  # Turquoise
        ]
        self.base_color = random.choice(base_colors)
        
        # Generate darker and lighter shades for depth
        self.dark_color = tuple(max(0, c - 60) for c in self.base_color)
        self.light_color = tuple(min(255, c + 60) for c in self.base_color)
        
        # Surface pattern type
        self.pattern_type = random.choice(['stripes', 'spots', 'swirl'])

    def generate_complementary_color(self, color):
        """Generate a complementary color for rings and details"""
        return (255 - color[0], 255 - color[1], 255 - color[2])

    def create_glow_effect(self):
        """Create a soft glow effect around the planet"""
        glow_size = self.size * 3
        self.glow_surface = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
        center = glow_size // 2
        
        for radius in range(self.size, glow_size // 2, 2):
            alpha = max(0, 100 - (radius - self.size))
            pygame.draw.circle(self.glow_surface, (*self.base_color, alpha), 
                             (center, center), radius)

    def draw_planet_features(self, surface, center_x, center_y):
        """Draw the detailed features of the planet"""
        # Draw base planet
        pygame.draw.circle(surface, self.base_color, (center_x, center_y), self.size)
        
        # Add pattern based on type
        if self.pattern_type == 'stripes':
            for i in range(-self.size, self.size, 8):
                pygame.draw.line(surface, self.dark_color,
                               (center_x - self.size, center_y + i),
                               (center_x + self.size, center_y + i + self.rotation % 8), 2)
        elif self.pattern_type == 'spots':
            for _ in range(8):
                spot_x = center_x + random.randint(-self.size//2, self.size//2)
                spot_y = center_y + random.randint(-self.size//2, self.size//2)
                spot_size = random.randint(4, 8)
                pygame.draw.circle(surface, self.light_color, (spot_x, spot_y), spot_size)
        elif self.pattern_type == 'swirl':
            points = []
            for i in range(0, 360, 20):
                angle = i + self.rotation
                radius = self.size * (0.5 + 0.3 * (i/360))
                x = center_x + radius * math.cos(math.radians(angle))
                y = center_y + radius * math.sin(math.radians(angle))
                points.append((x, y))
            if len(points) > 2:
                pygame.draw.lines(surface, self.dark_color, False, points, 2)

        # Draw rings if present
        if self.has_rings:
            ring_rect = pygame.Rect(center_x - self.size*1.5, center_y - self.size//4,
                                  self.size*3, self.size//2)
            pygame.draw.ellipse(surface, self.ring_color, ring_rect, 2)
            pygame.draw.ellipse(surface, self.light_color, ring_rect.inflate(-4, -4), 1)

        # Draw moons if present
        if self.has_moons:
            for i in range(self.moon_count):
                angle = math.radians(self.moon_rotation + (360/self.moon_count * i))
                moon_dist = self.size * 1.8
                moon_x = center_x + moon_dist * math.cos(angle)
                moon_y = center_y + moon_dist * math.sin(angle)
                moon_size = self.size // 4
                pygame.draw.circle(surface, self.light_color, (int(moon_x), int(moon_y)), moon_size)

    def draw(self, screen):
        """Draw the planet with all its effects and animations"""
        # Update animations
        self.rotation = (self.rotation + 0.5) % 360
        self.moon_rotation = (self.moon_rotation + 0.2) % 360
        
        if self.pulse_growing:
            self.pulse_scale += 0.01
            if self.pulse_scale >= 1.1:
                self.pulse_growing = False
        else:
            self.pulse_scale -= 0.01
            if self.pulse_scale <= 0.9:
                self.pulse_growing = True

        # Draw glow effect for clicked planets
        if self.clicked:
            glow_rect = self.glow_surface.get_rect(center=(self.x, self.y))
            screen.blit(self.glow_surface, glow_rect)

        # Create a surface for the planet
        planet_surface = pygame.Surface((self.size * 3, self.size * 3), pygame.SRCALPHA)
        center = planet_surface.get_rect().center
        
        # Draw all planet features
        self.draw_planet_features(planet_surface, center[0], center[1])
        
        # Apply pulse effect
        if self.clicked:
            scaled_size = (int(planet_surface.get_width() * self.pulse_scale),
                         int(planet_surface.get_height() * self.pulse_scale))
            planet_surface = pygame.transform.smoothscale(planet_surface, scaled_size)

        # Draw the planet surface
        planet_rect = planet_surface.get_rect(center=(self.x, self.y))
        screen.blit(planet_surface, planet_rect)

        # Draw name
        if not self.showing_fact:
            font = pygame.font.Font(None, 24)
            text = font.render(self.name, True, (255, 255, 255))
            text_rect = text.get_rect(center=(self.x, self.y + self.size + 20))
            screen.blit(text, text_rect)

        # Draw fact when clicked
        if self.clicked and self.showing_fact:
            self.draw_fact(screen)

    def draw_fact(self, screen):
        """Draw the educational fact in a playful speech bubble"""
        if not self.fact_surface:
            # Create the fact text surface
            padding = 20
            font = pygame.font.Font(None, 24)
            text = font.render(self.fact, True, (255, 255, 255))
            bubble_width = text.get_width() + padding * 2
            bubble_height = text.get_height() + padding * 2
            
            self.fact_surface = pygame.Surface((bubble_width, bubble_height), pygame.SRCALPHA)
            
            # Draw bubble background
            pygame.draw.rect(self.fact_surface, (0, 0, 0, 180), 
                           self.fact_surface.get_rect(), border_radius=10)
            
            # Draw text
            self.fact_surface.blit(text, (padding, padding))

        # Position fact bubble above planet
        fact_rect = self.fact_surface.get_rect(midbottom=(self.x, self.y - self.size - 10))
        screen.blit(self.fact_surface, fact_rect)

        # Draw connecting line
        pygame.draw.line(screen, (255, 255, 255),
                        (self.x, self.y - self.size),
                        (self.x, fact_rect.bottom),
                        2)