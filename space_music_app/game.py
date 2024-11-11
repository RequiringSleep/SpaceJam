# game.py
import pygame
import random
from planet import Planet

class Game:
    def __init__(self, screen, sound_manager, result):
        self.screen = screen
        self.sound_manager = sound_manager
        self.level = result
        self.planets = []
        
        # Create background stars
        self.stars = [(random.randint(0, 800), random.randint(0, 600), 
                      random.random()) for _ in range(200)]
        
        # Level settings
        self.required_active_planets = 3
        self.min_play_time = 10000  # 10 seconds
        self.start_time = None
        
        self.generate_planets()

    def draw_background(self):
        """Draw space background with stars"""
        self.screen.fill((0, 0, 20))  # Dark blue background
        
        # Draw stars with twinkling effect
        for x, y, brightness in self.stars:
            # Add subtle twinkling
            flicker = random.uniform(0.8, 1.2)
            color = int(255 * brightness * flicker)
            color = max(0, min(255, color))  # Clamp between 0 and 255
            
            pygame.draw.circle(self.screen, (color, color, color), 
                             (int(x), int(y)), 1)
            
            # Add occasional larger stars
            if brightness > 0.8:  # Brighter stars get a glow
                glow_radius = 2
                glow_color = (color // 4, color // 4, color // 4)
                pygame.draw.circle(self.screen, glow_color, 
                                 (int(x), int(y)), glow_radius)

    def generate_positions(self, num_planets):
        """Generate non-overlapping positions for planets"""
        positions = []
        margin = 100
        max_attempts = 100
        min_distance = 100  # Minimum distance between planets
        
        while len(positions) < num_planets and max_attempts > 0:
            x = random.randint(margin, 800 - margin)
            y = random.randint(margin, 600 - margin)
            
            # Check if position is far enough from other planets
            valid_position = True
            for pos in positions:
                distance = ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) ** 0.5
                if distance < min_distance:
                    valid_position = False
                    break
            
            if valid_position:
                positions.append((x, y))
            else:
                max_attempts -= 1
        
        return positions

    def generate_planets(self):
        """Generate planets for the current level"""
        num_planets = min(3 + self.level, 8)  # More planets in higher levels
        positions = self.generate_positions(num_planets)
        
        for pos in positions:
            # Randomize planet properties
            size = random.randint(30, 80)
            color = (random.randint(100, 255), 
                    random.randint(100, 255), 
                    random.randint(100, 255))
                    
            planet = Planet(pos[0], pos[1], size, color)
            self.planets.append(planet)

    def draw_interface(self):
        """Draw game interface elements"""
        font = pygame.font.Font(None, 36)
        
        # Draw level number
        level_text = font.render(f"Level {self.level}", True, (255, 255, 255))
        self.screen.blit(level_text, (20, 20))
        
        # Draw active planets counter
        active_count = sum(1 for planet in self.planets if planet.is_playing)
        counter_text = font.render(
            f"Active Planets: {active_count}/{self.required_active_planets}", 
            True, (255, 255, 255))
        self.screen.blit(counter_text, (20, 60))
        
        # Draw instructions if level just started
        if self.start_time is None:
            instruction_font = pygame.font.Font(None, 30)
            instruction_text = instruction_font.render(
                "Click planets to create music!", 
                True, (200, 200, 255))
            instruction_rect = instruction_text.get_rect(center=(400, 550))
            self.screen.blit(instruction_text, instruction_rect)

    def check_completion(self):
        """Check if level completion criteria are met"""
        if self.start_time is None:
            return False
            
        active_count = sum(1 for planet in self.planets if planet.is_playing)
        time_elapsed = pygame.time.get_ticks() - self.start_time
        
        return (active_count >= self.required_active_planets and 
                time_elapsed >= self.min_play_time)

    def cleanup_level(self):
        """Clean up resources when level is completed"""
        self.sound_manager.stop_all_sounds()
        for planet in self.planets:
            planet.is_playing = False

    def run(self):
        """Main game loop"""
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.cleanup_level()
                    return "quit"
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.cleanup_level()
                        return "menu"
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for planet in self.planets:
                        if planet.handle_click(event.pos):
                            self.sound_manager.play_planet_sound(planet)
                            if self.start_time is None:
                                self.start_time = pygame.time.get_ticks()
            
            # Update
            self.sound_manager.update()
            
            # Draw
            self.draw_background()
            for planet in self.planets:
                planet.draw(self.screen)
            self.draw_interface()
            
            # Check level completion
            if self.check_completion():
                self.cleanup_level()
                self.sound_manager.play_completion_melody()
                pygame.time.delay(1000)  # Wait for completion melody
                return ("level_complete", self.level)
            
            pygame.display.flip()