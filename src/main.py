# main.py
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
        
        self.width = 390
        self.height = 844
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
            center = (self.width // 2, self.height // 2)
            distance = ((pos[0] - center[0])**2 + (pos[1] - center[1])**2)**0.5
            
            if distance < 65:
                self.sound_manager.play_ui_sound('stop')
                self.stop_session()

    def start_session(self):
        self.state = 'running'
        self.start_time = datetime.now()
        self.audio_processor.start()
        self.visualizer.reset()
        self.voice_effects.reset_session()
        self.sound_manager.play_ui_sound('start')

    def stop_session(self):
        self.audio_processor.stop()
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

    def draw(self):
        if self.state == 'selection':
            self.visualizer.draw_selection(self.screen)
        elif self.state == 'running':
            self.visualizer.draw(self.screen, self.category, self.elapsed_time)
        elif self.state == 'conclusion':
            progress = (time.time() - self.conclusion_start) / self.conclusion_duration
            self.visualizer.draw_conclusion(self.screen, self.category, progress)
        
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
        pygame.quit()

if __name__ == "__main__":
    app = MindfulApp()
    app.run()