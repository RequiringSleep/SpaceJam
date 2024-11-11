import pygame
import numpy as np

class SoundManager:
    def __init__(self):
        """Initialize basic sound system"""
        pygame.mixer.init()
        self.notes = [261.63, 293.66, 329.63, 349.23, 392.00, 440.00, 493.88, 523.25]  # C4 to C5
        
    def play_note(self, note_index):
        """Play a musical note"""
        try:
            frequency = self.notes[note_index % len(self.notes)]
            duration = 1.0  # seconds
            sample_rate = 44100
            samples = int(duration * sample_rate)
            
            t = np.linspace(0, duration, samples)
            wave = np.sin(2 * np.pi * frequency * t)
            wave = np.int16(wave * 32767)
            
            # Convert to stereo
            stereo = np.column_stack((wave, wave))
            
            # Create sound buffer
            sound_buffer = pygame.sndarray.make_sound(stereo)
            sound_buffer.set_volume(0.5)
            sound_buffer.play()
            
        except Exception as e:
            print(f"Error playing sound: {e}")
    
    def play_startup_sound(self):
        """Play a startup sound"""
        self.play_note(0)
    
    def play_completion_melody(self):
        """Play a completion melody"""
        notes = [0, 2, 4, 7]  # C, E, G, C
        for i, note in enumerate(notes):
            pygame.time.delay(200 * i)  # Add delay between notes
            self.play_note(note)