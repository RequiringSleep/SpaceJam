# sound_manager.py
import pygame
import numpy as np
from pygame import mixer
import time

class SoundManager:
    def __init__(self):
        pygame.mixer.init(44100, -16, 2, 1024)
        self.volume = 0.5
        self.sample_rate = 44100
        
        # Sound effect parameters
        self.fade_duration = 0.1
        self.active_sounds = {}
        
        # Generate UI sounds
        self.ui_sounds = {
            'select': self._generate_select_sound(),
            'start': self._generate_start_sound(),
            'stop': self._generate_stop_sound(),
            'transition': self._generate_transition_sound()
        }
        
        # Set initial volumes
        for sound in self.ui_sounds.values():
            sound.set_volume(self.volume)

    def _generate_select_sound(self):
        """Generate a soft selection sound"""
        duration = 0.15
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Create a pleasant bell-like tone
        freq1, freq2 = 440, 880
        wave = 0.3 * np.sin(2 * np.pi * freq1 * t) + 0.2 * np.sin(2 * np.pi * freq2 * t)
        
        # Apply smooth envelope
        envelope = np.exp(-8 * t)
        wave = wave * envelope
        
        return self._create_sound(wave)

    def _generate_start_sound(self):
        """Generate an upward sweep for start"""
        duration = 0.4
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Create ascending frequency sweep
        freq = np.linspace(300, 600, len(t))
        wave = 0.4 * np.sin(2 * np.pi * freq * t)
        
        # Add harmonics
        wave += 0.2 * np.sin(4 * np.pi * freq * t)
        
        # Apply envelope
        envelope = np.exp(-2 * t)
        wave = wave * envelope
        
        return self._create_sound(wave)

    def _generate_stop_sound(self):
        """Generate a downward sweep for stop"""
        duration = 0.4
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Create descending frequency sweep
        freq = np.linspace(600, 300, len(t))
        wave = 0.4 * np.sin(2 * np.pi * freq * t)
        
        # Add harmonics
        wave += 0.2 * np.sin(4 * np.pi * freq * t)
        
        # Apply envelope
        envelope = np.exp(-2 * t)
        wave = wave * envelope
        
        return self._create_sound(wave)

    def _generate_transition_sound(self):
        """Generate a smooth transition sound"""
        duration = 0.3
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Create smooth transition tone
        freq1, freq2 = 440, 660
        wave = 0.3 * np.sin(2 * np.pi * np.linspace(freq1, freq2, len(t)) * t)
        
        # Apply envelope
        envelope = np.sin(np.pi * t / duration)
        wave = wave * envelope
        
        return self._create_sound(wave)

    def _create_sound(self, wave):
        """Convert numpy array to pygame Sound object"""
        # Normalize to prevent clipping
        wave = wave / (np.max(np.abs(wave)) + 1e-6)
        # Convert to 16-bit integer
        wave = np.int16(wave * 32767)
        # Create stereo sound
        return pygame.sndarray.make_sound(np.column_stack((wave, wave)))

    def play_ui_sound(self, sound_type):
        """Play UI sound effect"""
        try:
            if sound_type in self.ui_sounds:
                self.ui_sounds[sound_type].stop()  # Stop if already playing
                self.ui_sounds[sound_type].set_volume(self.volume)
                self.ui_sounds[sound_type].play()
        except Exception as e:
            print(f"Error playing UI sound: {e}")

    def stop_all(self):
        """Stop all active sounds"""
        try:
            pygame.mixer.stop()
        except Exception as e:
            print(f"Error stopping sounds: {e}")

    def set_volume(self, value):
        """Set master volume"""
        try:
            self.volume = max(0.0, min(1.0, value))
            for sound in self.ui_sounds.values():
                sound.set_volume(self.volume)
        except Exception as e:
            print(f"Error setting volume: {e}")

    def cleanup(self):
        """Clean up resources"""
        try:
            self.stop_all()
            pygame.mixer.quit()
        except Exception as e:
            print(f"Error during cleanup: {e}")