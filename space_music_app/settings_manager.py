import pygame
import numpy as np
from collections import defaultdict

class SoundManager:
    def __init__(self):
        """Initialize the cosmic sound system"""
        pygame.mixer.init(44100, -16, 2, 1024)
        self.sample_rate = 44100
        self.active_sounds = {}  # Track which planet sounds are currently playing
        self.volume = 0.5
        
        # Define different instrument types with unique characteristics
        self.instruments = {
            'bass': {
                'base_freq': 65.41,  # C2
                'waveform': 'sine',
                'harmonics': [1.0, 0.5, 0.25],  # Fundamental + overtones
                'envelope': {'attack': 0.1, 'decay': 0.2, 'sustain': 0.7, 'release': 0.3},
                'rhythm': [1, 0, 0, 1, 0, 0, 1, 0]  # Basic rhythm pattern
            },
            'pad': {
                'base_freq': 261.63,  # C4
                'waveform': 'sine',
                'mod_freq': 5.0,  # Modulation frequency
                'mod_depth': 3.0,
                'envelope': {'attack': 0.3, 'decay': 0.4, 'sustain': 0.8, 'release': 0.5}
            },
            'pluck': {
                'base_freq': 523.25,  # C5
                'waveform': 'triangle',
                'decay_factor': 8.0,
                'envelope': {'attack': 0.05, 'decay': 0.1, 'sustain': 0.3, 'release': 0.1},
                'rhythm': [1, 1, 0, 1, 1, 0, 1, 0]
            },
            'percussion': {
                'base_freq': 100.0,
                'noise_mix': 0.3,
                'decay_factor': 10.0,
                'envelope': {'attack': 0.01, 'decay': 0.1, 'sustain': 0.0, 'release': 0.1},
                'rhythm': [1, 0, 1, 0, 1, 0, 1, 0]
            }
        }
        
        # Map planet characteristics to instruments
        self.planet_types = {
            'small': {  # Small rocky planets
                'instrument': 'pluck',
                'size_range': (20, 35),
                'scale': [0, 4, 7, 12]  # Major chord arpeggio
            },
            'medium': {  # Earth-like planets
                'instrument': 'pad',
                'size_range': (35, 50),
                'scale': [0, 3, 7]  # Minor chord
            },
            'large': {  # Gas giants
                'instrument': 'bass',
                'size_range': (50, 70),
                'scale': [0, 5, 7]  # Power chord
            },
            'massive': {  # Super giants
                'instrument': 'percussion',
                'size_range': (70, 100),
                'rhythm_emphasis': True
            }
        }

    def get_planet_type(self, planet):
        """Determine planet type based on size and properties"""
        for ptype, props in self.planet_types.items():
            size_range = props['size_range']
            if size_range[0] <= planet.size < size_range[1]:
                return ptype
        return 'medium'  # Default type

    def generate_waveform(self, instrument_type, frequency, duration):
        """Generate waveform based on instrument type"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.zeros_like(t)
        instrument = self.instruments[instrument_type]
        
        if instrument_type == 'bass':
            # Generate rich bass tone with harmonics
            for i, amplitude in enumerate(instrument['harmonics']):
                wave += amplitude * np.sin(2 * np.pi * frequency * (i + 1) * t)
        
        elif instrument_type == 'pad':
            # Generate pad sound with frequency modulation
            mod = instrument['mod_depth'] * np.sin(2 * np.pi * instrument['mod_freq'] * t)
            wave = np.sin(2 * np.pi * frequency * t + mod)
        
        elif instrument_type == 'pluck':
            # Generate pluck sound with quick decay
            wave = np.sin(2 * np.pi * frequency * t)
            wave *= np.exp(-instrument['decay_factor'] * t)
        
        elif instrument_type == 'percussion':
            # Generate percussion with noise mix
            sine = np.sin(2 * np.pi * frequency * t)
            noise = np.random.normal(0, 1, len(t))
            wave = (1 - instrument['noise_mix']) * sine + instrument['noise_mix'] * noise
            wave *= np.exp(-instrument['decay_factor'] * t)
        
        # Apply envelope
        env = instrument['envelope']
        envelope = np.ones_like(t)
        attack = int(env['attack'] * self.sample_rate)
        decay = int(env['decay'] * self.sample_rate)
        release = int(env['release'] * self.sample_rate)
        
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[attack:attack + decay] = np.linspace(1, env['sustain'], decay)
        envelope[-release:] = np.linspace(env['sustain'], 0, release)
        
        wave = wave * envelope * self.volume
        
        # Convert to 16-bit integers
        wave = np.int16(wave * 32767)
        return pygame.sndarray.make_sound(np.column_stack((wave, wave)))

    def play_planet_sound(self, planet):
        """Toggle planet sound on/off"""
        try:
            planet_type = self.get_planet_type(planet)
            instrument_type = self.planet_types[planet_type]['instrument']
            
            if planet in self.active_sounds:
                # Stop the sound if it's already playing
                self.active_sounds[planet].stop()
                del self.active_sounds[planet]
                planet.is_playing = False
            else:
                # Generate and play the sound
                base_freq = self.instruments[instrument_type]['base_freq']
                # Modify frequency based on planet color
                color_mod = sum(planet.base_color) / (255 * 3)
                frequency = base_freq * (0.8 + 0.4 * color_mod)
                
                sound = self.generate_waveform(instrument_type, frequency, 2.0)
                sound.set_volume(self.volume)
                sound.play(-1)  # Loop the sound
                self.active_sounds[planet] = sound
                planet.is_playing = True
                
        except Exception as e:
            print(f"Error playing planet sound: {e}")

    def update_rhythms(self):
        """Update rhythm patterns for active sounds"""
        current_tick = (pygame.time.get_ticks() // 250) % 8  # 250ms per beat
        
        for planet, sound in self.active_sounds.items():
            planet_type = self.get_planet_type(planet)
            instrument_type = self.planet_types[planet_type]['instrument']
            
            if 'rhythm' in self.instruments[instrument_type]:
                rhythm = self.instruments[instrument_type]['rhythm']
                if rhythm[current_tick]:
                    sound.set_volume(self.volume)
                else:
                    sound.set_volume(0)

    def stop_all_sounds(self):
        """Stop all playing sounds"""
        for sound in self.active_sounds.values():
            sound.stop()
        self.active_sounds.clear()

    def set_volume(self, value):
        """Set master volume"""
        self.volume = max(0.0, min(1.0, value))
        for sound in self.active_sounds.values():
            sound.set_volume(self.volume)

    def play_startup_sound(self):
        """Play a startup sound"""
        pad_sound = self.generate_waveform('pad', 
            self.instruments['pad']['base_freq'], 1.5)
        pad_sound.set_volume(self.volume)
        pad_sound.play()

    def play_completion_melody(self):
        """Play a completion melody"""
        base_freq = self.instruments['pluck']['base_freq']
        intervals = [0, 4, 7, 12]  # Major scale intervals
        for i, interval in enumerate(intervals):
            freq = base_freq * (2 ** (interval/12))
            sound = self.generate_waveform('pluck', freq, 0.3)
            sound.set_volume(self.volume)
            pygame.time.delay(i * 200)
            sound.play()