import pygame
import numpy as np

class SoundManager:
    def __init__(self):
        """Initialize the sound system with child-friendly sounds"""
        pygame.mixer.init(frequency=44100, channels=2)
        self.notes = {
            'C': self._create_note(261.63),  # middle C
            'D': self._create_note(293.66),
            'E': self._create_note(329.63),
            'F': self._create_note(349.23),
            'G': self._create_note(392.00),
            'A': self._create_note(440.00),
            'B': self._create_note(493.88)
        }
        pygame.mixer.set_num_channels(8)

    def _create_note(self, frequency, duration=0.3):
        """Create a gentle, playful sound"""
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        t = np.linspace(0, duration, num_samples, False)
        
        # Create main wave with softer harmonics
        wave = (
            0.4 * np.sin(2 * np.pi * frequency * t) +  # Main tone
            0.1 * np.sin(4 * np.pi * frequency * t)    # Gentle overtone
        )
        
        # Create smooth envelope
        attack = int(0.1 * num_samples)
        decay = int(0.1 * num_samples)
        sustain = num_samples - attack - decay
        
        envelope = np.concatenate([
            np.linspace(0, 1, attack)**2,
            np.ones(sustain),
            np.linspace(1, 0, decay)**2
        ])
        
        # Ensure wave and envelope are the same length
        wave = wave[:len(envelope)]
        
        # Apply envelope and normalize
        wave = wave * envelope
        wave = wave / np.max(np.abs(wave))  # Normalize
        wave = (wave * 32767 * 0.3).astype(np.int16)  # Convert to 16-bit audio at reduced volume
        
        # Create stereo sound
        sound_buffer = np.zeros((len(wave), 2), dtype=np.int16)
        sound_buffer[:, 0] = wave
        sound_buffer[:, 1] = wave
        
        return pygame.sndarray.make_sound(sound_buffer)

    def play_startup_sound(self):
        """Play a playful, gentle startup sound"""
        duration = 1.0
        sample_rate = 44100
        num_samples = int(duration * sample_rate)
        t = np.linspace(0, duration, num_samples, False)
        
        # Create a gentler frequency sweep
        base_freq = np.linspace(200, 400, num_samples)
        
        # Create playful sound with gentle harmonics
        wave = (
            0.3 * np.sin(2 * np.pi * base_freq * t) +
            0.1 * np.sin(4 * np.pi * base_freq * t)
        )
        
        # Create smooth envelope
        attack = int(0.2 * num_samples)
        decay = int(0.2 * num_samples)
        sustain = num_samples - attack - decay
        
        envelope = np.concatenate([
            np.linspace(0, 1, attack)**2,
            np.ones(sustain),
            np.linspace(1, 0, decay)**2
        ])
        
        # Apply envelope and normalize
        wave = wave * envelope
        wave = wave / np.max(np.abs(wave))
        wave = (wave * 32767 * 0.3).astype(np.int16)
        
        # Create stereo sound
        sound_buffer = np.zeros((len(wave), 2), dtype=np.int16)
        sound_buffer[:, 0] = wave
        sound_buffer[:, 1] = wave
        
        sound = pygame.sndarray.make_sound(sound_buffer)
        sound.play()

    def play_note(self, note):
        """Play a gentle note"""
        if note in self.notes:
            self.notes[note].play()
            pygame.time.wait(50)

    def play_completion_melody(self):
        """Play a happy, child-friendly completion melody"""
        melody = ['C', 'E', 'G', 'C']
        for note in melody:
            if note in self.notes:
                self.notes[note].play()
                pygame.time.wait(200)