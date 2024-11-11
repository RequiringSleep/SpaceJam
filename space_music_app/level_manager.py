import random
from planet import Planet

class LevelManager:
    def __init__(self):
        self.current_level = 1
        self.max_level = 9  # Total number of levels
        self.level_data = {
            1: {"num_planets": 3, "min_size": 30, "max_size": 50},
            2: {"num_planets": 4, "min_size": 30, "max_size": 55},
            3: {"num_planets": 4, "min_size": 35, "max_size": 60},
            4: {"num_planets": 5, "min_size": 35, "max_size": 60},
            5: {"num_planets": 5, "min_size": 40, "max_size": 65},
            6: {"num_planets": 6, "min_size": 40, "max_size": 65},
            7: {"num_planets": 6, "min_size": 45, "max_size": 70},
            8: {"num_planets": 7, "min_size": 45, "max_size": 70},
            9: {"num_planets": 7, "min_size": 50, "max_size": 75}
        }

    def generate_level(self, sound_manager, level_num=None):
        """Generate a list of planets for the current level"""
        if level_num is not None:
            self.current_level = level_num

        level_config = self.level_data.get(self.current_level, self.level_data[1])
        num_planets = level_config["num_planets"]
        min_size = level_config["min_size"]
        max_size = level_config["max_size"]

        # Generate non-overlapping positions for planets
        positions = self._generate_positions(num_planets)
        planets = []

        # Planet names for the current level
        planet_names = [f"Planet {i+1}" for i in range(num_planets)]

        for i in range(num_planets):
            size = random.randint(min_size, max_size)
            planet = Planet(
                positions[i][0],
                positions[i][1],
                size,
                sound_manager,
                planet_names[i]
            )
            planets.append(planet)

        return planets

    def _generate_positions(self, num_planets):
        """Generate non-overlapping positions for planets"""
        positions = []
        margin = 100  # Minimum distance from edges
        screen_width = 800 - 2 * margin
        screen_height = 600 - 2 * margin

        while len(positions) < num_planets:
            x = random.randint(margin, screen_width)
            y = random.randint(margin, screen_height)

            # Check if position is far enough from other planets
            valid_position = True
            for pos in positions:
                distance = ((pos[0] - x) ** 2 + (pos[1] - y) ** 2) ** 0.5
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
        """Move to the next level if not at max level"""
        if self.current_level < self.max_level:
            self.current_level += 1
        return self.current_level