import numpy as np
import sounddevice as sd
import threading
import time
from collections import deque

class AudioProcessor:
    def __init__(self):
        devices = sd.query_devices()
        self.device_id = None
        for i, dev in enumerate(devices):
            if dev['max_input_channels'] > 0:
                self.device_id = i
                break
        
        if self.device_id is None:
            raise ValueError("No input device found")
        
        self.CHUNK = 1024
        self.RATE = 44100
        self.CHANNELS = 1
        
        self.volume = 0
        self.is_active = False
        self.intensity = 0
        self.peaks = []
        self.volume_history = deque(maxlen=10)
        
        self.peak_threshold = 1.2
        self.min_peak_interval = 0.05
        self.last_peak_time = 0
        
        self.lock = threading.Lock()
        self.running = False

    def audio_callback(self, indata, frames, time_info, status):
        if status:
            return
            
        volume_norm = np.sqrt(np.mean(indata**2))
        current_time = time.time()
        
        with self.lock:
            self.volume = float(volume_norm)
            self.volume_history.append(volume_norm)
            avg_volume = np.mean(list(self.volume_history))
            
            self.is_active = volume_norm > 0.01
            self.intensity = min(1.0, volume_norm / 0.1)
            
            if (volume_norm > avg_volume * self.peak_threshold and 
                current_time - self.last_peak_time > self.min_peak_interval):
                self.peaks.append(current_time)
                self.last_peak_time = current_time
            
            # Clean old peaks
            self.peaks = [t for t in self.peaks if current_time - t < 1.0]

    def start(self):
        self.running = True
        self.stream = sd.InputStream(
            device=self.device_id,
            channels=self.CHANNELS,
            samplerate=self.RATE,
            blocksize=self.CHUNK,
            dtype=np.float32,
            callback=self.audio_callback
        )
        self.stream.start()

    def stop(self):
        self.running = False
        if hasattr(self, 'stream'):
            self.stream.stop()
            self.stream.close()

    def get_analysis(self):
        with self.lock:
            return {
                'volume': self.volume,
                'is_active': self.is_active,
                'intensity': self.intensity,
                'peak_count': len(self.peaks),
                'has_recent_peak': bool(self.peaks and time.time() - self.peaks[-1] < 0.1)
            }