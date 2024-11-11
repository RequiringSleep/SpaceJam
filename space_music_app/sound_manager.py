import pygame
import numpy as np

class SoundManager:
    def __init__(self):
        """Initialize the cosmic sound system"""
        pygame.mixer.init(44100, -16, 2, 1024)
        self.sample_rate = 44100
        
        # Add the notes attribute that was missing
        self.notes = [
            'C4', 'D4', 'E4', 'F4', 'G4', 'A4', 'B4',
            'C5', 'D5', 'E5', 'F5', 'G5', 'A5', 'B5'
        ]
        
        # Base frequencies for different planet types
        self.frequencies = {
            'small': 440.0,    # A4 - Mercury/Mars like
            'medium': 349.23,  # F4 - Earth/Venus like
            'large': 261.63,   # C4 - Gas giants like
            'ringed': 392.00,  # G4 - Saturn like
            'icy': 329.63      # E4 - Ice giants like
        }
        
        # Frequency mapping for notes
        self.note_frequencies = {
            'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23,
            'G4': 392.00, 'A4': 440.00, 'B4': 493.88,
            'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46,
            'G5': 783.99, 'A5': 880.00, 'B5': 987.77
        }
        
    def generate_cosmic_tone(self, frequency, duration=1.0):
        """Generate a more cosmic sounding tone"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        
        # Create main tone
        base_tone = np.sin(2 * np.pi * frequency * t)
        
        # Add some shimmer (frequency modulation)
        shimmer = np.sin(2 * np.pi * frequency * 1.5 * t + 
                        3 * np.sin(2 * np.pi * 5 * t))
        
        # Combine waves with shimmer effect
        wave = 0.7 * base_tone + 0.3 * shimmer
        
        # Add envelope for smooth fade in/out
        envelope = np.ones_like(t)
        attack = int(0.1 * self.sample_rate)
        release = int(0.2 * self.sample_rate)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        wave = wave * envelope
        
        # Convert to 16-bit integers
        wave = np.int16(wave * 32767)
        
        # Create stereo by duplicating the wave
        stereo = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo)
    
    def play_note(self, note=None, planet=None):
        """Play a note based on either note name or planet properties"""
        try:
            if note:
                # Play specific note
                frequency = self.note_frequencies.get(note, self.frequencies['medium'])
            elif planet:
                # Choose base frequency based on planet size
                if planet.size < 35:
                    base_freq = self.frequencies['small']
                elif planet.size < 50:
                    base_freq = self.frequencies['medium']
                else:
                    base_freq = self.frequencies['large']
                
                # Modify frequency based on planet color
                color_mod = sum(planet.base_color) / (255 * 3)  # Normalize color to 0-1
                frequency = base_freq * (0.8 + 0.4 * color_mod)  # Modify by ±20%
            else:
                frequency = self.frequencies['medium']
            
            # Generate and play the cosmic tone
            sound = self.generate_cosmic_tone(frequency)
            sound.set_volume(0.5)
            sound.play()
            
        except Exception as e:
            print(f"Error playing sound: {e}")
    
    def play_startup_sound(self):
        """Play a startup sound"""
        try:
            startup = self.generate_cosmic_tone(self.frequencies['medium'], duration=1.5)
            startup.set_volume(0.4)
            startup.play()
        except Exception as e:
            print(f"Error playing startup sound: {e}")
    
    def play_completion_melody(self):
        """Play a completion melody"""
        try:
            # Play a simple ascending pattern using notes
            melody_notes = ['C4', 'E4', 'G4', 'C5']
            for i, note in enumerate(melody_notes):
                pygame.time.delay(i * 200)  # Add delay between notes
                sound = self.generate_cosmic_tone(self.note_frequencies[note], duration=0.3)
                sound.set_volume(0.4)
                sound.play()
        except Exception as e:
            print(f"Error playing completion melody: {e}")