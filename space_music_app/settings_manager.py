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
        
        # Musical constants
        self.root_note = 220.0  # A3
        self.scale = self._generate_scale('minor')  # Scale frequencies
        self.bpm = 120
        self.beat_length = 60000 / self.bpm  # milliseconds per beat
        self.beat_count = 0
        self.last_beat_time = 0
        
        # Sound characteristics for each type
        self.sound_types = {
            'bass': {
                'base_freq': self.root_note / 2,  # One octave down
                'waveform': 'sine',
                'harmonics': [1.0, 0.5, 0.25, 0.125],
                'envelope': {
                    'attack': 0.1,
                    'decay': 0.2,
                    'sustain': 0.8,
                    'release': 0.3
                },
                'rhythm': [1, 0, 0.5, 0, 1, 0, 0.5, 0],  # Bass rhythm pattern
                'filter_freq': 500,
                'resonance': 2.0
            },
            'melody': {
                'base_freq': self.root_note * 2,  # One octave up
                'waveform': 'triangle',
                'harmonics': [1.0, 0.3, 0.15],
                'envelope': {
                    'attack': 0.05,
                    'decay': 0.1,
                    'sustain': 0.7,
                    'release': 0.2
                },
                'rhythm': [1, 0.5, 1, 0, 0.7, 0.5, 0, 0.7],
                'vibrato_rate': 5.0,
                'vibrato_depth': 0.03
            },
            'percussion': {
                'base_freq': None,  # Uses noise instead of pitched sound
                'noise_types': ['white', 'pink', 'metallic'],
                'envelope': {
                    'attack': 0.01,
                    'decay': 0.1,
                    'sustain': 0.0,
                    'release': 0.1
                },
                'rhythm': [1, 0.7, 1, 0.7, 1, 0.7, 1, 0.7],
                'filter_freq': 2000,
                'resonance': 1.5
            },
            'ambient': {
                'base_freq': self.root_note,
                'waveform': 'sine',
                'harmonics': [1.0, 0.4, 0.2],
                'envelope': {
                    'attack': 0.3,
                    'decay': 0.4,
                    'sustain': 0.8,
                    'release': 0.5
                },
                'mod_freq': 0.5,
                'mod_depth': 0.1,
                'reverb_time': 2.0
            }
        }

    def _generate_scale(self, scale_type):
        """Generate frequencies for a musical scale"""
        # Semitone ratios for different scales
        scales = {
            'major': [0, 2, 4, 5, 7, 9, 11],
            'minor': [0, 2, 3, 5, 7, 8, 10],
            'pentatonic': [0, 2, 4, 7, 9]
        }
        
        chosen_scale = scales.get(scale_type, scales['minor'])
        frequencies = []
        
        for octave in range(2):  # Generate 2 octaves
            for semitone in chosen_scale:
                freq = self.root_note * (2 ** (octave + semitone/12))
                frequencies.append(freq)
                
        return frequencies

    def _generate_noise(self, duration, noise_type='white'):
        """Generate different types of noise"""
        num_samples = int(self.sample_rate * duration)
        
        if noise_type == 'white':
            noise = np.random.normal(0, 1, num_samples)
        elif noise_type == 'pink':
            # Generate pink noise using 1/f spectrum
            f = np.fft.fftfreq(num_samples)
            f[0] = 1e-6  # Avoid division by zero
            spectrum = 1 / np.sqrt(np.abs(f))
            phase = np.random.uniform(0, 2*np.pi, num_samples)
            noise = np.fft.ifft(spectrum * np.exp(1j*phase)).real
        elif noise_type == 'metallic':
            # Create metallic sound using filtered noise with resonant peaks
            noise = np.random.normal(0, 1, num_samples)
            resonant_freqs = [1000, 2000, 3000, 4000]
            filtered_noise = np.zeros_like(noise)
            for freq in resonant_freqs:
                t = np.linspace(0, duration, num_samples)
                filtered_noise += noise * np.sin(2 * np.pi * freq * t)
            noise = filtered_noise
            
        return noise / np.max(np.abs(noise))

    def _apply_envelope(self, wave, sound_type):
        """Apply ADSR envelope to the wave"""
        env = self.sound_types[sound_type]['envelope']
        num_samples = len(wave)
        
        attack_samples = int(env['attack'] * self.sample_rate)
        decay_samples = int(env['decay'] * self.sample_rate)
        release_samples = int(env['release'] * self.sample_rate)
        
        envelope = np.ones(num_samples)
        
        # Attack
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
        # Decay
        decay_end = attack_samples + decay_samples
        envelope[attack_samples:decay_end] = np.linspace(1, env['sustain'], decay_samples)
        # Release
        release_start = num_samples - release_samples
        envelope[release_start:] = np.linspace(env['sustain'], 0, release_samples)
        
        return wave * envelope

    def generate_sound(self, sound_type, planet_color):
        """Generate a sound based on planet type and characteristics"""
        duration = 2.0  # Base duration for all sounds
        type_info = self.sound_types[sound_type]
        
        # Use planet color to influence sound parameters
        color_value = sum(planet_color) / (255 * 3)  # 0 to 1
        
        if sound_type == 'bass':
            # Generate rich bass tone with harmonics
            wave = np.zeros(int(self.sample_rate * duration))
            base_freq = type_info['base_freq'] * (0.9 + color_value * 0.2)
            
            for i, amplitude in enumerate(type_info['harmonics']):
                t = np.linspace(0, duration, int(self.sample_rate * duration))
                wave += amplitude * np.sin(2 * np.pi * base_freq * (i + 1) * t)
                
        elif sound_type == 'melody':
            # Generate melodic sound with vibrato
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            freq = type_info['base_freq'] * (1 + color_value * 0.5)
            vibrato = type_info['vibrato_depth'] * np.sin(2 * np.pi * type_info['vibrato_rate'] * t)
            wave = np.sin(2 * np.pi * freq * t + vibrato)
            
        elif sound_type == 'percussion':
            # Generate percussion sound with filtered noise
            wave = self._generate_noise(duration, random.choice(type_info['noise_types']))
            
        elif sound_type == 'ambient':
            # Generate ambient pad sound with frequency modulation
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            freq = type_info['base_freq'] * (0.8 + color_value * 0.4)
            mod = type_info['mod_depth'] * np.sin(2 * np.pi * type_info['mod_freq'] * t)
            wave = np.sin(2 * np.pi * freq * t + mod)
            
            # Add subtle chorus effect
            chorus = np.sin(2 * np.pi * (freq * 1.01) * t + mod)
            wave = 0.7 * wave + 0.3 * chorus
        
        # Apply envelope
        wave = self._apply_envelope(wave, sound_type)
        
        # Convert to 16-bit integers and create stereo sound
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        
        return pygame.sndarray.make_sound(stereo_wave)

    def play_planet_sound(self, planet):
        """Play or stop planet sound"""
        try:
            if planet in self.active_sounds:
                self.active_sounds[planet]['sound'].stop()
                del self.active_sounds[planet]
                planet.is_playing = False
            else:
                sound = self.generate_sound(planet.sound_type, planet.base_color)
                sound.set_volume(self.volume)
                sound.play(-1)  # Loop the sound
                
                self.active_sounds[planet] = {
                    'sound': sound,
                    'type': planet.sound_type
                }
                planet.is_playing = True
                
        except Exception as e:
            print(f"Error playing planet sound: {e}")

    def update(self):
        """Update playing sounds and handle beat synchronization"""
        current_time = pygame.time.get_ticks()
        
        # Check for beat
        if current_time - self.last_beat_time >= self.beat_length:
            self.last_beat_time = current_time
            self.beat_count = (self.beat_count + 1) % 8
            
            # Update volumes based on rhythm patterns
            for planet, sound_info in self.active_sounds.items():
                sound_type = sound_info['type']
                if 'rhythm' in self.sound_types[sound_type]:
                    rhythm = self.sound_types[sound_type]['rhythm']
                    volume = rhythm[self.beat_count] * self.volume
                    sound_info['sound'].set_volume(volume)

    def stop_all_sounds(self):
        """Stop all playing sounds"""
        for sound_info in self.active_sounds.values():
            sound_info['sound'].stop()
        self.active_sounds.clear()

    def set_volume(self, value):
        """Set master volume"""
        self.volume = max(0.0, min(1.0, value))
        for sound_info in self.active_sounds.values():
            sound_info['sound'].set_volume(self.volume)

    def play_startup_sound(self):
        """Play an engaging startup sound"""
        duration = 1.5
        t = np.linspace(0, duration, int(self.sample_rate * duration))
        
        # Create a rising arpeggio
        frequencies = [self.root_note * (2 ** (i/12)) for i in [0, 4, 7, 12]]
        wave = np.zeros_like(t)
        
        for i, freq in enumerate(frequencies):
            start = int((i/len(frequencies)) * len(t))
            wave[start:] += 0.5 * np.sin(2 * np.pi * freq * t[:-start])
        
        # Apply envelope
        envelope = np.exp(-3 * t/duration)
        wave = wave * envelope
        
        # Convert and play
        wave = np.int16(wave * 32767)
        stereo_wave = np.column_stack((wave, wave))
        sound = pygame.sndarray.make_sound(stereo_wave)
        sound.set_volume(self.volume)
        sound.play()

    def play_completion_melody(self):
        """Play a satisfying completion melody"""
        duration = 0.2
        melody_notes = [0, 4, 7, 12]  # Major chord arpeggio
        
        for i, semitones in enumerate(melody_notes):
            t = np.linspace(0, duration, int(self.sample_rate * duration))
            freq = self.root_note * (2 ** (semitones/12))
            
            # Generate a pleasant bell-like tone
            wave = np.sin(2 * np.pi * freq * t)
            wave += 0.3 * np.sin(2 * 2 * np.pi * freq * t)
            wave += 0.2 * np.sin(3 * 2 * np.pi * freq * t)
            
            # Apply envelope
            envelope = np.exp(-5 * t/duration)
            wave = wave * envelope
            
            # Convert and play
            wave = np.int16(wave * 32767)
            stereo_wave = np.column_stack((wave, wave))
            sound = pygame.sndarray.make_sound(stereo_wave)
            sound.set_volume(self.volume)
            pygame.time.delay(i * 200)  # Delay between notes
            sound.play()