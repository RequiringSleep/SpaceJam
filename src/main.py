import pygame
import sys
import time
from datetime import datetime, timedelta
from audio_processor import AudioProcessor
from visualizer import Visualizer
from voice_effects import VoiceEffectsManager
from sound_manager import SoundManager

class MindfulApp:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 900
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Mindful Voice")
        
        self.audio_processor = AudioProcessor()
        self.visualizer = Visualizer(self.width, self.height)
        self.voice_effects = VoiceEffectsManager()
        self.sound_manager = SoundManager()
        
        self.state = 'selection'
        self.category = None
        self.start_time = None
        self.elapsed_time = timedelta()
        self.patterns = []
        self.current_pattern_index = 0
        
        self.patterns_button = pygame.Rect(self.width - 60, 20, 40, 40)
        self.next_button = pygame.Rect(self.width - 60, self.height//2, 40, 40)
        self.prev_button = pygame.Rect(20, self.height//2, 40, 40)
        
        self.clock = pygame.time.Clock()
        self.conclusion_start = 0
        self.conclusion_duration = 5.0
        self.interpretation = None

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.MOUSEBUTTONDOWN:
                self.handle_click(pygame.mouse.get_pos())
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True

    def handle_click(self, pos):
        if self.state == 'patterns':
            if self.next_button.collidepoint(pos) and self.current_pattern_index < len(self.patterns) - 1:
                self.current_pattern_index += 1
            elif self.prev_button.collidepoint(pos) and self.current_pattern_index > 0:
                self.current_pattern_index -= 1
            elif self.visualizer.back_button.collidepoint(pos):
                self.state = 'selection'
            return

        if self.patterns_button.collidepoint(pos):
            self.state = 'patterns'
            return

        if self.state == 'selection':
            spacing = self.height // 4
            categories = ['sleep', 'study', 'vent']
            
            for i, cat in enumerate(categories):
                button_pos = (self.width // 2, spacing * (i + 1))
                distance = ((pos[0] - button_pos[0])**2 + (pos[1] - button_pos[1])**2)**0.5
                
                if distance < 40:
                    self.category = cat
                    self.sound_manager.play_ui_sound('select')
                    self.start_session()
                    break
        
        elif self.state == 'running':
            back_clicked = self.visualizer.handle_click(pos)
            if back_clicked:
                self.state = back_clicked
                self.audio_processor.stop()
                self.visualizer.reset()
                self.sound_manager.play_ui_sound('transition')
                return
                
            center = (self.width // 2, self.height // 2)
            distance = ((pos[0] - center[0])**2 + (pos[1] - center[1])**2)**0.5
            
            if distance < 85:
                self.sound_manager.play_ui_sound('stop')
                self.stop_session()

    def draw_patterns_page(self):
        self.screen.fill((215, 248, 255))
        self.visualizer.draw_back_button(self.screen)
        
        if not self.patterns:
            text = self.visualizer.font_category.render("No patterns yet", True, (100, 100, 100))
            text_rect = text.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(text, text_rect)
            return

        pattern = self.patterns[self.current_pattern_index]
        
        # Draw navigation buttons
        if self.current_pattern_index < len(self.patterns) - 1:
            pygame.draw.polygon(self.screen, (40, 42, 45), 
                [(self.width - 40, self.height//2), 
                 (self.width - 60, self.height//2 - 20),
                 (self.width - 60, self.height//2 + 20)])
        
        if self.current_pattern_index > 0:
            pygame.draw.polygon(self.screen, (40, 42, 45),
                [(40, self.height//2),
                 (20, self.height//2 - 20),
                 (20, self.height//2 + 20)])

        # Draw pattern info
        count_text = f"Pattern {self.current_pattern_index + 1}/{len(self.patterns)}"
        text = self.visualizer.font_category.render(count_text, True, (40, 42, 45))
        text_rect = text.get_rect(center=(self.width//2, 50))
        self.screen.blit(text, text_rect)

        # Draw stored pattern
        self.visualizer.draw_stored_pattern(self.screen, pattern)

    def draw_patterns_button(self, surface):
        pygame.draw.circle(surface, (40, 42, 45), (self.width - 40, 40), 20)
        pygame.draw.circle(surface, (200, 200, 200), (self.width - 40, 40), 15, 2)
        pygame.draw.circle(surface, (200, 200, 200), (self.width - 40, 40), 8, 2)

    def start_session(self):
        self.state = 'running'
        self.start_time = datetime.now()
        self.audio_processor.start()
        self.visualizer.reset()
        self.voice_effects.reset_session()
        self.sound_manager.play_ui_sound('start')

    def stop_session(self):
        self.audio_processor.stop()
        pattern_data = {
            'trails': [trail.copy() for trail in self.visualizer.trails],
            'category': self.category,
            'timestamp': datetime.now()
        }
        self.patterns.append(pattern_data)
        self.state = 'conclusion'
        self.conclusion_start = time.time()
        session_duration = (datetime.now() - self.start_time).total_seconds()
        self.voice_effects.pattern_data['duration'] = session_duration
        self.interpretation = self.voice_effects.generate_pattern_interpretation(self.category)
        print(f"\nSession Interpretation:\n{self.interpretation}")

    def update(self):
        if self.state == 'running':
            audio_data = self.audio_processor.get_analysis()
            self.elapsed_time = datetime.now() - self.start_time
            self.visualizer.update(audio_data, self.category)
            self.voice_effects.record_pattern_data(audio_data, self.elapsed_time.total_seconds())
        elif self.state == 'conclusion':
            if time.time() - self.conclusion_start > self.conclusion_duration:
                self.sound_manager.play_ui_sound('transition')
                self.state = 'selection'
                self.category = None
                self.visualizer.reset()

    def draw(self):
        if self.state == 'selection':
            self.visualizer.draw_selection(self.screen)
            self.draw_patterns_button(self.screen)
        elif self.state == 'running':
            self.visualizer.draw(self.screen, self.category, self.elapsed_time)
        elif self.state == 'conclusion':
            progress = (time.time() - self.conclusion_start) / self.conclusion_duration
            self.visualizer.draw_conclusion(self.screen, self.category, progress)
        elif self.state == 'patterns':
            self.draw_patterns_page()
        
        pygame.display.flip()

    def run(self):
        running = True
        try:
            while running:
                running = self.handle_events()
                self.update()
                self.draw()
                self.clock.tick(60)
        finally:
            self.cleanup()

    def cleanup(self):
        self.audio_processor.stop()
        self.sound_manager.cleanup()
        self.visualizer.cleanup()
        pygame.quit()

if __name__ == "__main__":
    app = MindfulApp()
    app.run()