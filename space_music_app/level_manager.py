import random
from planet import Planet

class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.max_level = 3  # For prototype
    
    def generate_level(self, notes, level_num):
        """Generate planets for a level"""
        planets = []
        num_planets = min(3 + level_num, 7)  # Increase planets with each level
        available_positions = self._generate_positions(num_planets)
        
        # Get available notes
        note_list = list(notes.keys())
        
        for i in range(num_planets):
            pos = available_positions[i]
            planet_data = {
                'size': random.randint(30, 50),
                'note': note_list[i % len(note_list)],
                'name': f'Planet {i+1}'
            }
            planet = Planet(pos[0], pos[1], planet_data['size'], 
                          planet_data['note'], planet_data['name'])
            planets.append(planet)
        
        return planets
    
    def _generate_positions(self, num_planets):
        """Generate non-overlapping positions for planets"""
        positions = []
        margin = 100  # Minimum distance from edges
        screen_width = 800 - 2*margin
        screen_height = 600 - 2*margin
        
        while len(positions) < num_planets:
            x = random.randint(margin, screen_width)
            y = random.randint(margin, screen_height)
            
            # Check if position is far enough from other planets
            valid_position = True
            for pos in positions:
                distance = ((pos[0] - x)**2 + (pos[1] - y)**2)**0.5
                if distance < 100:  # Minimum distance between planets
                    valid_position = False
                    break
            
            if valid_position:
                positions.append((x, y))
        
        return positions
    
    def is_level_complete(self, planets):
        """Check if all planets in the level have been clicked"""
        return all(planet.clicked for planet in planets)
    
    def advance_level(self):
        """Progress to the next level"""
        self.current_level += 1
        if self.current_level > self.max_level:
            self.current_level = 1