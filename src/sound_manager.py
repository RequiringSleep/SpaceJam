from typing import Self
import pygame
import numpy as np
from pygame import mixer

class SoundManager:
    def __init__(self):
        pygame.mixer.init(44100, -16, 2, 1024)
        self.volume = 0.5
        self.sample_rate = 44100
        self.ui_sounds = {
            'select': self._generate_select_sound(),
            'start': self._generate_start_sound(),
            'stop': self._generate_stop_sound(),
            'transition': self._generate_transition_sound()
        }
        for sound in self.ui_sounds.values():
            sound.set_volume(self.volume)

    def _generate_select_sound(self):
        duration = 0.3
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)
        freq1, freq2 = 523, 784  # C5, G5
        wave = 0.3 * np.sin(2 * np.pi * freq1 * t) + 0.2 * np.sin(2 * np.pi * freq2 * t)
        envelope = np.sin(np.pi * t / duration) * np.exp(-2 * t)
        return self._create_sound(wave * envelope)

    def _generate_start_sound(self):
        duration = 0.6
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)
        freq = np.linspace(392, 587, samples)  # G4 to D5
        wave = 0.4 * np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(4 * np.pi * freq * t)
        envelope = np.sin(np.pi * t / duration)
        return self._create_sound(wave * envelope)

    def _generate_stop_sound(self):
        duration = 0.6
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)
        freq = np.linspace(587, 392, samples)  # D5 to G4
        wave = 0.4 * np.sin(2 * np.pi * freq * t) + 0.2 * np.sin(4 * np.pi * freq * t)
        envelope = np.sin(np.pi * t / duration)
        return self._create_sound(wave * envelope)

    def _generate_transition_sound(self):
        duration = 0.4
        samples = int(self.sample_rate * duration)
        t = np.linspace(0, duration, samples)
        freq1, freq2 = 523, 698  # C5, F5
        wave = 0.3 * np.sin(2 * np.pi * np.linspace(freq1, freq2, samples) * t)
        envelope = np.sin(np.pi * t / duration) ** 2
        return self._create_sound(wave * envelope)

    def _create_sound(self, wave):
        normalized = wave / (np.max(np.abs(wave)) + 1e-6)
        samples = np.int16(normalized * 32767)
        
        stereo = np.empty((len(samples), 2), dtype=np.int16)
        stereo[:, 0] = samples
        stereo[:, 1] = samples
        
        try:
            return pygame.mixer.Sound(buffer=stereo)
        except Exception as e:
            print(f"Sound creation error: {e}")
            return pygame.mixer.Sound(buffer=np.zeros((1000, 2), dtype=np.int16))

    def play_ui_sound(self, sound_type):
        if sound_type in self.ui_sounds:
            self.ui_sounds[sound_type].stop()
            self.ui_sounds[sound_type].set_volume(self.volume)
            self.ui_sounds[sound_type].play()

    def stop_all(self):
        pygame.mixer.stop()

    def set_volume(self, value):
        self.volume = max(0.0, min(1.0, value))
        for sound in self.ui_sounds.values():
            sound.set_volume(self.volume)

    def cleanup(self):
        self.stop_all()
        pygame.mixer.quit()