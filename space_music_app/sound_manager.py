# sound_manager.py
import pygame
import numpy as np

class SoundManager:
    def __init__(self):
        """Initialize the cosmic sound system"""
        pygame.mixer.init(44100, -16, 2, 1024)
        self.sample_rate = 44100
        self.active_sounds = {}  # Track which planet sounds are currently playing
        self.volume = 0.5
        
        # Define different sound types for planets
        self.sound_types = {
            'melody': {
                'base_freq': 261.63,  # C4
                'waveform': 'sine',
                'harmonics': [1.0, 0.5, 0.3],
                'rhythm': [1, 0, 1, 0, 1, 0, 1, 0],
                'duration': 0.5
            },
            'bass': {
                'base_freq': 65.41,  # C2
                'waveform': 'sine',
                'harmonics': [1.0, 0.7, 0.3],
                'rhythm': [1, 0, 0, 1, 1, 0, 0, 1],
                'duration': 1.0
            },
            'ambient': {
                'base_freq': 174.61,  # F3
                'waveform': 'sine',
                'mod_freq': 5.0,
                'mod_depth': 3.0,
                'duration': 2.0
            },
            'percussion': {
                'base_freq': 100.0,
                'waveform': 'noise',
                'decay': 10.0,
                'rhythm': [1, 1, 0, 1, 0, 1, 1, 0],
                'duration': 0.2
            }
        }
        
        # Beat timing
        self.beat_interval = 250  # milliseconds (240 BPM)
        self.last_beat_time = pygame.time.get_ticks()

    def get_sound_type(self, planet):
        """Determine sound type based on planet properties"""
        if planet.size < 35:
            return 'melody'
        elif planet.size < 50:
            return 'percussion'
        elif planet.size < 70:
            return 'bass'
        else:
            return 'ambient'

    def generate_waveform(self, sound_type, base_freq, duration):
        """Generate a waveform based on sound type"""
        t = np.linspace(0, duration, int(self.sample_rate * duration), False)
        wave = np.zeros_like(t)
        
        if sound_type == 'melody':
            # Melodic sound with harmonics
            for i, amp in enumerate(self.sound_types['melody']['harmonics']):
                wave += amp * np.sin(2 * np.pi * base_freq * (i + 1) * t)
            # Add slight pitch modulation
            wave *= (1 + 0.1 * np.sin(2 * np.pi * 3 * t))
            
        elif sound_type == 'bass':
            # Rich bass sound
            for i, amp in enumerate(self.sound_types['bass']['harmonics']):
                wave += amp * np.sin(2 * np.pi * base_freq * (i + 1) * t)
            # Add subtle overdrive
            wave = np.clip(wave * 1.2, -1, 1)
            
        elif sound_type == 'ambient':
            # Ambient pad sound with frequency modulation
            mod = self.sound_types['ambient']['mod_depth'] * \
                  np.sin(2 * np.pi * self.sound_types['ambient']['mod_freq'] * t)
            wave = np.sin(2 * np.pi * base_freq * t + mod)
            # Add slow amplitude modulation
            wave *= (1 + 0.3 * np.sin(2 * np.pi * 0.5 * t))
            
        elif sound_type == 'percussion':
            # Percussion with noise mix
            noise = np.random.normal(0, 1, len(t))
            sine = np.sin(2 * np.pi * base_freq * t)
            wave = 0.7 * sine + 0.3 * noise
            wave *= np.exp(-self.sound_types['percussion']['decay'] * t)

        # Apply envelope
        attack = int(0.1 * self.sample_rate)
        release = int(0.2 * self.sample_rate)
        
        envelope = np.ones_like(t)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-release:] = np.linspace(1, 0, release)
        
        wave = wave * envelope * self.volume
        
        # Convert to 16-bit integers
        wave = np.int16(wave * 32767)
        return pygame.sndarray.make_sound(np.column_stack((wave, wave)))

    def play_planet_sound(self, planet):
        """Toggle planet sound on/off"""
        try:
            if planet in self.active_sounds:
                # Stop the sound if it's already playing
                self.active_sounds[planet].stop()
                del self.active_sounds[planet]
                planet.is_playing = False
            else:
                # Generate and play new sound
                sound_type = self.get_sound_type(planet)
                base_freq = self.sound_types[sound_type]['base_freq']
                
                # Modify frequency based on planet color
                color_mod = sum(planet.base_color) / (255 * 3)  # 0 to 1
                freq = base_freq * (0.8 + 0.4 * color_mod)  # ±20% variation
                
                duration = self.sound_types[sound_type]['duration']
                sound = self.generate_waveform(sound_type, freq, duration)
                sound.set_volume(self.volume)
                sound.play(-1)  # Loop the sound
                
                self.active_sounds[planet] = sound
                planet.is_playing = True
                
        except Exception as e:
            print(f"Error playing planet sound: {e}")

    def update(self):
        """Update playing sounds and rhythms"""
        current_time = pygame.time.get_ticks()
        
        # Update rhythms on beat
        if current_time - self.last_beat_time >= self.beat_interval:
            self.last_beat_time = current_time
            beat_index = (current_time // self.beat_interval) % 8
            
            for planet, sound in self.active_sounds.items():
                sound_type = self.get_sound_type(planet)
                
                # Apply rhythm pattern if sound type has one
                if 'rhythm' in self.sound_types[sound_type]:
                    rhythm = self.sound_types[sound_type]['rhythm']
                    if rhythm[beat_index]:
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
        duration = 1.5
        sound = self.generate_waveform('ambient', 
            self.sound_types['ambient']['base_freq'], duration)
        sound.set_volume(self.volume)
        sound.play()

    def play_completion_melody(self):
        """Play a completion melody"""
        base_freq = self.sound_types['melody']['base_freq']
        intervals = [0, 4, 7, 12]  # Major chord arpeggio
        
        for i, interval in enumerate(intervals):
            freq = base_freq * (2 ** (interval/12))
            sound = self.generate_waveform('melody', freq, 0.3)
            sound.set_volume(self.volume)
            pygame.time.delay(i * 200)  # 200ms between notes
            sound.play()